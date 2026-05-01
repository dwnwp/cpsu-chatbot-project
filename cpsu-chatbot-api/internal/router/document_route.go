package router

import (
	"github.com/labstack/echo/v4"
	"github.com/qdrant/go-client/qdrant"
	"github.com/redis/go-redis/v9"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms"
	handler "gitlab.com/project-together/cpsu-chatbot-api/internal/handlers"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/services"
)

func InitDocumentRoutes(e *echo.Group, embedder embeddings.Embedder, llm llms.Model, qdrantClient *qdrant.Client, redisClient *redis.Client) {
	documentService := services.NewDocumentService(embedder, llm, qdrantClient)
	documentHandler := handler.NewDocumentHandler(*documentService, redisClient)

	ragGroup := e.Group(
		"/rag",
		authMiddleware,
	)

	ragGroup.POST("/files", documentHandler.Ingest)
	ragGroup.DELETE("/files", documentHandler.DeleteFile)
	ragGroup.POST("/search", documentHandler.Search)
	ragGroup.GET("/files", documentHandler.GetFileSources)
	ragGroup.GET("/files/:source", documentHandler.GetDocumentChunks)
}
