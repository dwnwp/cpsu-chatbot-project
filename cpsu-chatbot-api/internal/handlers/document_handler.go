package handler

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/services"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
)

type DocumentHandler struct {
	DocumentService services.DocumentService
	RedisClient     *redis.Client
}

func NewDocumentHandler(dcService services.DocumentService, redisClient *redis.Client) *DocumentHandler {
	return &DocumentHandler{
		DocumentService: dcService,
		RedisClient:     redisClient,
	}
}

func (h *DocumentHandler) Ingest(c echo.Context) error {
	// 1. รับค่า Form Data
	chunkSizeStr := c.FormValue("chunk_size")
	chunkOverlapStr := c.FormValue("chunk_overlap")
	indexName := c.FormValue("index_name")
	rawMetadata := c.FormValue("metadata")
	separateNewline := c.FormValue("separate_newline") == "true"

	// 2. Validate Required Fields
	if chunkSizeStr == "" || chunkOverlapStr == "" || indexName == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Missing required parameters: 'chunk_size', 'chunk_overlap', and 'index_name' are required."})
	}

	// 3. Convert Types (String -> Int)
	chunkSize, err := strconv.Atoi(chunkSizeStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "chunk_size must be an integer"})
	}
	chunkOverlap, err := strconv.Atoi(chunkOverlapStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "chunk_overlap must be an integer"})
	}

	// 4. Parse Metadata JSON (ถ้ามี)
	var customMeta map[string]interface{}
	if rawMetadata != "" {
		if err := json.Unmarshal([]byte(rawMetadata), &customMeta); err != nil {
			return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Invalid JSON format in metadata"})
		}
	}

	// 5. Handle File Upload
	fileHeader, err := c.FormFile("file")
	if err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "No file part or no selected file"})
	}

	// Validate File Extension (.pdf, .txt)
	ext := strings.ToLower(filepath.Ext(fileHeader.Filename))
	if ext != ".pdf" && ext != ".txt" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "File type not allowed (.pdf, .txt only)"})
	}

	// 6. Save to Temp File (Best Practice)
	// สร้างโฟลเดอร์ temp ถ้ายังไม่มี
	tempDir := "./temp_uploads"
	if err := os.MkdirAll(tempDir, os.ModePerm); err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: "Failed to create temp directory"})
	}

	// สร้างชื่อไฟล์แบบ Unique (uuid + filename)
	safeFilename := fmt.Sprintf("%s_%s", uuid.New().String(), fileHeader.Filename)
	tempPath := filepath.Join(tempDir, safeFilename)

	// เขียนไฟล์ลง Disk
	src, err := fileHeader.Open()
	if err != nil {
		return err
	}
	defer src.Close()

	dst, err := os.Create(tempPath)
	if err != nil {
		return err
	}
	defer dst.Close()

	if _, err = io.Copy(dst, src); err != nil {
		return err
	}

	// 7. เรียก Service (Ingest)
	// ต้องใช้ defer os.Remove เพื่อลบไฟล์ temp ไม่ว่าจะเกิด error หรือไม่
	defer os.Remove(tempPath)

	count, err := h.DocumentService.IngestDocument(
		c.Request().Context(),
		tempPath,
		fileHeader.Filename,
		indexName,
		chunkSize,
		chunkOverlap,
		customMeta,
		separateNewline,
	)

	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	// 8. Clear Redis Cache for Semantic Caching
	ctx := c.Request().Context()
	var cursor uint64
	for {
		var keys []string
		var scanErr error
		keys, cursor, scanErr = h.RedisClient.Scan(ctx, cursor, "rag_semantic_cache*", 100).Result()
		if scanErr != nil {
			fmt.Println("Warning: Failed to scan Redis cache:", scanErr)
			break
		}
		for _, key := range keys {
			h.RedisClient.Del(ctx, key)
		}
		if cursor == 0 {
			break
		}
	}

	// Success Response
	return c.JSON(http.StatusOK, model.IngestDocumentResponse{
		Status:         "success",
		ChunkProcessed: count,
	})
}

