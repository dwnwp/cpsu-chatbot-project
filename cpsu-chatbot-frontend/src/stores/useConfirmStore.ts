import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface ConfirmOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDanger?: boolean;
}

export const useConfirmStore = defineStore('confirm', () => {
  const isOpen = ref(false);
  const options = ref<ConfirmOptions>({
    title: '',
    message: '',
    confirmText: 'ยืนยัน',
    cancelText: 'ยกเลิก',
    isDanger: false
  });

  // ตัวแปรเก็บฟังก์ชัน resolve ของ Promise
  const resolvePromise = ref<((value: boolean) => void) | null>(null);

  // ฟังก์ชันเรียกเปิด Modal (คืนค่าเป็น Promise<boolean>)
  const open = (newOptions: ConfirmOptions): Promise<boolean> => {
    options.value = { ...options.value, ...newOptions };
    isOpen.value = true;
    
    return new Promise((resolve) => {
      resolvePromise.value = resolve;
    });
  };

  const confirm = () => {
    isOpen.value = false;
    if (resolvePromise.value) resolvePromise.value(true);
  };

  const cancel = () => {
    isOpen.value = false;
    if (resolvePromise.value) resolvePromise.value(false);
  };

  return { isOpen, options, resolvePromise, open, confirm, cancel };
});