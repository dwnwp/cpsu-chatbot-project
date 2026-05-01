package services

import (
	"context"
	"fmt"
	"log"
	"os"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/ledongthuc/pdf"
	"github.com/pkoukk/tiktoken-go"
	"github.com/qdrant/go-client/qdrant"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/textsplitter"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
)

type DocumentService struct {
	embedder     embeddings.Embedder
	llm          llms.Model
	qdrantClient *qdrant.Client
}

func NewDocumentService(embedder embeddings.Embedder, llm llms.Model, qdrantClient *qdrant.Client) *DocumentService {
	return &DocumentService{embedder: embedder, llm: llm, qdrantClient: qdrantClient}
}

func tokenLen(text string) int {
	tkm, _ := tiktoken.GetEncoding("cl100k_base")
	token := tkm.Encode(text, nil, nil)
	return len(token)
}

func splitFAQ(content string) []string {
	content = strings.ReplaceAll(content, "\r\n", "\n")
	re := regexp.MustCompile(`\n\s*\n+`)
	rawChunks := re.Split(content, -1)
	var chunks []string
	for _, chunk := range rawChunks {
		trimmed := strings.TrimSpace(chunk)
		if trimmed != "" {
			chunks = append(chunks, trimmed)
		}
	}
	return chunks
}

func (s *DocumentService) IngestDocument(
	ctx context.Context,
	filePath, filename,
	indexName string,
	chunkSize, chunkOverlap int,
	customMeta map[string]interface{},
	separateNewline bool) (int, error) {

	// 1. Load File Content (PDF/Text)
	var content string
	if strings.HasSuffix(strings.ToLower(filename), ".pdf") {
		f, r, err := pdf.Open(filePath)
		if err != nil {
			return 0, fmt.Errorf("open pdf error: %w", err)
		}
		defer f.Close()
		var buf strings.Builder
		for i := 1; i <= r.NumPage(); i++ {
			p := r.Page(i)
			if p.V.IsNull() {
				continue
			}
			text, _ := p.GetPlainText(nil)
			buf.WriteString(text)
		}
		content = buf.String()
	} else {
		b, err := os.ReadFile(filePath)
		if err != nil {
			return 0, err
		}
		content = string(b)
	}

	// 2. Text Splitting
	var chunks []string
	var err error

	if separateNewline {
		fmt.Println("Using Paragraph Splitting Mode (\\n\\n)")
		chunks = splitFAQ(content)

	} else {
		content = strings.ReplaceAll(content, "\n", " ")

		splitter := textsplitter.NewRecursiveCharacter()
		splitter.ChunkSize = chunkSize
		splitter.ChunkOverlap = chunkOverlap
		splitter.LenFunc = tokenLen

		chunks, err = splitter.SplitText(content)
		if err != nil {
			return 0, err
		}
	}

	// 3. Ensure Qdrant Collection Exists
	exists, err := s.qdrantClient.CollectionExists(ctx, indexName)
	if err != nil {
		return 0, fmt.Errorf("fail to check collection: %w", err)
	}

	if !exists {
		err = s.qdrantClient.CreateCollection(ctx, &qdrant.CreateCollection{
			CollectionName: indexName,
			VectorsConfig: qdrant.NewVectorsConfig(&qdrant.VectorParams{
				Size:     uint64(environment.GetVectorDimension()),
				Distance: qdrant.Distance_Cosine,
			}),
		})
		if err != nil {
			return 0, fmt.Errorf("fail to create collection: %w", err)
		}
	}

	// 4. Batch Processing
	batchSize := 50
	totalChunks := len(chunks)

	for i := 0; i < totalChunks; i += batchSize {
		end := i + batchSize
		if end > totalChunks {
			end = totalChunks
		}
		batch := chunks[i:end]

		// 4.1 Create Embeddings using Universal Embedder
		batchClean := make([]string, len(batch))
		for k, v := range batch {
			batchClean[k] = strings.ReplaceAll(v, "\n", " ")
		}

		vectors, err := s.embedder.EmbedDocuments(ctx, batchClean)
		if err != nil {
			return 0, fmt.Errorf("embedding error: %w", err)
		}

		// 4.2 Prepare Points
		var points []*qdrant.PointStruct

		for j, vec32 := range vectors {

			metaMap := map[string]any{
				"source":      filename,
				"text":        batch[j],
				"uploaded_at": time.Now().Format(time.RFC3339),
				"chunk_index": i + j,
			}
			for k, v := range customMeta {
				metaMap[k] = v
			}

			pointIdStr := fmt.Sprintf("%s_%d", filename, i+j)
			pointUuid := uuid.NewMD5(uuid.NameSpaceURL, []byte(pointIdStr)).String()

			points = append(points, &qdrant.PointStruct{
				Id:      qdrant.NewID(pointUuid),
				Vectors: qdrant.NewVectors(vec32...),
				Payload: qdrant.NewValueMap(metaMap),
			})
		}

		// Upsert Points
		_, err = s.qdrantClient.Upsert(ctx, &qdrant.UpsertPoints{
			CollectionName: indexName,
			Points:         points,
		})
		if err != nil {
			return 0, fmt.Errorf("upsert error: %w", err)
		}
	}

	return totalChunks, nil
}

