<template>
  <DashboardLayout 
    title="รูปภาพ" 
    :menus="imageMenus" 
    :activeMenu="currentCategory"
    @update:activeMenu="changeCategory"
  >
    
    <ImageUploadModal 
    v-model:isOpen="isUploadModalOpen"
    :categoryName="currentCategory"
    :folderPath="categoryMap[currentCategory] || ''"
    @success="imageStore.fetchImages(categoryMap[currentCategory] || '')"
    />

    <div class="max-w-6xl mx-auto h-full flex flex-col relative pb-20">
      
      <h2 class="text-4xl font-bold mb-8 text-gray-900 animate-fade-in-up">{{ currentCategory }} <span class="text-xl font-normal text-gray-400">ระบบจัดการรูปภาพ</span></h2>

      <div class="flex items-center justify-end mb-6">
        <div class="flex items-center space-x-3 w-1/3">
          <button @click="refreshImages" class="bg-white text-gray-500 hover:text-[#1A7662] border hover:border-teal-200 border-gray-200 p-2.5 rounded-full transition-all cursor-pointer shadow-sm hover:shadow" title="รีเฟรชรูปภาพ" :disabled="imageLoading">
            <svg class="w-5 h-5" :class="imageLoading ? 'animate-spin text-[#1A7662]' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button>
          <div class="relative w-full">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="ค้นหาชื่อรูปภาพ..." 
              class="w-full pl-4 pr-10 py-2.5 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1A7662] focus:border-transparent text-sm"
            />
            <svg class="w-4 h-4 text-gray-400 absolute right-4 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border p-4 flex-1 overflow-y-auto min-h-[400px]" style="border-color: var(--color-border); box-shadow: var(--shadow-sm);">
        
        <div v-if="imageLoading" class="flex justify-center items-center h-full py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1A7662]"></div>
        </div>
        
        <div v-else class="space-y-3 stagger-list">
          <div 
            v-for="item in filteredImages" 
            :key="item.name"
            class="bg-white border rounded-xl p-4 flex items-center justify-between hover-lift animate-fade-in-up"
            style="border-color: var(--color-border);"
          >
            <div class="flex items-center">
              <div 
                @click="openImageViewer(item.url)"
                class="w-16 h-16 rounded-xl border overflow-hidden bg-gray-50 flex items-center justify-center mr-4 shrink-0 cursor-pointer hover:scale-105 transition-transform"
                style="border-color: var(--color-border);"
              >
                <img v-if="item.url" :src="item.url" alt="thumbnail" class="w-full h-full object-cover" />
                <svg v-else class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              </div>

              <div>
                <h4 class="font-bold text-gray-900 text-sm break-all">{{ item.name }}</h4>
                <p class="text-xs mt-0.5" :class="item.uploadedAt ? 'text-gray-500 text-[11px]' : 'text-gray-400 italic'">
                  {{ item.uploadedAt ? formatDate(item.uploadedAt) : 'ไม่ระบุเวลาอัปโหลด' }}
                </p>
              </div>
            </div>
            
            <button @click="deleteImage(item.name)" class="text-red-400 hover:text-red-600 p-2 transition-all hover:scale-110 shrink-0">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
          </div>
          
          <div v-if="filteredImages.length === 0" class="text-center py-16">
            <svg class="mx-auto w-16 h-16 text-gray-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            <p class="text-gray-400 font-medium">ยังไม่มีรูปภาพในหมวดหมู่นี้</p>
            <p class="text-gray-300 text-sm mt-1">คลิกปุ่ม "อัปโหลดรูปภาพ" เพื่อเพิ่มรูป</p>
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
          อัปโหลดรูปภาพ
        </button>
      </div>

      <div 
        v-if="selectedImageUrl" 
        class="fixed inset-0 z-[150] flex items-center justify-center bg-black/90 backdrop-blur-sm transition-opacity select-none"
        @click="closeImageViewer"
      >
        <div class="relative w-full h-full flex flex-col items-center justify-center overflow-hidden" @click.stop>
          
          <button 
            @click="closeImageViewer" 
            class="absolute top-6 right-6 text-gray-300 hover:text-white transition-colors bg-white/10 hover:bg-white/20 rounded-full p-3 z-50 cursor-pointer"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>

          <div class="absolute bottom-8 flex items-center space-x-4 bg-gray-900/80 backdrop-blur-md px-6 py-3 rounded-full z-50 shadow-2xl border border-gray-700">
            <button @click="zoomIn" class="text-gray-300 hover:text-white p-2 cursor-pointer transition-transform hover:scale-110">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path></svg>
            </button>
            
            <span class="text-white font-medium min-w-[3rem] text-center">{{ Math.round(zoomScale * 100) }}%</span>
            
            <button @click="zoomOut" class="text-gray-300 hover:text-white p-2 cursor-pointer transition-transform hover:scale-110">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path></svg>
            </button>

            <div class="w-px h-6 bg-gray-600 mx-2"></div>

            <button @click="resetZoom" class="text-sm font-medium text-gray-300 hover:text-white px-2 py-1 cursor-pointer">
              คืนค่า
            </button>
          </div>
          
          <div 
            class="w-full h-full flex items-center justify-center"
            :class="zoomScale > 1 ? 'cursor-grab active:cursor-grabbing' : ''"
            @wheel.prevent="handleWheel"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
          >
            <img 
              :src="selectedImageUrl" 
              class="max-w-full max-h-full object-contain origin-center transition-transform duration-75 ease-out" 
              :style="{ transform: `translate(${panPosition.x}px, ${panPosition.y}px) scale(${zoomScale})` }"
              draggable="false"
              alt="Enlarged img" 
            />
          </div>

        </div>
      </div>

    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import DashboardLayout from '@/layouts/DashboardLayout.vue';
