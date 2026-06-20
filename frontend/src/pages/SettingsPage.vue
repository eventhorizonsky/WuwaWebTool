<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'
import {
  getStoredAuth,
  storeAuth,
  clearAuth,
  isLoggedIn,
} from '@/composables/useApi'
import type { StoredAuth } from '@/types/auth'

type ToastFn = (msg: string, type: 'success' | 'error') => void
const toast = inject<ToastFn>('toast')

const router = useRouter()
const authStore = useAuthStore()
const charStore = useCharacterStore()

const currentAuth = ref<StoredAuth>(getStoredAuth())
const editToken = ref('')
const editDid = ref('')
const loading = ref(false)
const statusText = ref('')
const showToken = ref(false)

const loggedIn = computed(() => !!(currentAuth.value.token && currentAuth.value.did))
const maskedToken = computed(() => {
  const t = currentAuth.value.token || ''
  if (t.length <= 16) return t
  return t.slice(0, 8) + '...' + t.slice(-8)
})

onMounted(() => {
  refreshState()
})

function refreshState() {
  currentAuth.value = getStoredAuth()
  editToken.value = currentAuth.value.token || ''
  editDid.value = currentAuth.value.did || ''
  authStore.restoreFromStorage()
}

function doSave() {
  const token = editToken.value.trim()
  const did = editDid.value.trim()
  if (!token || !did) {
    statusText.value = 'Token 和 DID 不能为空'
    return
  }
  storeAuth(token, did, currentAuth.value.uid, currentAuth.value.bat)
  refreshState()
  statusText.value = '已保存'
  toast?.('Token 和 DID 已保存', 'success')
}

function doClear() {
  clearAuth()
  editToken.value = ''
  editDid.value = ''
  refreshState()
  statusText.value = '已清除所有认证信息'
}

