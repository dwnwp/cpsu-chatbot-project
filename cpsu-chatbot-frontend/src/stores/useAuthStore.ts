import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/services/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ username: string } | null>(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(true);

  const verifySession = async () => {
    isLoading.value = true;
    try {
      const response = await apiClient.get('/v1/auth/verify'); 
      
      if (response.status === 200) {
        isAuthenticated.value = true;
      }
    } catch {
      isAuthenticated.value = false;
    } finally {
      isLoading.value = false;
    }
  };

  // ฟังก์ชัน Login
  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.post('/v1/auth/login', {
        username,
        password,
      })

      if (response.status === 200) {
        user.value = { username }
        isAuthenticated.value = true
        return { success: true, message: response.data.message }
      }
    } catch (error: any) {
      // จัดการ Error ตาม API Spec
      const message = error.response?.data?.message || 'Something went wrong'
      return { success: false, message }
    }
  }

  // ฟังก์ชัน Logout
  const logout = async () => {
    try {
      await apiClient.post('/v1/auth/logout')
    } finally {
      // เคลียร์ค่า State เสมอไม่ว่าจะยิง API สำเร็จหรือไม่
      user.value = null
      isAuthenticated.value = false
    }
  }

  const resetPassword = async (payload: {
    username: string
    password: string
    new_password: string
  }) => {
    try {
      const response = await apiClient.post('/v1/auth/password-reset', payload)
      if (response.status === 200) {
        return { success: true, message: response.data.message }
      }
    } catch (error: any) {
      const message = error.response?.data?.message || 'Cannot update password'
      return { success: false, message }
    }
  }

  return { user, isAuthenticated, login, logout, resetPassword, verifySession, isLoading }
})
