<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col animate-in fade-in zoom-in duration-200">
      
      <div class="px-8 py-6 border-b border-gray-100 flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-extrabold text-gray-900">อัปโหลดรูปภาพ</h2>
          <p class="text-gray-500 text-sm mt-1">หมวดหมู่: {{ categoryName }}</p>
        </div>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 p-2 cursor-pointer">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="p-8">
        <div 
          class="border-2 border-dashed rounded-2xl p-10 text-center transition-all min-h-[200px] flex flex-col items-center justify-center relative"
          :class="isDragging ? 'border-[#1A7662] bg-teal-50' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileSelect" 
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
            accept=".jpg,.jpeg,.png" 
            multiple
          />
          
          <div v-if="files.length === 0" class="space-y-3">
            <div class="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center mx-auto text-gray-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            </div>
            <p class="text-sm text-gray-500 font-medium">
              <span class="text-[#1A7662] font-bold">เลือกรูปภาพ</span> หรือลากไฟล์มาวาง<br/>
              <span class="text-xs opacity-60">รองรับ .jpg, .jpeg, .png</span>
            </p>
          </div>
          
          <div v-else class="w-full z-10 relative pointer-events-auto">
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-[250px] overflow-y-auto p-2">
               <div v-for="(f, index) in files" :key="index" class="relative group flex flex-col items-center">
                 <img :src="previewUrls[index]" class="w-20 h-20 object-cover rounded-lg shadow-md" alt="uploading img"/>
                 <button @click.stop="removeFile(index)" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-sm cursor-pointer hover:bg-red-600">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                 </button>
                 <p class="text-[#1A7662] font-bold text-xs truncate w-full text-center mt-2 px-1">{{ f.name }}</p>
               </div>
            </div>
            <div class="mt-4 flex justify-center">
               <button @click.stop="clearFiles" class="text-xs text-red-500 font-medium hover:underline cursor-pointer px-3 py-1 rounded-full hover:bg-red-50 transition-colors">ล้างรูปทั้งหมด</button>
            </div>
          </div>
        </div>
      </div>

      <div class="px-8 py-5 bg-gray-50 flex justify-end gap-3">
        <button @click="closeModal" class="px-6 py-2.5 rounded-xl text-gray-500 font-bold hover:bg-gray-100 cursor-pointer">ยกเลิก</button>
        <button 
          @click="handleUpload" 
          :disabled="files.length === 0 || isUploading"
          class="px-8 py-2.5 rounded-xl text-white font-bold bg-[#1A7662] hover:bg-teal-800 disabled:opacity-50 transition-all flex items-center cursor-pointer"
        >
          <svg v-if="isUploading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ isUploading ? 'กำลังอัปโหลด...' : 'ยืนยันการอัปโหลด' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { imageApi } from '@/services/api/document';

const props = defineProps<{
  isOpen: boolean;
  categoryName: string; // ชื่อภาษาไทยไว้โชว์ Header
  folderPath: string;   // path จริงที่จะส่งไป API
}>();

const emit = defineEmits(['update:isOpen', 'success']);

const files = ref<File[]>([]);
const previewUrls = ref<string[]>([]);
const isDragging = ref(false);
const isUploading = ref(false);

const closeModal = () => {
  emit('update:isOpen', false);
  clearFiles();
};

const handleFileSelect = (e: any) => {
  const selected = Array.from(e.target.files) as File[];
  if (selected.length) addFiles(selected);
  e.target.value = '';
};

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  const dropped = Array.from(e.dataTransfer?.files || []) as File[];
  if (dropped.length) addFiles(dropped);
};

const addFiles = (selectedFiles: File[]) => {
  files.value.push(...selectedFiles);
  selectedFiles.forEach(f => {
    previewUrls.value.push(URL.createObjectURL(f));
  });
};

const clearFiles = () => {
  files.value = [];
  previewUrls.value = [];
};

const removeFile = (index: number) => {
  files.value.splice(index, 1);
  previewUrls.value.splice(index, 1);
};

const handleUpload = async () => {
  if (files.value.length === 0) return;
  isUploading.value = true;
  
  const formData = new FormData();
  files.value.forEach(f => {
    formData.append('images', f);
  });
  formData.append('folder_path', props.folderPath);

  try {
    await imageApi.uploadImage(formData);
    emit('success');
    closeModal();
  } catch (err: any) {
    alert(err.response?.data?.error || 'อัปโหลดล้มเหลว');
  } finally {
    isUploading.value = false;
  }
};
</script>