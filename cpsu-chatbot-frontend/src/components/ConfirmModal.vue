<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 relative transform transition-all">
      
      <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4" 
           :class="options.isDanger ? 'bg-red-100' : 'bg-teal-100'">
        <svg v-if="options.isDanger" class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <svg v-else class="h-6 w-6 text-[#1A7662]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <div class="text-center mb-6">
        <h3 class="text-lg leading-6 font-bold text-gray-900 mb-2">{{ options.title }}</h3>
        <p class="text-sm text-gray-500">{{ options.message }}</p>
      </div>

      <div class="flex flex-row space-x-3">
        <button 
          @click="cancel" 
          class="flex-1 px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
        >
          {{ options.cancelText || 'ยกเลิก' }}
        </button>
        <button 
          @click="confirm" 
          :class="[
            'flex-1 px-4 py-2.5 rounded-lg text-white font-medium transition-colors',
            options.isDanger ? 'bg-red-600 hover:bg-red-700' : 'bg-[#1A7662] hover:bg-teal-800'
          ]"
        >
          {{ options.confirmText || 'ยืนยัน' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfirmStore } from '@/stores/useConfirmStore';

const confirmStore = useConfirmStore();
const { isOpen, options } = storeToRefs(confirmStore);
const { confirm, cancel } = confirmStore;
</script>