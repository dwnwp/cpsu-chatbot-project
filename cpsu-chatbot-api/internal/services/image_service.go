package services

import (
	"context"
	"fmt"
	"mime/multipart"
	"path/filepath"
	"time"

	"gitlab.com/project-together/cpsu-chatbot-api/model"
	"gitlab.com/project-together/cpsu-chatbot-api/storage"
)

type ImageService interface {
	UploadImage(ctx context.Context, fileHeader *multipart.FileHeader, folder string) (string, error)
	DeleteImage(ctx context.Context, objectPath string) error
	ListImages(ctx context.Context, folder string) ([]model.ImageDetail, error)
}

type imageServiceImpl struct {
	store storage.CloudStorage
}

func NewImageService(store storage.CloudStorage) ImageService {
	return &imageServiceImpl{store: store}
}

func (s *imageServiceImpl) UploadImage(ctx context.Context, fileHeader *multipart.FileHeader, folder string) (string, error) {
	// เปิดไฟล์เพื่อเตรียมอ่านข้อมูล
	file, err := fileHeader.Open()
	if err != nil {
		return "", err
	}
	defer file.Close()

	// ตั้งชื่อไฟล์ใหม่
	filename := fmt.Sprintf("%s", filepath.Base(fileHeader.Filename))
	objectPath := filename
	if folder != "" {
		objectPath = fmt.Sprintf("%s/%s", folder, filename)
	}

	// กำหนด Timeout สำหรับการอัปโหลด (50 วินาที)
	uploadCtx, cancel := context.WithTimeout(ctx, 50*time.Second)
	defer cancel()

	contentType := fileHeader.Header.Get("Content-Type")
	if contentType == "" {
		contentType = "application/octet-stream"
	}

	// เรียกใช้ Storage เลเยอร์
	err = s.store.UploadFile(uploadCtx, objectPath, file, fileHeader.Size, contentType)
	if err != nil {
		return "", err
	}

	return objectPath, nil
}

func (s *imageServiceImpl) DeleteImage(ctx context.Context, objectPath string) error {
	// กำหนด Timeout สำหรับการลบ (10 วินาที)
	deleteCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	return s.store.DeleteFile(deleteCtx, objectPath)
}

func (s *imageServiceImpl) ListImages(ctx context.Context, folder string) ([]model.ImageDetail, error) {
	listCtx, cancel := context.WithTimeout(ctx, 15*time.Second)
	defer cancel()

	return s.store.ListFiles(listCtx, folder)
}
