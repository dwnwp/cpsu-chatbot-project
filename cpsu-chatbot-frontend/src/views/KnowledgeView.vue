<template>
  <DashboardLayout 
    title="เอกสาร" 
    :menus="ragMenus" 
    :activeMenu="currentCategory"
    @update:activeMenu="changeCategory"
  >
    <div class="max-w-6xl mx-auto h-full flex flex-col relative pb-20">
      
      <h2 class="text-4xl font-bold mb-8 text-gray-900 animate-fade-in-up">{{ currentCategory }} <span class="text-xl font-normal text-gray-400">ระบบฐานความรู้</span></h2>

      <!-- ===== โหมดแก้ไขไฟล์ TXT ===== -->
      <template v-if="editingFile">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-lg border border-gray-300 bg-gray-50 text-gray-700 flex items-center justify-center">
              <span class="font-bold text-xs">TXT</span>
            </div>
            <div>
              <h3 class="font-bold text-gray-900">{{ editingFile }}</h3>
              <p class="text-sm text-gray-400">กำลังแก้ไขเนื้อหา</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 flex-1 flex flex-col overflow-hidden shadow-sm min-h-[400px]">
          <div v-if="isLoadingContent" class="flex justify-center items-center h-full py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1A7662]"></div>
          </div>

          <textarea 
            v-else
            v-model="editContent"
            class="flex-1 w-full h-full p-6 text-sm text-gray-800 leading-relaxed resize-none outline-none font-mono"
            placeholder="เนื้อหาเอกสาร..."
          ></textarea>
        </div>

        <div class="flex justify-end space-x-3 mt-4">
          <button 
            @click="cancelEdit"
            class="px-6 py-2.5 rounded-full text-gray-600 font-bold hover:bg-gray-100 transition-colors cursor-pointer"
          >
            ยกเลิก
          </button>
          <button 
            @click="saveEdit"
            :disabled="isSaving"
            class="px-8 py-2.5 rounded-full text-white font-bold bg-[#1A7662] hover:bg-teal-800 disabled:opacity-50 transition-all flex items-center cursor-pointer"
          >
            <svg v-if="isSaving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            {{ isSaving ? 'กำลังบันทึก...' : 'บันทึก' }}
          </button>
        </div>
      </template>

      <!-- ===== โหมดแสดงรายการไฟล์ (ปกติ) ===== -->
      <template v-else>
        <div class="flex items-center justify-between mb-6">
          <div class="flex bg-white rounded-xl border overflow-hidden" style="border-color: var(--color-border);">
            <button 
              v-for="tab in tabs" :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-2.5 text-sm font-medium transition-all duration-200 border-r last:border-r-0',
                activeTab === tab.id ? 'bg-[#1A7662] text-white shadow-inner' : 'text-gray-400 hover:bg-gray-50 hover:text-gray-600'
              ]"
              :style="{ borderColor: 'var(--color-border)' }"
            >
              {{ tab.name }}
            </button>
          </div>

          <div class="flex items-center space-x-3 w-1/3">
            <button @click="refreshDocuments" class="bg-white text-gray-500 hover:text-[#1A7662] border hover:border-teal-200 border-gray-200 p-2.5 rounded-full transition-all cursor-pointer shadow-sm hover:shadow" title="รีเฟรชเอกสาร" :disabled="ragLoading">
              <svg class="w-5 h-5" :class="ragLoading ? 'animate-spin text-[#1A7662]' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            </button>
            <div class="relative w-full">
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="ค้นหาชื่อไฟล์..." 
                class="w-full pl-4 pr-10 py-2.5 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1A7662] focus:border-transparent text-sm"
              />
              <svg class="w-4 h-4 text-gray-400 absolute right-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border p-4 flex-1 overflow-y-auto min-h-[400px]" style="border-color: var(--color-border); box-shadow: var(--shadow-sm);">
          
          <div v-if="ragLoading" class="flex justify-center items-center h-full py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1A7662]"></div>
          </div>
          
          <div v-else class="space-y-3 stagger-list">
            <div 
              v-for="item in filteredDocuments" 
              :key="item.name"
              class="bg-white border rounded-xl p-4 flex items-center justify-between hover-lift animate-fade-in-up"
              style="border-color: var(--color-border);"
            >
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-lg border flex items-center justify-center mr-4" 
                     :class="item.type === 'PDF' ? 'border-red-200 bg-red-50 text-red-500' : 'border-gray-300 bg-gray-50 text-gray-700'">
                  <span class="font-bold text-xs">{{ item.type }}</span>
                </div>

                <div>
                  <h4 class="font-bold text-gray-900 text-sm">{{ item.name }}</h4>
                  <p class="text-xs mt-0.5" :class="item.uploadedAt ? 'text-gray-500 text-[11px]' : 'text-gray-400 italic'">
                    {{ item.uploadedAt ? formatDate(item.uploadedAt) : 'ไม่ระบุเวลาอัปโหลด' }}
                  </p>
                </div>
              </div>
              
              <div class="flex items-center space-x-1">
                <button 
                  v-if="item.type === 'TXT'" 
                  @click="startEdit(item.name)" 
                  class="text-[#1A7662] hover:text-teal-800 p-2 transition-all hover:scale-110"
                  title="แก้ไขเอกสาร"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                </button>

                <button @click="deleteDocument(item.name)" class="text-red-400 hover:text-red-600 p-2 transition-all hover:scale-110">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            </div>
            
            <div v-if="filteredDocuments.length === 0" class="text-center py-16">
              <svg class="mx-auto w-16 h-16 text-gray-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <p class="text-gray-400 font-medium">ยังไม่มีเอกสารในหมวดหมู่นี้</p>
              <p class="text-gray-300 text-sm mt-1">คลิกปุ่ม "อัปโหลดไฟล์" เพื่อเพิ่มเอกสาร</p>
            </div>
          </div>
        </div>

        <div class="absolute bottom-4 right-4">
          <button 
            @click="isUploadModalOpen = true"
            class="bg-[#1A7662] text-white px-6 py-3 rounded-full hover:bg-teal-800 transition-all font-medium text-sm flex items-center cursor-pointer animate-pulse-glow hover:scale-105"
            style="box-shadow: var(--shadow-lg);"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
            อัปโหลดไฟล์
          </button>
        </div>
      </template>

      <RagUploadModal 
        v-model:isOpen="isUploadModalOpen"
        :defaultIndex="categoryMap[currentCategory] || 'academic'"
        :initialFile="editedFile ?? undefined"
        @success="handleUploadSuccess"
      />

    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useRagStore } from '@/stores/useRagStore';
