import { defineStore } from 'pinia';
import { ref } from 'vue';
import { imageApi } from '@/services/api/document';

export const useImageStore = defineStore('image', () => {
  const images = ref<any[]>([]);
  const isLoading = ref(false);

  // ตัวนับ request เพื่อป้องกัน race condition เมื่อเปลี่ยนหมวดหมู่เร็วๆ
  let _requestId = 0;

  const fetchImages = async (folderPath: string) => {
    const currentRequestId = ++_requestId;

    images.value = [];
    isLoading.value = true;
    try {
      const res = await imageApi.getImages(folderPath);

      // ถ้า request นี้ไม่ใช่ล่าสุด → ไม่ต้องอัปเดต
      if (currentRequestId !== _requestId) return;

      if (res.message === 'successfully') {
        images.value = res.files.map((file: any) => ({
          name: file.file_name,
          type: 'IMAGE',
          url: file.public_url,
          uploadedAt: file.uploaded_at,
        }));
      } else { images.value = []; }
    } catch (error) {
      if (currentRequestId !== _requestId) return;
      console.error("Fetch images error:", error);
      images.value = [];
    } finally {
      if (currentRequestId === _requestId) {
        isLoading.value = false;
      }
    }
  };
  return { images, isLoading, fetchImages };
});