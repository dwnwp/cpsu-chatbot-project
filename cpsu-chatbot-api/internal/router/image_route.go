package router

import (
	"github.com/labstack/echo/v4"
	"github.com/minio/minio-go/v7"
	handler "gitlab.com/project-together/cpsu-chatbot-api/internal/handlers"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/services"
	"gitlab.com/project-together/cpsu-chatbot-api/storage"
)

func InitImageRouter(e *echo.Group, minioClient *minio.Client) {
	minioStorage := storage.NewCloudStorage(minioClient)
	imageService := services.NewImageService(minioStorage)
	imageHandler := handler.NewImageHandler(imageService)

	imageGroup := e.Group(
		"/images",
		authMiddleware,
	)

	imageGroup.POST("", imageHandler.Upload)
	imageGroup.DELETE("", imageHandler.Delete)
	imageGroup.GET("", imageHandler.List)
}