import { useConfirmStore } from '@/stores/useConfirmStore';
import { ragApi } from '@/services/api/document';
import RagUploadModal from '@/components/RagUploadModal.vue';

const ragStore = useRagStore();
const { documents, isLoading: ragLoading } = storeToRefs(ragStore);
const confirmStore = useConfirmStore();

// --- หมวดหมู่และการยิง API ---
const categoryMap: Record<string, string> = {
  'ค่าใช้จ่าย': 'tuition-fee',
  'หลักสูตร': 'academic',
  'บุคลากร': 'staff',
  'ทั่วไป': 'general'
};
const ragMenus = Object.keys(categoryMap);
const currentCategory = ref<string>(ragMenus[0] || 'หลักสูตร');

const refreshDocuments = () => {
  const apiIndexName = categoryMap[currentCategory.value] || 'other'; 
  ragStore.fetchDocuments(apiIndexName);
};

const changeCategory = (menu: string) => {
  currentCategory.value = menu;
  cancelEdit(); // ยกเลิกการแก้ไขถ้ากำลังแก้ไขอยู่
  refreshDocuments();
};

onMounted(() => changeCategory(currentCategory.value));

// --- UI State ---
const tabs = [
  { id: 'ALL', name: 'ทั้งหมด' },
  { id: 'PDF', name: 'PDF' },
  { id: 'TXT', name: 'TXT' }
];

const activeTab = ref('ALL');
const searchQuery = ref('');
const isUploadModalOpen = ref(false);
const isDeleting = ref(false);

