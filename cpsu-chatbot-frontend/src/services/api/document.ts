import apiClient from '../axios';

// --- RAG API (PDF, TXT) ---
export const ragApi = {
  getFileContent: async (source: string, index_name: string) => {
    const response = await apiClient.get(`/v1/rag/files/${encodeURIComponent(source)}`, {
      params: { index_name }
    });
    return response.data;
  },
  getFiles: async (index_name: string) => {
    // ใช้ { data: ... } สำหรับส่ง Body ใน GET request
    const response = await apiClient.get('/v1/rag/files', { params: { index_name: index_name } });
    return response.data;
  },
  deleteFile: async (filename: string, index_name: string) => {
    const response = await apiClient.delete('/v1/rag/files', { data: { filename, index_name } });
    return response.data;
  },
  uploadFile: async (formData: FormData) => {
    const response = await apiClient.post('/v1/rag/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// --- Image API (JPG, PNG) ---
export const imageApi = {
  getImages: async (folder_path: string) => {
    const response = await apiClient.get('/v1/images', { params: { folder_path: folder_path } });
    return response.data;
  },
  deleteImage: async (folder_path: string) => {
    const response = await apiClient.delete('/v1/images', { data: { folder_path } });
    return response.data;
  },
  uploadImage: async (formData: FormData) => {
    const response = await apiClient.post('/v1/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
};