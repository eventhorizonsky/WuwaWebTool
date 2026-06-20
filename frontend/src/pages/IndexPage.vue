<script setup lang="ts">
import { onMounted, inject } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import Sidebar from '@/components/index/Sidebar.vue'
import MainContent from '@/components/index/MainContent.vue'
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'

const authStore = useAuthStore()
const charStore = useCharacterStore()

type ToastFn = (msg: string, type: 'success' | 'error') => void
const toast = inject<ToastFn>('toast')

onMounted(async () => {
  // Handle login redirect — params are already consumed by the router guard.
  // The guard sets a session flag so we can show the success toast here.
  if (sessionStorage.getItem('wuwa_fresh_login') === '1') {
    sessionStorage.removeItem('wuwa_fresh_login')
    toast?.('登录成功！', 'success')
  }

  if (!authStore.loggedIn) {
    return
  }

  await charStore.loadAll(false)
})
</script>

<template>
  <AppHeader />

  <main class="app-container">
    <!-- Not logged in -->
    <div v-if="!authStore.loggedIn" class="text-center py-20 text-[#9aa0aa] text-base">
      请先登录查看角色面板
    </div>

    <!-- Loading -->
    <LoadingSpinner v-else-if="charStore.loading" />

    <!-- Error -->
    <div
      v-else-if="charStore.error"
      class="error-box"
      style="display:block;padding:12px 16px;"
      v-html="charStore.error"
    ></div>

    <!-- Main Layout -->
    <div v-else class="page-layout">
      <Sidebar />
      <MainContent />
    </div>
  </main>
</template>