// --- ตัวกรองข้อมูล ---
const filteredDocuments = computed(() => {
  let result = documents.value;

  if (activeTab.value !== 'ALL') {
    result = result.filter(doc => doc.type === activeTab.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(doc => doc.name.toLowerCase().includes(query));
  }

  return result;
});

// --- โหมดแก้ไขไฟล์ TXT ---
const editingFile = ref<string | null>(null);
const editContent = ref('');
const isLoadingContent = ref(false);
const isSaving = ref(false);
const editedFile = ref<File | null>(null);

const startEdit = async (filename: string) => {
  editingFile.value = filename;
  editContent.value = '';
  isLoadingContent.value = true;

  try {
    const indexName = categoryMap[currentCategory.value] || 'academic';
    const res = await ragApi.getFileContent(filename, indexName);

    if (res.status === 'success' && res.chunks) {
      // รวม chunk text ตามลำดับ id (ascending)
      const sortedChunks = [...res.chunks].sort((a: any, b: any) => Number(a.id) - Number(b.id));
      editContent.value = sortedChunks.map((chunk: any) => chunk.text).join('\n\n');
    }
  } catch (error: any) {
    console.error('Load file content failed:', error);
    alert(error.response?.data?.error || 'ไม่สามารถโหลดเนื้อหาไฟล์ได้');
    editingFile.value = null;
  } finally {
    isLoadingContent.value = false;
  }
};

const cancelEdit = () => {
  editingFile.value = null;
  editContent.value = '';
  editedFile.value = null;
};

const saveEdit = async () => {
  if (!editingFile.value) return;

  // ยืนยันก่อนลบไฟล์เก่า เพื่อป้องกันการลบโดยไม่ตั้งใจ
  const isConfirmed = await confirmStore.open({
    title: 'ยืนยันการบันทึก',
    message: `ระบบจะลบไฟล์ "${editingFile.value}" เดิมออก แล้วเปิดหน้าอัปโหลดไฟล์ใหม่ที่แก้ไขแล้ว ต้องการดำเนินการต่อหรือไม่?`,
    confirmText: 'ดำเนินการต่อ',
    cancelText: 'ยกเลิก',
    isDanger: false
  });
  if (!isConfirmed) return;

  isSaving.value = true;

  try {
    const indexName = categoryMap[currentCategory.value] || 'academic';
    const filename = editingFile.value;

    // 1. ลบไฟล์เก่า
    await ragApi.deleteFile(filename, indexName);

    // 2. สร้าง File blob จากเนื้อหาที่แก้ไข
    const blob = new Blob([editContent.value], { type: 'text/plain' });
    const newFile = new File([blob], filename, { type: 'text/plain' });

    // 3. เก็บไฟล์ไว้เพื่อส่งให้ Modal แล้วเปิด Upload Modal
    editedFile.value = newFile;
    editingFile.value = null;
    editContent.value = '';
    isUploadModalOpen.value = true;

  } catch (error: any) {
    console.error('Save edit failed:', error);
    alert(error.response?.data?.message || 'เกิดข้อผิดพลาดในการบันทึก');
  } finally {
    isSaving.value = false;
  }
};

const handleUploadSuccess = () => {
  editedFile.value = null;
  const indexName = categoryMap[currentCategory.value] || 'academic';
  ragStore.fetchDocuments(indexName);
};

// --- Helper: Format Date ---
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('th-TH', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date) + ' น.';
};

// --- ลบเอกสาร ---
const deleteDocument = async (filename: string) => {
  const isConfirmed = await confirmStore.open({
    title: 'ยืนยันการลบไฟล์',
    message: `คุณต้องการลบไฟล์ ${filename} ออกจากระบบใช่หรือไม่? การกระทำนี้ไม่สามารถกู้คืนได้`,
    confirmText: 'ลบไฟล์',
    isDanger: true
  });
  if (!isConfirmed) return;
  
  isDeleting.value = true;
  try {
    const indexName = categoryMap[currentCategory.value] || 'academic';

    await ragApi.deleteFile(filename, indexName);
    await ragStore.fetchDocuments(indexName);
  } catch (error: any) {
    console.error('Delete failed:', error);
    alert(error.response?.data?.message || 'เกิดข้อผิดพลาดในการลบเอกสาร');
  } finally {
    isDeleting.value = false;
  }
};
</script>