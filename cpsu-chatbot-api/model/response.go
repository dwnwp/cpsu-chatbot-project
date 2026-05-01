package model

type MessageResponse struct {
	Message string `json:"message"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type IngestDocumentResponse struct {
	Status         string `json:"status"`
	ChunkProcessed int    `json:"chunk_processed"`
}

type DeleteDocumentResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

type DocumentSource struct {
	Name       string `json:"name"`
	UploadedAt string `json:"uploaded_at"`
}

type GetFileSourcesResponse struct {
	Status    string           `json:"status"`
	IndexName string           `json:"index_name"`
	Sources   []DocumentSource `json:"sources"`
	Count     int              `json:"count"`
}

type SearchDocumentResponse struct {
	Query       string                 `json:"query"`
	FileterUsed map[string]interface{} `json:"filter_used"`
	Results     string                 `json:"results"`
}

type ImageResponse struct {
	Message string   `json:"message"`
	Path    string   `json:"path,omitempty"`
	Paths   []string `json:"paths,omitempty"`
}

type ImageDetail struct {
	FileName   string `json:"file_name"`
	PublicURL  string `json:"public_url"`
	UploadedAt string `json:"uploaded_at"`
}

type ListImageResponse struct {
	Message string        `json:"message"`
	Folder  string        `json:"folder"`
	Count   int           `json:"count"`
	Files   []ImageDetail `json:"files"`
}