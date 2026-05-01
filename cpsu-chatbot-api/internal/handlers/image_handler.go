package handler

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"gitlab.com/project-together/cpsu-chatbot-api/internal/services"
	"gitlab.com/project-together/cpsu-chatbot-api/model"
)

type ImageHandler struct {
	imgService services.ImageService
}

func NewImageHandler(imgService services.ImageService) *ImageHandler {
	return &ImageHandler{imgService: imgService}
}

func (h *ImageHandler) Upload(c echo.Context) error {
	folder := c.FormValue("folder_path")

	form, err := c.MultipartForm()
	if err != nil {
		return c.JSON(http.StatusBadRequest, model.ErrorResponse{Error: "Cannot parse multipart form: " + err.Error()})
	}

	files := form.File["images"]
	if len(files) == 0 {
		// Fallback for backward compatibility
		files = form.File["image"]
		if len(files) == 0 {
			return c.JSON(http.StatusBadRequest, model.ErrorResponse{Error: "No images provided"})
		}
	}

	ctx := c.Request().Context()
	var uploadedPaths []string

	for _, fileHeader := range files {
		objectPath, err := h.imgService.UploadImage(ctx, fileHeader, folder)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: "Failed to upload image: " + err.Error()})
		}
		uploadedPaths = append(uploadedPaths, objectPath)
	}

	// Just for backward compatibility, provide the first path to `Path`
	firstPath := ""
	if len(uploadedPaths) > 0 {
		firstPath = uploadedPaths[0]
	}

	return c.JSON(http.StatusOK, model.ImageResponse{
		Message: "Uploaded successfully",
		Path:    firstPath,
		Paths:   uploadedPaths,
	})
}

func (h *ImageHandler) Delete(c echo.Context) error {
	var req model.DeleteImageRequest

	// Bind JSON Body
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "invalid JSON format"})
	}

	// Validate
	if req.FolderPath == "" {
		return c.JSON(http.StatusBadRequest, model.MessageResponse{Message: "Missing 'folder_path' parameter"})
	}

	ctx := c.Request().Context()
	err := h.imgService.DeleteImage(ctx, req.FolderPath)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	return c.JSON(http.StatusOK, model.ImageResponse{
		Message: "Deleted successfully",
		Path:    req.FolderPath,
	})
}

func (h *ImageHandler) List(c echo.Context) error {
	folderPath := c.QueryParam("folder_path")

	ctx := c.Request().Context()

	files, err := h.imgService.ListImages(ctx, folderPath)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, model.ErrorResponse{Error: err.Error()})
	}

	// กรณีที่ค้นหาแล้วไม่เจอไฟล์เลย ป้องกันการส่งค่า null กลับไป
	if files == nil {
		files = []model.ImageDetail{}
	}

	return c.JSON(http.StatusOK, model.ListImageResponse{
		Message: "successfully",
		Folder:  folderPath,
		Count:   len(files),
		Files:   files,
	})
}
