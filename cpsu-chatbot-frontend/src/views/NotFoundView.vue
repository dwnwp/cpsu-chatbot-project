<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 bg-gradient-mesh">
    <div class="text-center">
      <h1 class="text-[10rem] font-extrabold text-[#1A7662] opacity-10 leading-none animate-float select-none">404</h1>
      
      <h2 class="text-3xl font-bold text-gray-800 -mt-8 mb-3 animate-fade-in-up">ไม่พบหน้าที่ค้นหา</h2>
      <p class="text-gray-400 mb-8 max-w-md mx-auto animate-fade-in-up" style="animation-delay: 0.1s;">
        ขออภัยครับ ไม่พบหน้าที่คุณกำลังค้นหา อาจจะพิมพ์ URL ผิด หรือหน้านี้ถูกลบไปแล้ว
      </p>
      
      <router-link 
        to="/" 
        class="inline-flex items-center justify-center px-7 py-3 text-base font-semibold rounded-xl text-white transition-all hover:scale-105 animate-fade-in-up"
        style="background: linear-gradient(135deg, #1A7662, #2A9A80); box-shadow: 0 4px 14px rgba(26,118,98,0.3); animation-delay: 0.2s;"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        กลับไปหน้าเข้าสู่ระบบ
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>