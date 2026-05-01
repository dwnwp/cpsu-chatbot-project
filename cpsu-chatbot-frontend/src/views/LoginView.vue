<template>
  <div class="min-h-screen flex login-page">
    <!-- Left Panel: Form -->
    <div class="w-full md:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-24 relative bg-gradient-mesh">
      <!-- Logo -->
      <div class="absolute top-8 left-8 animate-fade-in">
        <img src="@/assets/logo/su-logo.svg" alt="Silpakorn University" class="h-16" />
      </div>

      <div class="max-w-md w-full mx-auto mt-16">
        <h1 class="text-4xl font-extrabold mb-2 animate-fade-in-up">
          <span class="text-amber-500">CP</span><span class="text-[#1A7662]">SU CHATBOT</span>
        </h1>
        <p class="text-gray-400 text-sm mb-8 animate-fade-in-up" style="animation-delay: 0.1s;">ระบบจัดการข้อมูลอัจฉริยะ สำหรับผู้ดูแลระบบ</p>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div
            v-if="errorMessage"
            class="p-3.5 bg-red-50 text-red-600 rounded-xl text-sm text-center border border-red-100 animate-fade-in"
          >
            {{ errorMessage }}
          </div>

          <div class="animate-fade-in-up" style="animation-delay: 0.15s;">
            <label for="username" class="block text-sm font-semibold text-gray-500 mb-1.5">Username</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              autocomplete="off"
              required
              class="login-input"
              placeholder="กรอกชื่อผู้ใช้"
            />
          </div>

          <div class="animate-fade-in-up" style="animation-delay: 0.2s;">
            <label for="password" class="block text-sm font-semibold text-gray-500 mb-1.5">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="login-input"
              placeholder="กรอกรหัสผ่าน"
            />
          </div>

          <div class="flex items-center justify-end text-sm animate-fade-in-up" style="animation-delay: 0.25s;">
            <a
              href="#"
              @click.prevent="openResetPassword"
              class="text-[#1A7662] font-medium hover:text-teal-800 transition-colors hover:underline"
            >
              เปลี่ยนรหัสผ่าน?
            </a>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="login-btn animate-fade-in-up"
            style="animation-delay: 0.3s;"
          >
            <svg
              v-if="isLoading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Right Panel: Decorative -->
    <div class="hidden md:flex md:w-1/2 flex-col justify-center items-center text-white p-12 relative overflow-hidden login-right-panel">
      <!-- Floating decorative shapes -->
      <div class="absolute top-[10%] left-[10%] w-32 h-32 rounded-full bg-white/5 animate-float"></div>
      <div class="absolute bottom-[15%] right-[12%] w-24 h-24 rounded-2xl bg-white/5 animate-float" style="animation-delay: 1.5s;"></div>
      <div class="absolute top-[60%] left-[5%] w-16 h-16 rounded-full bg-white/[0.03] animate-float" style="animation-delay: 2.5s;"></div>
      <div class="absolute top-[20%] right-[20%] w-20 h-20 rounded-xl rotate-12 bg-white/[0.04] animate-float" style="animation-delay: 0.8s;"></div>

      <img
        src="@/assets/logo/bot-logo.png"
        alt="Chatbot Graphic"
        class="w-52 h-52 object-contain mb-6 animate-float drop-shadow-2xl"
      />

      <h2 class="text-3xl font-bold mb-2 tracking-wide animate-fade-in-up" style="animation-delay: 0.3s;">จัดการข้อมูลแชทบอท</h2>
      <p class="text-teal-200/80 text-lg animate-fade-in-up" style="animation-delay: 0.4s;">ภาควิชาคอมพิวเตอร์ มหาวิทยาลัยศิลปากร</p>
    </div>

    <ResetPasswordModal :isOpen="isResetModalOpen" @close="isResetModalOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import ResetPasswordModal from '@/components/ResetPasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()

// State สำหรับฟอร์ม
const form = reactive({
  username: '',
  password: '',
  remember: false,
})

const isLoading = ref(false)
const errorMessage = ref('')
const isResetModalOpen = ref(false)

// จัดการเมื่อกดปุ่ม Login
const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true

  const result = await authStore.login(form.username, form.password)

  if (result?.success) {
    router.push({ name: 'Knowledge' })
  } else {
    // แสดง Error
    errorMessage.value = result?.message || 'Login failed. Please try again.'
  }

  isLoading.value = false
}

// จัดการการเปิด Modal/หน้าต่าง สำหรับ Reset Password
const openResetPassword = () => {
  isResetModalOpen.value = true
}
</script>

<style scoped>
.login-right-panel {
  background: linear-gradient(135deg, #1A7662 0%, #0F5A4A 40%, #134E3F 70%, #1A7662 100%);
  background-size: 200% 200%;
  animation: gradientShift 8s ease-in-out infinite;
}

.login-input {
  width: 100%;
  padding: 0.7rem 1rem;
  border: 1.5px solid #E8E6E1;
  border-radius: 12px;
  outline: none;
  transition: all 0.2s ease;
  background: #FAFAF9;
  font-size: 0.9rem;
}
.login-input:focus {
  border-color: #1A7662;
  box-shadow: 0 0 0 3px rgba(26, 118, 98, 0.12);
  background: #fff;
}

.login-btn {
  width: 100%;
  background: linear-gradient(135deg, #1A7662, #2A9A80);
  color: white;
  font-weight: 700;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.25s ease;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(26, 118, 98, 0.25);
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(26, 118, 98, 0.35);
}
.login-btn:active:not(:disabled) {
  transform: translateY(0);
}
.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