func (s *DocumentService) DeleteDocument(ctx context.Context, filename, indexName string) error {
	_, err := s.qdrantClient.Delete(ctx, &qdrant.DeletePoints{
		CollectionName: indexName,
		Points: &qdrant.PointsSelector{
			PointsSelectorOneOf: &qdrant.PointsSelector_Filter{
				Filter: &qdrant.Filter{
					Must: []*qdrant.Condition{
						qdrant.NewMatch("source", filename),
					},
				},
			},
		},
	})
	if err != nil {
		return fmt.Errorf("failed to delete points: %w", err)
	}

	return nil
}

func (s *DocumentService) GetFileSources(ctx context.Context, indexName string, isAllIndex bool) ([]model.DocumentSource, error) {
	var targetCollections []string

	// 1. Check if all indices or specific index
	if isAllIndex {
		collections, err := s.qdrantClient.ListCollections(ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to list collections: %w", err)
		}
		for _, col := range collections {
			targetCollections = append(targetCollections, col)
		}
	} else {
		targetCollections = append(targetCollections, indexName)
	}

	uniqueSourcesMap := make(map[string]string)

	for _, collection := range targetCollections {
		
		var offset *qdrant.PointId
		limit := uint32(100)

		for {
			scrollRes, err := s.qdrantClient.Scroll(ctx, &qdrant.ScrollPoints{
				CollectionName: collection,
				Limit:          &limit,
				Offset:         offset,
				WithPayload:    qdrant.NewWithPayload(true),
			})
			if err != nil {
				return nil, fmt.Errorf("scroll error on collection %s: %w", collection, err)
			}

			// Parse Payload
			for _, point := range scrollRes {
				if point.Payload != nil {
					payload := point.Payload
					
					sourceVal, sourceExists := payload["source"]
					if sourceExists && sourceVal.GetStringValue() != "" {
						sourceStr := sourceVal.GetStringValue()
						uploadedAtStr := ""
						
						uaVal, uaExists := payload["uploaded_at"]
						if uaExists {
							uploadedAtStr = uaVal.GetStringValue()
						}

						if existingUa, hasExisting := uniqueSourcesMap[sourceStr]; hasExisting {
							if uploadedAtStr != "" && (existingUa == "" || uploadedAtStr < existingUa) {
								uniqueSourcesMap[sourceStr] = uploadedAtStr
							}
						} else {
							uniqueSourcesMap[sourceStr] = uploadedAtStr
						}
					}
				}
				offset = point.Id
			}

			if len(scrollRes) < int(limit) {
				break
			}
		}
	}

	var uniqueSources []model.DocumentSource
	for source, uploadedAt := range uniqueSourcesMap {
		uniqueSources = append(uniqueSources, model.DocumentSource{
			Name:       source,
			UploadedAt: uploadedAt,
		})
	}

	return uniqueSources, nil
}

