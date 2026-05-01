package storage

import (
	"context"
	"fmt"
	"io"
	"path/filepath"
	"time"

	"github.com/minio/minio-go/v7"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/environment"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
)

type cloudStorage struct {
	minioClient *minio.Client
	bucketName  string
}

type CloudStorage interface {
	UploadFile(ctx context.Context, objectPath string, file io.Reader, size int64, contentType string) error
	DeleteFile(ctx context.Context, objectPath string) error
	ListFiles(ctx context.Context, prefix string) ([]model.ImageDetail, error)
}

func NewCloudStorage(minioClient *minio.Client) CloudStorage {
	return &cloudStorage{
		minioClient: minioClient,
		bucketName:  environment.GetMinioBucketName(),
	}
}

func (s *cloudStorage) UploadFile(ctx context.Context, objectPath string, file io.Reader, size int64, contentType string) error {
	_, err := s.minioClient.PutObject(ctx, s.bucketName, objectPath, file, size, minio.PutObjectOptions{ContentType: contentType})
	return err
}

func (s *cloudStorage) DeleteFile(ctx context.Context, objectPath string) error {
	return s.minioClient.RemoveObject(ctx, s.bucketName, objectPath, minio.RemoveObjectOptions{})
}

func (s *cloudStorage) ListFiles(ctx context.Context, prefix string) ([]model.ImageDetail, error) {
	var files []model.ImageDetail

	opts := minio.ListObjectsOptions{
		Prefix:    prefix,
		Recursive: true,
	}

	for object := range s.minioClient.ListObjects(ctx, s.bucketName, opts) {
		if object.Err != nil {
			return nil, object.Err
		}

		if object.Size == 0 || object.Key[len(object.Key)-1] == '/' {
			continue
		}

		fileName := filepath.Base(object.Key)

		endpoint := environment.GetMinioExternalEndpoint()
		protocol := "https"
		
		publicURL := fmt.Sprintf("%s://%s/%s/%s", protocol, endpoint, s.bucketName, object.Key)

		files = append(files, model.ImageDetail{
			FileName:   fileName,
			PublicURL:  publicURL,
			UploadedAt: object.LastModified.Format(time.RFC3339),
		})
	}

	return files, nil
}
