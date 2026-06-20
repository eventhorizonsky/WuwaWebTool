<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'

defineProps<{
  showBackLink?: boolean
  showExport?: boolean
}>()

const emit = defineEmits<{
  export: []
}>()

const router = useRouter()
const authStore = useAuthStore()
const charStore = useCharacterStore()

function goLogin() {
  window.location.href = '/login'
}

function doLogout() {
  authStore.logout()
  charStore.allChars = []
  charStore.roleAccounts = []
  charStore.accountInfo = null
  charStore.calabashData = null
}

function onAccountChange(event: Event) {
  const newUid = (event.target as HTMLSelectElement).value
  if (newUid && newUid !== String(authStore.auth.uid || '')) {
    authStore.setUid(newUid)
    charStore.loadAll(true)
  }
}

function goBack() {
  router.push({ name: 'index' })
}
</script>

<template>
  <header class="app-header">
    <!-- Row: navigation + branding (top row on mobile) -->
    <div class="header-brand-row">
      <!-- Back link -->
      <a
        v-if="showBackLink"
        href="#"
        class="text-sm text-[#9aa0aa] no-underline transition-colors hover:text-[#d4b163] flex-shrink-0"
        @click.prevent="goBack"
      >
        ← 返回
      </a>

      <!-- Title -->
      <h1 class="header-title text-xl font-bold italic tracking-[1px] whitespace-nowrap flex-shrink-0" style="color: #d4b163">
        <slot name="title">角色面板</slot>
      </h1>

      <!-- GitHub link -->
      <a
        href="https://github.com/eventhorizonsky/WuwaWebTool"
        target="_blank"
        title="WuwaWebTool on GitHub"
        class="text-[#9aa0aa] no-underline flex-shrink-0"
      >
        <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor" class="align-[-2px]">
          <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
        </svg>
      </a>

      <!-- Settings link -->
      <router-link
        to="/settings"
        title="认证设置"
        class="header-settings-link text-xs text-[#9aa0aa] no-underline flex-shrink-0 hover:text-[#d4b163] transition-colors flex items-center gap-1"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span class="hidden sm:inline">设置</span>
      </router-link>

      <!-- Attribution (hidden on small screens) -->
      <span class="header-attribution text-[10px] text-[#9aa0aa] flex-shrink-0">
        改自
        <a
          href="https://github.com/Loping151/XutheringWavesUID"
          target="_blank"
          class="text-[#9aa0aa]"
          title="XutheringWavesUID"
        >XutheringWavesUID</a>
      </span>
    </div>

    <!-- Row: actions (bottom row on mobile) -->
    <div class="header-actions-row">
      <!-- Account area (logged in) -->
      <div
        v-if="authStore.loggedIn"
        class="flex items-center gap-2 flex-1 justify-end md:justify-center"
      >
        <select
          class="header-account-select px-2.5 py-[5px] rounded-md bg-[var(--color-ink-1)] border border-[var(--color-line)] text-sm text-[#e8edf2] min-w-[180px] max-w-[280px] outline-none focus:border-[#d4b163]"
          :value="authStore.auth.uid || ''"
          @change="onAccountChange"
        >
          <option
            v-for="a in charStore.roleAccounts"
            :key="a.roleId"
            :value="String(a.roleId)"
          >
            {{ a.roleName || '漂泊者' }} — UID {{ a.roleId }}
          </option>
        </select>
        <button
          class="px-3 py-[5px] rounded-md border font-semibold text-xs cursor-pointer transition-all bg-[#d4b163] text-[#0f1115] border-[#d4b163] hover:opacity-85 whitespace-nowrap"
          @click="charStore.refreshAllData()"
        >
          刷新
        </button>
      </div>

      <!-- Export button (panel page) -->
      <button
        v-if="showExport"
        class="px-3 py-[5px] rounded-md border font-semibold text-xs cursor-pointer transition-all bg-[#d4b163] text-[#0f1115] border-[#d4b163] hover:opacity-85 whitespace-nowrap flex-shrink-0"
        @click="emit('export')"
      >
        导出图片
      </button>

      <!-- User area -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <span class="header-login-label text-xs text-[#9aa0aa]">
          {{ authStore.loggedIn ? '已登录' : '未登录' }}
        </span>
        <button
          v-if="!authStore.loggedIn"
          class="px-3 py-[5px] rounded-md border font-semibold text-xs cursor-pointer transition-all bg-[#d4b163] text-[#0f1115] border-[#d4b163] hover:opacity-85 whitespace-nowrap"
          @click="goLogin"
        >
          登录
        </button>
        <button
          v-else
          class="px-3 py-[5px] rounded-md border border-[var(--color-line)] bg-transparent text-[#e8edf2] text-xs cursor-pointer transition-all hover:bg-[var(--color-bg-card-hover)] hover:border-[#d4b163] whitespace-nowrap"
          @click="doLogout"
        >
          退出
        </button>
      </div>
    </div>
  </header>
</template>