func (h *DocumentHandler) DeleteFile(c echo.Context) error {
	var req model.DeleteFileRequest

	// Bind JSON Body
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "invalid JSON format"})
	}

	// Validate
	if req.Filename == "" || req.IndexName == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Missing 'filename' or 'index_name' parameter"})
	}

	// Call Service
	err := h.DocumentService.DeleteDocument(c.Request().Context(), req.Filename, req.IndexName)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	return c.JSON(http.StatusOK, model.DeleteDocumentResponse{Status: "success", Message: fmt.Sprintf("Deleted all vectors for '%s'", req.Filename)})
}

func (h *DocumentHandler) GetFileSources(c echo.Context) error {
	indexName := c.QueryParam("index_name")
	isAllIndexStr := c.QueryParam("is_all_index")

	// convert string -> bool
	isAllIndex := false
	if isAllIndexStr == "true" {
		isAllIndex = true
	}

	// 2. Validate
	if indexName == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Missing 'index_name' parameter"})
	}

	// 3. เรียกใช้ Service เพื่อดึงข้อมูล source ที่ไม่ซ้ำกัน
	// (คุณต้องไปสร้างฟังก์ชัน GetUniqueSources ใน Interface ของ DocumentService ด้วย)
	uniqueSources, err := h.DocumentService.GetFileSources(c.Request().Context(), indexName, isAllIndex)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	// 4. Return Response
	if isAllIndex {
		return c.JSON(http.StatusOK, model.GetFileSourcesResponse{
			Status:    "success",
			IndexName: "all index",
			Sources:   uniqueSources,
			Count:     len(uniqueSources),
		})
	}
	return c.JSON(http.StatusOK, model.GetFileSourcesResponse{
		Status:    "success",
		IndexName: indexName,
		Sources:   uniqueSources,
		Count:     len(uniqueSources),
	})
}

func (h *DocumentHandler) Search(c echo.Context) error {
	var req model.SearchRequest

	// Bind JSON Body
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Invalid JSON format"})
	}

	// Validate
	if req.Query == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Query is required"})
	}

	// Default Value for TopK
	if req.TopK == 0 {
		req.TopK = 5
	}

	// Call Service
	results, err := h.DocumentService.RetrieveMultiQuery(
		c.Request().Context(),
		req.Query,
		req.Index,
		req.Filter,
		req.TopK,
	)

	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	// Context Assembly (เอา Text มาต่อกันด้วย \n\n)
	contextText := strings.Join(results, "\n\n")

	// Return Response Format ตามต้นฉบับ
	return c.JSON(http.StatusOK, model.SearchDocumentResponse{
		Query:       req.Query,
		FileterUsed: req.Filter,
		Results:     contextText,
	})
}

func (h *DocumentHandler) GetDocumentChunks(c echo.Context) error {
	// 1. รับค่า Params
	rawSource := c.Param("source")
	indexName := c.QueryParam("index_name")

	sourceName, err := url.PathUnescape(rawSource)
	if err != nil {
		return c.JSON(http.StatusBadRequest, model.ErrorResponse{Error: "Invalid source encoding"})
	}

	// 2. Validate
	if indexName == "" {
		return c.JSON(http.StatusBadRequest, model.ErrorResponse{Error: "Missing 'index_name' parameter"})
	}
	if sourceName == "" {
		return c.JSON(http.StatusBadRequest, model.ErrorResponse{Error: "Missing 'source' parameter"})
	}

	// 3. เรียก Service
	chunks, err := h.DocumentService.GetDocumentChunks(c.Request().Context(), indexName, sourceName)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	// 4. Return Response
	return c.JSON(http.StatusOK, model.GetChunksResponse{
		Status:    "success",
		IndexName: indexName,
		Source:    sourceName,
		Chunks:    chunks,
		Count:     len(chunks),
	})
}