import { useImageStore } from '@/stores/useImageStore';
import { useConfirmStore } from '@/stores/useConfirmStore';
import { imageApi } from '@/services/api/document';
import ImageUploadModal from '@/components/ImageUploadModal.vue';

const imageStore = useImageStore();
const { images, isLoading: imageLoading } = storeToRefs(imageStore);
const confirmStore = useConfirmStore();

// --- หมวดหมู่และการยิง API ---
const categoryMap: Record<string, string> = {
  'บุคลากร': 'images/academic_staff',
  'ปฏิทิน': 'images/calendar',
  'การยื่นคําร้องเรียน': 'images/channels_submit_complaints',
  'สำเร็จการศึกษา': 'images/graduated',
  'แผนที่': 'images/map_SU',
  'เวลาทํางานอาจารย์': 'images/office_hours',
  'ฝ่ายลงทะเบียน': 'images/registration_officer',
  'STEP': 'images/STEP',
  'ห้องภาควิชาคอมพิวเตอร์': 'images/computer_department_room',
};

const imageMenus = Object.keys(categoryMap);
const currentCategory = ref<string>(imageMenus[0] || 'บุคลากร');

const refreshImages = () => {
  const apiFolderPath = categoryMap[currentCategory.value] || 'images/other'; 
  imageStore.fetchImages(apiFolderPath);
};

const changeCategory = (menu: string) => {
  currentCategory.value = menu;
  refreshImages();
};

onMounted(() => changeCategory(currentCategory.value));

// --- ส่วนที่เพิ่มใหม่สำหรับการจัดการ UI ---
const searchQuery = ref('');
const isUploadModalOpen = ref(false);

const selectedImageUrl = ref<string | null>(null);
const zoomScale = ref(1);
const panPosition = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const startPan = ref({ x: 0, y: 0 });

const openImageViewer = (url: string) => {
  if (url) {
    selectedImageUrl.value = url;
    resetZoom(); // รีเซ็ตซูมทุกครั้งที่เปิดรูปใหม่
  }
};

const closeImageViewer = () => {
  selectedImageUrl.value = null;
  resetZoom();
};

const zoomIn = () => {
  zoomScale.value = Math.min(zoomScale.value + 0.25, 5);
};

const zoomOut = () => {
  zoomScale.value = Math.max(zoomScale.value - 0.25, 0.5);
};

const resetZoom = () => {
  zoomScale.value = 1;
  panPosition.value = { x: 0, y: 0 };
};

const handleWheel = (e: WheelEvent) => {
  const zoomSensitivity = 0.05;
  if (e.deltaY < 0) {
    zoomScale.value = Math.min(zoomScale.value + zoomSensitivity, 5);
  } else {
    zoomScale.value = Math.max(zoomScale.value - zoomSensitivity, 0.5);
  }
};

const startDrag = (e: MouseEvent) => {
  if (zoomScale.value <= 1) return; 
  isDragging.value = true;
  startPan.value = {
    x: e.clientX - panPosition.value.x,
    y: e.clientY - panPosition.value.y
  };
};

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return;
  panPosition.value = {
    x: e.clientX - startPan.value.x,
    y: e.clientY - startPan.value.y
  };
};

const endDrag = () => {
  isDragging.value = false;
};

// ตัวกรองข้อมูลตามช่องค้นหา
const filteredImages = computed(() => {
  let result = images.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(img => img.name.toLowerCase().includes(query));
  }

  return result;
});

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

// ฟังก์ชันสำหรับลบรูปภาพ
const deleteImage = async (filename: string) => {
  const isConfirmed = await confirmStore.open({
    title: 'ยืนยันการลบไฟล์',
    message: `คุณต้องการลบไฟล์ ${filename} ออกจากระบบใช่หรือไม่? การกระทำนี้ไม่สามารถกู้คืนได้`,
    confirmText: 'ลบไฟล์',
    isDanger: true
  });
  if (!isConfirmed) return;

  try {
    const folder = categoryMap[currentCategory.value] || 'images/other';
    const fullPath = `${folder}/${filename}`;
    await imageApi.deleteImage(fullPath);
    await imageStore.fetchImages(folder);
    
  } catch (error: any) {
    console.error('Delete image failed:', error);
    alert(error.response?.data?.message || 'เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์');
  }
};

</script>