func (s *DocumentService) RetrieveMultiQuery(
	ctx context.Context,
	query, indexName string,
	filter map[string]interface{},
	topK int) ([]string, error) {

	// 1. Generate & Embed Queries (เหมือนเดิม)
	generatedQueries := s.generateMultiQueries(ctx, query)
	generatedQueries = append(generatedQueries, query)

	inputs := make([]string, len(generatedQueries))
	for i, q := range generatedQueries {
		inputs[i] = strings.ReplaceAll(q, "\n", " ")
	}

	log.Println("Generated Query: ", inputs)
	vectors, err := s.embedder.EmbedDocuments(ctx, inputs)
	if err != nil {
		return nil, fmt.Errorf("embed error: %w", err)
	}

	// 2. Parallel Search
	var wg sync.WaitGroup
	type SearchResult struct {
		Matches []*qdrant.ScoredPoint
		Err     error
	}
	resultsChan := make(chan SearchResult, len(vectors))

	var metadataFilter *qdrant.Filter
	if filter != nil {
		conditions := []*qdrant.Condition{}
		for k, v := range filter {
			if strVal, ok := v.(string); ok {
				conditions = append(conditions, qdrant.NewMatch(k, strVal))
			}
		}
		if len(conditions) > 0 {
			metadataFilter = &qdrant.Filter{
				Must: conditions,
			}
		}
	}

	for _, vec32 := range vectors {
		wg.Add(1)
		go func(vec []float32) {
			defer wg.Done()

			res, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
				CollectionName: indexName,
				Query:          qdrant.NewQuery(vec...),
				Limit:          qdrant.PtrOf(uint64(topK)),
				Filter:         metadataFilter,
				WithPayload:    qdrant.NewWithPayload(true),
			})

			if err == nil {
				resultsChan <- SearchResult{Matches: res, Err: nil}
			} else {
				resultsChan <- SearchResult{Matches: nil, Err: err}
			}
		}(vec32)
	}

	wg.Wait()
	close(resultsChan)

	// 3. Deduplicate & Extract
	uniqueMatches := make(map[string]*qdrant.ScoredPoint)
	for res := range resultsChan {
		if res.Err != nil {
			continue
		}

		for _, match := range res.Matches {
			if match == nil || match.Id == nil {
				continue
			}

			// ID should be a string in our setup
			var id string
			if numId := match.Id.GetNum(); numId > 0 {
				id = strconv.FormatUint(numId, 10)
			} else if strId := match.Id.GetUuid(); strId != "" {
				id = strId
			}

			if existing, ok := uniqueMatches[id]; !ok || match.Score > existing.Score {
				uniqueMatches[id] = match
			}
		}
	}

	var sortedMatches []*qdrant.ScoredPoint
	for _, v := range uniqueMatches {
		sortedMatches = append(sortedMatches, v)
	}
	sort.Slice(sortedMatches, func(i, j int) bool {
		return sortedMatches[i].Score > sortedMatches[j].Score
	})

	// 4. Extract Text from Payload
	finalResults := []string{}
	limit := topK
	if len(sortedMatches) < limit {
		limit = len(sortedMatches)
	}

	for i := 0; i < limit; i++ {
		match := sortedMatches[i]
		if match.Payload != nil {
			if txtVal, ok := match.Payload["text"]; ok {
				finalResults = append(finalResults, txtVal.GetStringValue())
			}
		}
	}

	return finalResults, nil
}

