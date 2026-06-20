<script setup lang="ts">
import { ref, onMounted, inject, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import CharListSidebar from '@/components/panel/CharListSidebar.vue'
import PanelMain from '@/components/panel/PanelMain.vue'
import { useAuthStore } from '@/stores/auth'
import { useCharacterStore } from '@/stores/character'
import { isLoggedIn, cacheGetScore } from '@/composables/useApi'
import { getCompositeGrade } from '@/constants'
import type { ScoreData, EchoGradeData } from '@/types/scoring'

type ToastFn = (msg: string, type: 'success' | 'error') => void
const toast = inject<ToastFn>('toast')

const route = useRoute()
const authStore = useAuthStore()
const charStore = useCharacterStore()

const charId = ref(route.query.charId as string || '')
const loading = ref(true)
const error = ref('')
const echoGrades = ref<Record<number, EchoGradeData>>({})
const subWeights = ref<Record<string, number>>({})
const mainWeights = ref<Record<string, number>>({})

const exportAreaRef = ref<HTMLElement | null>(null)

onMounted(async () => {
  authStore.restoreFromStorage()
  if (!isLoggedIn()) {
    error.value = '请先<a href="/login" style="color:#d4b163">登录</a>'
    loading.value = false
    return
  }
  await initPanel()
})

async function initPanel() {
  loading.value = true
  try {
    // Load role list from cache
    if (charStore.allChars.length === 0) {
      await charStore.loadAll(false)
    }

    if (!charId.value) {
      error.value = '未指定角色ID'
      loading.value = false
      return
    }

    await charStore.loadCharacterDetail(charId.value, false)
    if (charStore.currentScoreData) {
      displayScore(charStore.currentScoreData)
    }
  } catch (e: unknown) {
    error.value = '初始化失败: ' + (e instanceof Error ? e.message : String(e))
  }
  loading.value = false
}

async function switchCharacter(newCharId: string) {
  if (newCharId === charId.value) return
  charId.value = newCharId
  charStore.currentCharDetail = null
  charStore.currentScoreData = null
  echoGrades.value = {}
  subWeights.value = {}
  mainWeights.value = {}

  const url = new URL(location.href)
  url.hash = '#/panel?charId=' + newCharId
  history.pushState({}, '', url)

  loading.value = true
  try {
    await charStore.loadCharacterDetail(newCharId, false)
    if (charStore.currentScoreData) {
      displayScore(charStore.currentScoreData)
    }
  } catch (e: unknown) {
    error.value = '加载失败: ' + (e instanceof Error ? e.message : String(e))
  }
  loading.value = false
}

function displayScore(data: ScoreData) {
  subWeights.value = data.sub_weights || {}
  mainWeights.value = data.main_weights || {}

  const grades: Record<number, EchoGradeData> = {}
  if (data.phantoms) {
    data.phantoms.forEach((p, i) => {
      grades[i] = {
        grade: p.grade || 'c',
        score: p.score,
        substat_scores: data.substat_scores?.[i] || [],
      }
    })
  }
  echoGrades.value = grades
}

async function handleExport() {
  try {
    await nextTick()
    const html2canvas = (await import('html2canvas')).default
    const el = exportAreaRef.value
    if (!el) return
    const canvas = await html2canvas(el, {
      backgroundColor: '#0f1923',
      scale: 2,
      useCORS: true,
      allowTaint: true,
    })
    const a = document.createElement('a')
    a.download = 'wuwa-panel-' + charId.value + '.png'
    a.href = canvas.toDataURL()
    a.click()
    toast?.('已导出', 'success')
  } catch {
    toast?.('导出失败', 'error')
  }
}

async function refreshCurrentCharacter() {
  if (!charId.value) return
  loading.value = true
  try {
    localStorage.removeItem('wuwa_roledetail_' + charId.value)
    localStorage.removeItem('wuwa_score_' + charId.value)
    await charStore.loadCharacterDetail(charId.value, true)
    if (charStore.currentScoreData) {
      displayScore(charStore.currentScoreData)
    }
    toast?.('角色数据已刷新', 'success')
  } catch {
    toast?.('刷新失败', 'error')
  }
  loading.value = false
}
</script>

<template>
  <AppHeader
    :show-back-link="true"
    :show-export="true"
    @export="handleExport"
  >
    <template #title>
      {{ charStore.currentCharDetail?.role?.roleName || charStore.currentCharDetail?.roleName || '角色面板' }}
    </template>
  </AppHeader>

  <main class="app-container">
    <!-- Error -->
    <div v-if="error" class="error-box" style="display:block;margin:12px 0;" v-html="error"></div>

    <!-- Loading -->
    <LoadingSpinner v-else-if="loading" />

    <!-- Panel Content -->
    <div v-else id="exportArea" ref="exportAreaRef">
      <div class="panel-page">
        <CharListSidebar
          :characters="charStore.allChars"
          :current-char-id="charId"
          @switch="switchCharacter"
        />
        <PanelMain
          :role-detail="charStore.currentCharDetail?._detail || null"
          :score-data="charStore.currentScoreData"
          :echo-grades="echoGrades"
          :char-id="charId"
          @refresh="refreshCurrentCharacter"
        />
      </div>
    </div>
  </main>
</template>
