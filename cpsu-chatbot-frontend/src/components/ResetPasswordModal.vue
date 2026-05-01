<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
      
      <button @click="closeModal" class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition-colors">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>

      <h3 class="text-2xl font-bold text-[#1A7662] mb-6">Reset Password</h3>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="message" :class="isSuccess ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="p-3 rounded-md text-sm text-center">
          {{ message }}
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input v-model="form.username" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#1A7662] outline-none" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
          <input v-model="form.password" type="password" required class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#1A7662] outline-none" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
          <input v-model="form.new_password" type="password" required class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#1A7662] outline-none" />
        </div>

        <div class="flex justify-end space-x-3 mt-8">
          <button type="button" @click="closeModal" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md font-medium transition-colors">Cancel</button>
          <button type="submit" :disabled="isLoading" class="px-4 py-2 bg-[#1A7662] text-white rounded-md hover:bg-teal-800 font-medium transition-colors disabled:opacity-70 flex items-center">
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'Processing...' : 'Reset Password' }}
          </button>
        </div>
      </form>

    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useAuthStore } from '@/stores/useAuthStore';

// รับค่า isOpen จากหน้าหลักเพื่อเปิด/ปิด Modal
defineProps<{ isOpen: boolean }>();
const emit = defineEmits(['close']);

const authStore = useAuthStore();
const isLoading = ref(false);
const message = ref('');
const isSuccess = ref(false);

const form = reactive({
  username: '',
  password: '',
  new_password: ''
});

const closeModal = () => {
  // เคลียร์ค่าฟอร์มก่อนปิด
  form.username = '';
  form.password = '';
  form.new_password = '';
  message.value = '';
  isSuccess.value = false;
  emit('close');
};

const handleSubmit = async () => {
  isLoading.value = true;
  message.value = '';
  
  const result = await authStore.resetPassword(form);
  
  isSuccess.value = result?.success || false;
  message.value = result?.message || '';
  isLoading.value = false;

  // ถ้าเปลี่ยนรหัสผ่านสำเร็จ ให้หน่วงเวลา 1.5 วินาทีแล้วปิด Modal อัตโนมัติ
  if (isSuccess.value) {
    setTimeout(() => {
      closeModal();
    }, 1500);
  }
};
</script>