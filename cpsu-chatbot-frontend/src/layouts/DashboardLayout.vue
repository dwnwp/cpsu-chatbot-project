<template>
  <div class="flex h-screen font-sans" style="background-color: var(--color-bg);">
    <!-- Sidebar -->
    <aside class="w-64 flex flex-col bg-sidebar-gradient border-r" style="border-color: var(--color-border);">
      <div class="h-20 flex items-center px-6 border-b" style="border-color: var(--color-border);">
        <img src="@/assets/logo/su-logo.svg" alt="Logo" class="h-10 w-10 mr-3" />
        <div>
          <h1 class="font-bold text-[#1A7662] leading-tight flex flex-col">
            <span class="text-amber-500 text-sm">CPSU CHATBOT</span> Management
          </h1>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto py-6">
        <div class="px-6 mb-4 text-xs font-bold text-gray-400 uppercase tracking-wider">หมวดหมู่{{ title }} :</div>
        <ul class="space-y-1.5 px-3 stagger-list">
          <li v-for="menu in menus" :key="menu" class="animate-fade-in-up">
            <button 
              @click="$emit('update:activeMenu', menu)"
              :class="['sidebar-menu-item',
                activeMenu === menu ? 'sidebar-menu-active' : 'sidebar-menu-inactive'
              ]"
            >
              <div class="flex justify-center w-full">{{ menu }}</div>
            </button>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col h-screen overflow-hidden">
      <header class="h-16 bg-white flex items-center justify-between px-8 shrink-0 shadow-sm" style="border-bottom: 1px solid var(--color-border);">
        <div class="flex space-x-6">
          <router-link to="/knowledge" :class="[route.path.includes('/knowledge') ? 'nav-link-active' : 'nav-link-inactive', 'nav-link']">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            จัดการฐานความรู้แชทบอท
          </router-link>
          
          <router-link to="/images" :class="[route.path.includes('/images') ? 'nav-link-active' : 'nav-link-inactive', 'nav-link']">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            จัดการรูปภาพ
          </router-link>
        </div>
        
        <button @click="handleLogout" class="flex items-center text-red-500 hover:text-red-700 text-sm font-semibold transition-colors cursor-pointer group">
          <img src="@/assets/logout.svg" class="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" alt="logout icon" />
          ออกจากระบบ
        </button>
      </header>

      <div class="flex-1 overflow-auto p-8">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { useConfirmStore } from '@/stores/useConfirmStore';

const confirmStore = useConfirmStore();

// รับค่า Props เพื่อเปลี่ยน UI Sidebar ตามหน้า
defineProps<{
  title: string;
  menus: string[];
  activeMenu: string;
}>();

defineEmits(['update:activeMenu']);

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const handleLogout = async () => {
    const isConfirmed = await confirmStore.open({
        title: 'ยืนยันการออกจากระบบ',
        message: `คุณต้องการออกจากระบบใช่หรือไม่?`,
        confirmText: 'logout',
        isDanger: true
    });
    if (!isConfirmed) return;
    await authStore.logout();
    router.push('/');
};
</script>

<style scoped>
.sidebar-menu-item {
  width: 100%;
  text-align: left;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.sidebar-menu-active {
  background: linear-gradient(135deg, #1A7662, #2A9A80);
  color: white;
  box-shadow: 0 4px 12px rgba(26, 118, 98, 0.3);
}

.sidebar-menu-inactive {
  color: #6B6B6B;
}
.sidebar-menu-inactive:hover {
  background-color: rgba(26, 118, 98, 0.06);
  color: #1A7662;
}

.nav-link {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}

.nav-link-active {
  color: #1A7662;
  border-bottom-color: #1A7662;
}

.nav-link-inactive {
  color: #9C9C9C;
}
.nav-link-inactive:hover {
  color: #6B6B6B;
}
</style>