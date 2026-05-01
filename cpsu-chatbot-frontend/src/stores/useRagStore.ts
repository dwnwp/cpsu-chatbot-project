import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ragApi } from '@/services/api/document';

export const useRagStore = defineStore('rag', () => {
  const documents = ref<any[]>([]);
  const isLoading = ref(false);

  // ตัวนับ request เพื่อป้องกัน race condition เมื่อเปลี่ยนหมวดหมู่เร็วๆ
  let _requestId = 0;

  const fetchDocuments = async (indexName: string) => {
    // 1. สร้าง ID สำหรับ request นี้ ถ้ามี request ใหม่เข้ามา ID จะไม่ตรงกัน
    const currentRequestId = ++_requestId;

    // 2. ล้างข้อมูลเก่าทิ้งทันที เพื่อป้องกันการแสดงผลข้ามหมวดหมู่
    documents.value = []; 
    isLoading.value = true;

    try {
      const res = await ragApi.getFiles(indexName);

      // 3. ตรวจสอบว่า request นี้ยังเป็น request ล่าสุดอยู่หรือไม่
      // ถ้าไม่ใช่ แสดงว่าผู้ใช้เปลี่ยนหมวดหมู่แล้ว → ไม่ต้องอัปเดต
      if (currentRequestId !== _requestId) return;
      
      if (res.status === 'success' && res.sources) {
        documents.value = res.sources.map((sourceItem: { name: string; uploaded_at: string }) => ({
          name: sourceItem.name,
          type: sourceItem.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'TXT',
          uploadedAt: sourceItem.uploaded_at,
        }));
      } else {
        documents.value = [];
      }
    } catch (error) {
      // ถ้า request นี้ไม่ใช่ล่าสุด ไม่ต้องจัดการ error
      if (currentRequestId !== _requestId) return;
      console.error("Fetch error:", error);
      documents.value = [];
    } finally {
      // อัปเดต loading เฉพาะ request ล่าสุดเท่านั้น
      if (currentRequestId === _requestId) {
        isLoading.value = false;
      }
    }
  };

  return { documents, isLoading, fetchDocuments };
});