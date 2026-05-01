<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
    <div class="bg-white rounded-[24px] shadow-2xl w-full max-w-5xl overflow-hidden flex flex-col max-h-[95vh] animate-in fade-in zoom-in duration-200">
      
      <div class="px-10 py-8 pb-4 flex justify-between items-start">
        <div>
          <h2 class="text-[32px] font-bold text-black tracking-tight">ตั้งค่าการจัดการเอกสาร</h2>
          <p class="text-gray-500 mt-1 text-sm">เลือกรูปแบบการแบ่งเอกสารให้เหมาะสมกับประเภทข้อมูล</p>
        </div>
      </div>

      <div class="px-10 pb-10 overflow-y-auto flex-1 flex flex-col md:flex-row gap-12">
        
        <div class="w-full md:w-5/12 space-y-4">
          <div 
            v-for="(preset, index) in presets" :key="index"
            @click="selectPreset(preset)"
            :class="[
              'p-5 rounded-2xl border cursor-pointer transition-all duration-200',
              selectedPresetName === preset.name 
                ? 'border-[#1A7662] bg-[#CCE2DB] text-[#0A4D3C]' 
                : 'border-gray-200 bg-white hover:border-gray-300 text-gray-800 shadow-sm'
            ]"
          >
            <h4 class="font-bold text-lg">{{ preset.name }}</h4>
            <p :class="selectedPresetName === preset.name ? 'text-[#1A7662]' : 'text-gray-500'" class="text-sm mt-1" v-if="preset.description">
              {{ preset.description }}
            </p>
          </div>
        </div>

        <div class="w-full md:w-7/12 flex flex-col space-y-5">

          <!-- หมวดหมู่ — แสดงเสมอ -->
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
              หมวดหมู่
              <span class="tooltip-wrapper">
                <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="tooltip-text">เลือกหมวดหมู่ที่ตรงกับเนื้อหา เพื่อให้ AI จัดเก็บและค้นหาข้อมูลชุดนี้ได้แม่นยำและเป็นระเบียบมากขึ้น</span>
              </span>
            </label>
            <select 
              v-model="selectedIndex"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none bg-white font-medium"
            >
              <option v-for="(val, key) in categoryMap" :key="val" :value="val">{{ key }}</option>
            </select>
          </div>

          <!-- Metadata fields for ค่าใช้จ่าย -->
          <transition name="slide-fade">
            <div v-if="selectedIndex === 'tuition-fee'" class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                  ระดับการศึกษา
                  <span class="tooltip-wrapper">
                    <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="tooltip-text">เลือกระดับการศึกษาที่เกี่ยวข้องกับเอกสาร</span>
                  </span>
                </label>
                <select 
                  v-model="studyLevel"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none bg-white font-medium"
                >
                  <option value="all">ทั้งหมด (All)</option>
                  <option value="bachelor">ปริญญาตรี (Bachelor)</option>
                  <option value="master">ปริญญาโท (Master)</option>
                  <option value="doctoral">ปริญญาเอก (Doctoral)</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                  ประเภทหลักสูตร
                  <span class="tooltip-wrapper">
                    <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="tooltip-text">เลือกประเภทของหลักสูตรที่เกี่ยวข้อง</span>
                  </span>
                </label>
                <select 
                  v-model="programType"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none bg-white font-medium"
                >
                  <option value="all">ทั้งหมด (All)</option>
                  <option value="regular">โครงการปกติ (Regular)</option>
                  <option value="special">โครงการพิเศษ (Special)</option>
                </select>
              </div>
            </div>
          </transition>

          <!-- ตั้งค่าขั้นสูง — แสดงเฉพาะตอนเลือก "กำหนดเอง" -->
          <transition name="slide-fade">
            <div v-if="selectedPresetName === 'กำหนดเอง'" class="space-y-5">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                    Max Chunk Size
                    <span class="tooltip-wrapper">
                      <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      <span class="tooltip-text">ขนาดสูงสุดของแต่ละส่วน (หน่วยเป็นตัวอักษร) ยิ่งค่ามากจะได้เนื้อหาต่อส่วนมากขึ้น แต่อาจทำให้การค้นหาไม่แม่นยำ แนะนำ 400-1200</span>
                    </span>
                  </label>
                  <input 
                    type="number" 
                    v-model="customSize" 
                    class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none transition-all font-medium" 
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                    Chunk Overlap
                    <span class="tooltip-wrapper">
                      <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      <span class="tooltip-text">จำนวนตัวอักษรที่ซ้อนทับกันระหว่างส่วน เพื่อให้บริบทเชื่อมต่อกัน ค่ายิ่งมากจะช่วยรักษาบริบท แต่จะใช้พื้นที่จัดเก็บมากขึ้น</span>
                    </span>
                  </label>
                  <input 
                    type="number" 
                    v-model="customOverlap" 
                    class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none transition-all font-medium" 
                  />
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                  Separate Newline
                  <span class="tooltip-wrapper">
                    <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="tooltip-text">ให้ระบบพยายามตัดแบ่งเนื้อหาตรงจุดที่มีการขึ้นบรรทัดใหม่ (Enter) เพื่อรักษาโครงสร้างของย่อหน้าไว้</span>
                  </span>
                </label>
                <select 
                  v-model="separateNewline"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none bg-white font-medium"
                >
                  <option value="false">ไม่แยก</option>
                  <option value="true">แยกบรรทัด</option>
                </select>
              </div>
              <!-- Metadata key-value builder -->
              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-500 flex items-center gap-1">
                  Metadata
                  <span class="tooltip-wrapper">
                    <svg class="w-4 h-4 text-gray-400 hover:text-[#1A7662] transition-colors cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="tooltip-text">เพิ่มข้อมูลเพิ่มเติมแบบ key-value</span>
                  </span>
                </label>
                <div class="space-y-2">
                  <div v-for="(entry, idx) in metadataEntries" :key="idx" class="flex items-center gap-2">
                    <input 
                      type="text" 
                      v-model="entry.key" 
                      placeholder="Key"
                      class="flex-1 px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none text-sm font-medium" 
                    />
                    <span class="text-gray-400 text-sm font-bold">:</span>
                    <input 
                      type="text" 
                      v-model="entry.value" 
                      placeholder="Value"
                      class="flex-1 px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-[#1A7662] focus:border-transparent outline-none text-sm font-medium" 
                    />
                    <button 
                      @click="removeMetadataEntry(idx)" 
                      class="w-8 h-8 flex items-center justify-center rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                      title="ลบ"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                  </div>
                </div>
                <button 
                  @click="addMetadataEntry" 
                  class="flex items-center gap-1 text-sm text-[#1A7662] hover:text-teal-800 font-semibold transition-colors cursor-pointer mt-1"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                  เพิ่ม Metadata
                </button>
              </div>
            </div>
          </transition>

          <div 
            class="border-2 border-dashed rounded-xl p-6 text-center transition-all flex flex-col items-center justify-center relative flex-1 min-h-[140px]"
            :class="isDragging ? 'border-[#1A7662] bg-[#E8F3F0]' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
          >
            <input 
              type="file" 
              ref="fileInput" 
              @change="handleFileSelect" 
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              accept=".pdf,.txt" 
            />
            
            <div v-if="!file" class="space-y-2 pointer-events-none">
              <svg class="mx-auto w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
              <p class="text-sm text-gray-600 font-medium">
                <span class="text-[#1A7662]">คลิกเพื่อเลือกไฟล์</span> หรือลากไฟล์มาวาง<br/>
                <span class="text-xs text-gray-400 font-normal">รองรับเฉพาะ .PDF และ .TXT</span>
              </p>
            </div>
            
            <div v-else class="flex flex-col items-center z-10">
              <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mb-2">
                 <svg class="w-6 h-6 text-[#1A7662]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <p class="text-[#1A7662] font-bold text-sm truncate max-w-[250px]">{{ file.name }}</p>
              <button @click.stop="clearFile" class="text-xs text-red-500 mt-1 hover:underline cursor-pointer">ลบไฟล์นี้</button>
            </div>
          </div>

        </div>
      </div>

      <div class="px-10 py-6 bg-white flex justify-end gap-4 border-t border-gray-100">
        <button @click="closeModal" class="px-8 py-3 rounded-full text-white font-bold bg-[#8C8C8C] hover:bg-gray-500 transition-colors cursor-pointer shadow-sm">
          ยกเลิก
        </button>
        <button 
          @click="handleUpload" 
          :disabled="!file || isUploading"
          class="px-8 py-3 rounded-full text-white font-bold bg-[#1A7662] hover:bg-teal-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center shadow-sm"
        >
          <svg v-if="isUploading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ isUploading ? 'กำลังอัปโหลด...' : 'ยืนยัน' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ragApi } from '@/services/api/document';

const props = defineProps<{
  isOpen: boolean;
  defaultIndex?: string; // รับค่า index_name เริ่มต้นมาจากหน้า KnowledgeView
  initialFile?: File;    // ไฟล์เริ่มต้น (ใช้เมื่อแก้ไขไฟล์ TXT)
}>();

const emit = defineEmits(['update:isOpen', 'success']);

// --- หมวดหมู่สำหรับ Dropdown ---
const categoryMap: Record<string, string> = {
  'ค่าใช้จ่าย': 'tuition-fee',
  'หลักสูตร': 'academic',
  'บุคลากร': 'staff',
  'ทั่วไป': 'general'
};

// --- State การตั้งค่า API ---
const selectedIndex = ref(props.defaultIndex || 'academic');
const separateNewline = ref('false');

// --- Metadata fields for ค่าใช้จ่าย ---
const allStudyLevels = ['bachelor', 'master', 'doctoral'];
const allProgramTypes = ['regular', 'special'];
const studyLevel = ref('all');
const programType = ref('all');

// --- Dynamic metadata key-value entries ---
interface MetadataEntry { key: string; value: string; }
const metadataEntries = ref<MetadataEntry[]>([]);

const addMetadataEntry = () => {
  metadataEntries.value.push({ key: '', value: '' });
};
const removeMetadataEntry = (idx: number) => {
  metadataEntries.value.splice(idx, 1);
};

/** Build final metadata JSON string from all sources */
const buildMetadataJson = (): string | null => {
  const obj: Record<string, string | string[]> = {};

  // Auto-inject study_level & program_type for ค่าใช้จ่าย
  if (selectedIndex.value === 'tuition-fee') {
    obj.study_level = studyLevel.value === 'all' ? allStudyLevels : studyLevel.value;
    obj.program_type = programType.value === 'all' ? allProgramTypes : programType.value;
  }

  // Merge user-added key-value pairs
  for (const entry of metadataEntries.value) {
    const k = entry.key.trim();
    const v = entry.value.trim();
    if (k && v) obj[k] = v;
  }

  return Object.keys(obj).length > 0 ? JSON.stringify(obj) : null;
};

// อัปเดต selectedIndex อัตโนมัติเมื่อ defaultIndex เปลี่ยน
watch(() => props.defaultIndex, (newVal) => {
  if (newVal) selectedIndex.value = newVal;
});

// เมื่อ modal เปิดพร้อม initialFile ให้ set ไฟล์เริ่มต้น
watch(() => props.isOpen, (open) => {
  if (open && props.initialFile) {
    file.value = props.initialFile;
  }
});

// --- State ไฟล์ ---
const file = ref<File | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const isUploading = ref(false);

const handleFileSelect = (e: any) => { file.value = e.target.files[0]; };
const handleDrop = (e: DragEvent) => { 
  isDragging.value = false;
  if (e.dataTransfer?.files[0]) file.value = e.dataTransfer.files[0];
};
const clearFile = () => {
  file.value = null;
  if (fileInput.value) fileInput.value.value = '';
};

const closeModal = () => { 
  emit('update:isOpen', false); 
  clearFile();
  metadataEntries.value = [];
  studyLevel.value = 'all';
  programType.value = 'all';
};

// --- Chunk Configs (ตาม Mockup) ---
const presets = [
  { name: 'FAQ / ข้อมูลสั้นๆ', size: 400, overlap: 100, description: 'เหมาะสำหรับเอกสารที่มีรูปแบบถาม-ตอบ หรือมีเนื้อหาสั้นๆ' },
  { name: 'ข้อมูลทั่วไป / บทความ', size: 800, overlap: 250, description: 'เหมาะสำหรับคู่มือ ประกาศ หรือบทความทั่วไป' },
  { name: 'ไฟล์ขนาดใหญ่', size: 1200, overlap: 400, description: 'เหมาะสำหรับเอกสารที่มีความยาวมาก เช่น เล่มรายงาน' },
  { name: 'กำหนดเอง', size: 1000, overlap: 200, description: '' }
];
const defaultPreset = presets[0]!;
const selectedPresetName = ref(defaultPreset.name);
const customSize = ref(defaultPreset.size);
const customOverlap = ref(defaultPreset.overlap);

const selectPreset = (p: any) => {
  selectedPresetName.value = p.name;
  customSize.value = p.size;
  customOverlap.value = p.overlap;
};

// --- API Submit ---
const handleUpload = async () => {
  if (!file.value) return;
  isUploading.value = true;
  
  const formData = new FormData();
  formData.append('file', file.value);
  formData.append('chunk_size', customSize.value.toString());
  formData.append('chunk_overlap', customOverlap.value.toString());
  formData.append('index_name', selectedIndex.value);
  formData.append('separate_newline', separateNewline.value);
  
  // Build metadata from key-value entries + tuition-fee selects
  const metadataJson = buildMetadataJson();
  if (metadataJson) {
    formData.append('metadata', metadataJson);
  }

  try {
    await ragApi.uploadFile(formData);
    emit('success');
    closeModal();
  } catch (err: any) {
    console.error('Upload Error:', err);
    alert(err.response?.data?.message || 'อัปโหลดล้มเหลว กรุณาลองใหม่');
  } finally {
    isUploading.value = false;
  }
};
</script>

<style scoped>
.tooltip-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.tooltip-text {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #1f2937;
  color: #fff;
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
  padding: 8px 12px;
  border-radius: 10px;
  width: 240px;
  text-align: left;
  z-index: 9999;
  pointer-events: none;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tooltip-text::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent #1f2937 transparent;
}

.tooltip-wrapper:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>