async function doFetchAll() {
  if (!isLoggedIn()) {
    statusText.value = '请先保存 Token 和 DID'
    return
  }
  loading.value = true
  try {
    statusText.value = '正在获取角色列表...'
    await charStore.loadAll(true)
    refreshState()
    if (charStore.error) {
      statusText.value = '获取数据出错: ' + charStore.error
    } else {
      statusText.value = `数据获取完成，共 ${charStore.allChars.length} 个角色`
      toast?.('数据获取成功', 'success')
    }
  } catch (e: unknown) {
    statusText.value = '请求失败: ' + (e instanceof Error ? e.message : String(e))
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <header class="app-header">
    <h1 class="text-xl font-bold italic tracking-[1px] whitespace-nowrap flex-shrink-0" style="color: #d4b163">
      认证设置
    </h1>
    <div class="flex-1"></div>
    <button
      class="px-3 py-[5px] rounded-md border border-[var(--color-line)] bg-transparent text-[#e8edf2] text-xs cursor-pointer transition-all hover:bg-[var(--color-bg-card-hover)] hover:border-[#d4b163] whitespace-nowrap"
      @click="router.push({ name: 'index' })"
    >
      ← 返回首页
    </button>
  </header>

  <main class="app-container" style="overflow-y: auto;">
    <div class="max-w-[640px] mx-auto py-6 px-4 flex flex-col gap-5">

      <!-- Current status -->
      <div class="section-container">
        <div class="section-header">
          <span class="section-title">当前状态</span>
          <div class="section-deco-line"></div>
        </div>
        <div class="flex flex-col gap-3 text-sm">
          <div class="flex items-center gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0">状态:</span>
            <span v-if="loggedIn" class="text-[#2d6a4f] font-semibold">● 已配置</span>
            <span v-else class="text-[#c1121f] font-semibold">○ 未配置</span>
          </div>
          <div class="flex items-start gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0 pt-0.5">Token:</span>
            <code class="text-[#e8edf2] bg-black/30 px-2 py-0.5 rounded text-xs break-all flex-1">
              {{ currentAuth.token ? maskedToken : '(空)' }}
            </code>
            <button
              v-if="currentAuth.token"
              class="text-xs text-[#9aa0aa] hover:text-[#d4b163] flex-shrink-0"
              @click="showToken = !showToken"
            >
              {{ showToken ? '隐藏' : '显示' }}
            </button>
          </div>
          <div v-if="showToken" class="flex items-start gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0"></span>
            <code class="text-[#d4b163] bg-black/30 px-2 py-1 rounded text-xs break-all flex-1">
              {{ currentAuth.token }}
            </code>
          </div>
          <div class="flex items-start gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0 pt-0.5">DID:</span>
            <code class="text-[#e8edf2] bg-black/30 px-2 py-0.5 rounded text-xs break-all flex-1">
              {{ currentAuth.did || '(空)' }}
            </code>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0">UID:</span>
            <code class="text-[#e8edf2] bg-black/30 px-2 py-0.5 rounded text-xs">
              {{ currentAuth.uid || '(空)' }}
            </code>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[#9aa0aa] w-14 flex-shrink-0">BAT:</span>
            <code class="text-[#e8edf2] bg-black/30 px-2 py-0.5 rounded text-xs break-all flex-1">
              {{ currentAuth.bat ? maskedToken : '(空)' }}
            </code>
          </div>
        </div>
      </div>

      <!-- Edit token / did -->
      <div class="section-container">
        <div class="section-header">
          <span class="section-title">手动配置</span>
          <div class="section-deco-line"></div>
        </div>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-[#9aa0aa] uppercase tracking-[1px]">Token</label>
            <textarea
              v-model="editToken"
              rows="3"
              placeholder="在此粘贴 Token..."
              class="px-3 py-2 rounded-md bg-black/30 border border-[var(--color-line)] text-sm text-[#e8edf2] outline-none focus:border-[#d4b163] resize-y font-mono text-xs"
            ></textarea>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-[#9aa0aa] uppercase tracking-[1px]">DID (设备ID)</label>
            <input
              v-model="editDid"
              type="text"
              placeholder="在此粘贴 DID..."
              class="px-3 py-2 rounded-md bg-black/30 border border-[var(--color-line)] text-sm text-[#e8edf2] outline-none focus:border-[#d4b163] font-mono text-xs"
            />
          </div>
          <div class="flex gap-2 flex-wrap">
            <button
              class="px-4 py-2 rounded-md border font-semibold text-xs cursor-pointer transition-all bg-[#d4b163] text-[#0f1115] border-[#d4b163] hover:opacity-85"
              @click="doSave"
            >
              保存配置
            </button>
            <button
              class="px-4 py-2 rounded-md border border-[var(--color-line)] bg-transparent text-[#e8edf2] text-xs cursor-pointer transition-all hover:bg-[var(--color-bg-card-hover)] hover:border-[#d4b163]"
              @click="doClear"
            >
              清除全部
            </button>
          </div>
        </div>
      </div>

      <!-- Fetch data -->
      <div class="section-container">
        <div class="section-header">
          <span class="section-title">数据获取</span>
          <div class="section-deco-line"></div>
        </div>
        <div class="flex flex-col gap-3">
          <p class="text-xs text-[#9aa0aa]">
            保存 Token 和 DID 后，点击下方按钮逐步获取角色列表、刷新 BAT、拉取账号信息和角色数据。
          </p>
          <button
            class="px-4 py-2 rounded-md border font-semibold text-sm cursor-pointer transition-all bg-[#d4b163] text-[#0f1115] border-[#d4b163] hover:opacity-85 disabled:opacity-40 disabled:cursor-not-allowed self-start"
            :disabled="!loggedIn || loading"
            @click="doFetchAll"
          >
            {{ loading ? '获取中...' : '获取全部数据' }}
          </button>

          <!-- Status / loading -->
          <div v-if="loading" class="flex items-center gap-2 text-sm text-[#9aa0aa]">
            <div class="spinner" style="width:16px;height:16px;border-width:2px;"></div>
            {{ statusText }}
          </div>
          <div
            v-else-if="statusText"
            class="text-sm px-3 py-2 rounded-md"
            :class="statusText.includes('成功') ? 'bg-[#2d6a4f]/20 text-[#2d6a4f]' : 'bg-[#c1121f]/15 text-[#c1121f]'"
          >
            {{ statusText }}
          </div>
        </div>
      </div>

    </div>
  </main>
</template>
