package model

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type DeleteFileRequest struct {
	Filename  string `json:"filename"`
	IndexName string `json:"index_name"`
}

type SearchRequest struct {
	Query  string                 `json:"query"`
	Index  string                 `json:"index"`
	Filter map[string]interface{} `json:"filter"`
	TopK   int                    `json:"top_k"`
}

type RegisterRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type ChangePasswordRequest struct {
	Username    string `json:"username"`
	Password    string `json:"password"`
	NewPassword string `json:"new_password"`
}

type DeleteAccountRequest struct {
	Username string `json:"username"`
}

type DeleteImageRequest struct {
	FolderPath string `json:"folder_path"`
}

type DocumentChunk struct {
	ID   string `json:"id"`
	Text string `json:"text"`
}

type GetChunksResponse struct {
	Status    string          `json:"status"`
	IndexName string          `json:"index_name"`
	Source    string          `json:"source"`
	Chunks    []DocumentChunk `json:"chunks"`
	Count     int             `json:"count"`
}