func (s *DocumentService) generateMultiQueries(ctx context.Context, originalQuery string) []string {
	systemPrompt := `You are an AI language model assistant. Your task is to generate 1 - 5 different sub questions OR alternate versions of the given user question to retrieve relevant documents from a vector database.

By generating multiple versions of the user question,
your goal is to help the user overcome some of the limitations
of distance-based similarity search.

By generating sub questions, you can break down questions that refer to multiple concepts into distinct questions. This will help you get the relevant documents for constructing a final answer

If multiple concepts are present in the question, you should break into sub questions, with one question for each concept

### Restrictions:
- Do NOT explain anything
- Do NOT add numbering, bullets, or quotation marks
- Do NOT repeat identical phrasing
- Output Thai language ONLY

### Output:
Return only the Thai search queries, one per line.`

	contentItems := []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeSystem, systemPrompt),
		llms.TextParts(llms.ChatMessageTypeHuman, originalQuery),
	}

	resp, err := s.llm.GenerateContent(ctx, contentItems, llms.WithTemperature(0.7))
	if err != nil || len(resp.Choices) == 0 {
		return []string{}
	}

	content := resp.Choices[0].Content
	lines := strings.Split(content, "\n")
	var queries []string
	for _, l := range lines {
		trimmed := strings.TrimSpace(l)
		if trimmed != "" {
			queries = append(queries, trimmed)
		}
	}
	return queries
}

func (s *DocumentService) GetDocumentChunks(ctx context.Context, indexName string, sourceName string) ([]model.DocumentChunk, error) {
	// 1. Describe Index - Check Collection Exists & Connect
	exists, err := s.qdrantClient.CollectionExists(ctx, indexName)
	if err != nil {
		return nil, fmt.Errorf("failed to describe collection '%s': %w", indexName, err)
	}
	if !exists {
		return nil, fmt.Errorf("collection '%s' does not exist", indexName)
	}

	// 2. Create Search Filter (filter specific document source)
	filter := &qdrant.Filter{
		Must: []*qdrant.Condition{
			qdrant.NewMatch("source", sourceName),
		},
	}

	// 3. สร้าง Dummy Vector ป้องกัน Error Cosine Similarity
	vectorDimension := environment.GetVectorDimension()
	dummyVector := make([]float32, vectorDimension)
	dummyVector[0] = 1.0 // ใส่ค่า 1.0 ในตำแหน่งแรก เพื่อไม่ให้ Vector เป็น 0 ทั้งหมด

	// 4. Send Search Request for Document Chunks using Limit parameter instead of TopK
	limit := uint64(10000)
	queryRes, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
		CollectionName: indexName,
		Query:          qdrant.NewQuery(dummyVector...),
		Filter:         filter,
		Limit:          &limit,
		WithPayload:    qdrant.NewWithPayload(true),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to query by vector values: %w", err)
	}

	// 5. Build Result array
	type ChunkWithIndex struct {
		Chunk model.DocumentChunk
		Index int
	}
	var chunksWithIdx []ChunkWithIndex

	for _, match := range queryRes {
		if match.Payload != nil {
			meta := match.Payload

			textStr := ""
			if t, ok := meta["text"]; ok {
				textStr = t.GetStringValue()
			}

			chunkIdx := 0
			if idx, ok := meta["chunk_index"]; ok {
				chunkIdx = int(idx.GetIntegerValue())
			}

			// ID should be a string
			var id string
			if numId := match.Id.GetNum(); numId > 0 {
				id = strconv.FormatUint(numId, 10)
			} else if strId := match.Id.GetUuid(); strId != "" {
				id = strId
			}

			chunksWithIdx = append(chunksWithIdx, ChunkWithIndex{
				Chunk: model.DocumentChunk{
					ID:   id,
					Text: textStr,
				},
				Index: chunkIdx,
			})
		}
	}

	// 6. เรียงลำดับ Chunk ตาม chunk_index เพื่อให้ประกอบร่างเป็น Text ที่อ่านรู้เรื่อง
	sort.Slice(chunksWithIdx, func(i, j int) bool {
		return chunksWithIdx[i].Index < chunksWithIdx[j].Index
	})

	var chunks []model.DocumentChunk
	for _, c := range chunksWithIdx {
		chunks = append(chunks, c.Chunk)
	}

	return chunks, nil
}


