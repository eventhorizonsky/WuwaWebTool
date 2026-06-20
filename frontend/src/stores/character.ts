import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CharacterEntry } from '@/types/character'
import type { RoleAccount, AccountInfo, CalabashData } from '@/types/api'
import type { ScoreData } from '@/types/scoring'
import {
  apiGetRoleList,
  apiGetRoleData,
  apiGetBaseData,
  apiGetCalabash,
  apiRefreshData,
  apiRefreshBat,
  getStoredAuth,
  storeAuth,
  cacheGet,
  cacheSet,
  cacheClear,
  hydrateCharFromCache,
  loadCharDetailAndScore,
} from '@/composables/useApi'
import { getCompositeGrade } from '@/constants'
import { useAuthStore } from './auth'

export const useCharacterStore = defineStore('character', () => {
  // State
  const allChars = ref<CharacterEntry[]>([])
  const roleAccounts = ref<RoleAccount[]>([])
  const accountInfo = ref<AccountInfo | null>(null)
  const calabashData = ref<CalabashData | null>(null)
  const currentCharDetail = ref<CharacterEntry | null>(null)
  const currentScoreData = ref<ScoreData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const sortMode = ref<'score' | 'level' | 'element'>('score')

  // Computed
  const filteredChars = computed(() => {
    let list = [...allChars.value]
    const q = searchQuery.value.toLowerCase()
    if (q) {
      list = list.filter((r) =>
        (r.roleName || r.role?.roleName || '').toLowerCase().includes(q)
      )
    }
    if (sortMode.value === 'score') {
      list.sort((a, b) => (b._score ?? -1) - (a._score ?? -1))
    } else if (sortMode.value === 'level') {
      list.sort(
        (a, b) => (b.level || b.role?.level || 0) - (a.level || a.role?.level || 0)
      )
    } else {
      list.sort(
        (a, b) =>
          (a.attributeId || a.role?.attributeId || 0) -
          (b.attributeId || b.role?.attributeId || 0)
      )
    }
    return list
  })

  const hasData = computed(() => allChars.value.length > 0)

  // Actions
  function populateAccountSelect() {
    const authStore = useAuthStore()
    const curUid = authStore.auth.uid
    if (!curUid && roleAccounts.value.length > 0) {
      const first = roleAccounts.value[0]
      storeAuth(null, null, String(first.roleId), null)
      authStore.restoreFromStorage()
    }
  }

  async function loadAll(force = false) {
    loading.value = true
    error.value = null

    try {
      // Restore from cache first
      if (!force) {
        const cachedAccounts = cacheGet<RoleAccount[]>('roleAccounts')
        if (cachedAccounts && cachedAccounts.length > 0) {
          roleAccounts.value = cachedAccounts
          populateAccountSelect()
        }
        const c = cacheGet<CharacterEntry[]>('roleList')
        if (c && c.length > 0) allChars.value = c
        const acct = cacheGet<AccountInfo>('accountInfo')
        if (acct) accountInfo.value = acct
        const cala = cacheGet<CalabashData>('calabashData')
        if (cala) calabashData.value = cala
      }

      // Fetch role accounts if not cached
      if (roleAccounts.value.length === 0) {
        try {
          const r = await apiGetRoleList()
          if (r.success && r.data) {
            // API may return { data: [...] } or { data: { roleList: [...], list: [...] } }
            const rd = r.data as unknown as Record<string, unknown>
            let rl: RoleAccount[] = []
            if (Array.isArray(r.data)) {
              rl = r.data as unknown as RoleAccount[]
            } else if (Array.isArray(rd.roleList)) {
              rl = rd.roleList as unknown as RoleAccount[]
            } else if (Array.isArray(rd.list)) {
              rl = rd.list as unknown as RoleAccount[]
            }
            if (rl.length > 0) {
              roleAccounts.value = rl
              cacheSet('roleAccounts', rl)
              populateAccountSelect()
              if (!getStoredAuth().uid) {
                const gu = String(rl[0].roleId || '')
                if (gu) {
                  storeAuth(null, null, gu, null)
                  useAuthStore().restoreFromStorage()
                }
              }
            }
          }
        } catch {
          // Non-fatal
        }
        if (!getStoredAuth().uid) {
          error.value = '未能获取游戏角色，请重新登录'
          loading.value = false
          return
        }
      }

      // Refresh BAT if empty (required for game data API calls)
      if (!getStoredAuth().bat) {
        try { await apiRefreshBat() } catch { /* non-fatal */ }
      }

      // Fetch account info + calabash
      if (!accountInfo.value || !calabashData.value || force) {
        const [br, cr] = await Promise.allSettled([
          apiGetBaseData(),
          apiGetCalabash(),
        ])
        if (br.status === 'fulfilled' && br.value.success && br.value.data) {
          accountInfo.value = br.value.data
          cacheSet('accountInfo', br.value.data)
        }
        if (cr.status === 'fulfilled' && cr.value.success && cr.value.data) {
          calabashData.value = cr.value.data
          cacheSet('calabashData', cr.value.data)
        }
      }

      // Hydrate cached scores/details
      if (allChars.value.length > 0 && !force) {
        let anyHydrated = false
        for (const r of allChars.value) {
          if (hydrateCharFromCache(r)) anyHydrated = true
        }
        if (anyHydrated) cacheSet('roleList', allChars.value)
        loading.value = false
        return
      }

      // Full load
      if (force) await apiRefreshBat()

      const rr = await apiGetRoleData()
      if (!rr.success) throw new Error(rr.msg || '获取角色数据失败')
      // API returns { data: { roleList: [...] } } — extract roleList from the nested structure
      const rawData = rr.data as unknown as Record<string, unknown>
      let rl: CharacterEntry[] = []
      if (rawData && Array.isArray((rawData as { roleList?: unknown }).roleList)) {
        rl = (rawData as { roleList: CharacterEntry[] }).roleList
      } else if (Array.isArray(rr.data)) {
        rl = rr.data as unknown as CharacterEntry[]
      }
      if (!rl || !rl.length) {
        loading.value = false
        return
      }

      // Initialize scores/details
      for (const r of rl) {
        r._score = null
        r._grade = null
        r._detail = null
      }

      // Sort by level descending
      rl.sort((a, b) => (b.level || b.role?.level || 0) - (a.level || a.role?.level || 0))
      allChars.value = rl
      cacheSet('roleList', rl)

      // Hydrate from caches
      let anyHydrated = false
      for (const r of allChars.value) {
        if (hydrateCharFromCache(r)) anyHydrated = true
      }
      if (anyHydrated) cacheSet('roleList', allChars.value)
    } catch (e: unknown) {
      error.value = '加载失败: ' + (e instanceof Error ? e.message : String(e))
    }
    loading.value = false
  }

  async function loadCharacterDetail(charId: string, forceRefresh = false) {
    try {
      const { detail, score } = await loadCharDetailAndScore(charId, forceRefresh)
      if (!detail) throw new Error('未找到角色数据')

      // Find and update entry in allChars
      const entry: CharacterEntry = {
        roleId: parseInt(charId),
        role: detail.role,
        level: detail.level,
        _detail: detail,
        _score: score?.total_score ?? null,
        _grade: score ? getCompositeGrade(score.total_score) : null,
      }
      currentCharDetail.value = entry
      currentScoreData.value = score

      // Update in allChars
      const idx = allChars.value.findIndex(
        (r) => String(r.roleId || r.role?.roleId || '') === charId
      )
      if (idx >= 0) {
        allChars.value[idx]._detail = detail
        allChars.value[idx]._score = score?.total_score ?? null
        allChars.value[idx]._grade = score ? getCompositeGrade(score.total_score) : null
      }

      return entry
    } catch (e: unknown) {
      error.value = '加载角色失败: ' + (e instanceof Error ? e.message : String(e))
      throw e
    }
  }

  async function refreshCharacter(charId: string) {
    // Clear caches
    localStorage.removeItem('wuwa_roledetail_' + charId)
    localStorage.removeItem('wuwa_score_' + charId)
    await loadCharacterDetail(charId, true)
  }

  async function refreshAllData() {
    const authStore = useAuthStore()
    if (!authStore.auth.uid) {
      error.value = '请先选择账号'
      return
    }
    loading.value = true
    try {
      await apiRefreshData()
      cacheClear()
      accountInfo.value = null
      calabashData.value = null
      allChars.value = []
      roleAccounts.value = []
      await loadAll(true)
    } catch (e: unknown) {
      error.value = '刷新失败: ' + (e instanceof Error ? e.message : String(e))
    }
    loading.value = false
  }

  return {
    // State
    allChars,
    roleAccounts,
    accountInfo,
    calabashData,
    currentCharDetail,
    currentScoreData,
    loading,
    error,
    searchQuery,
    sortMode,
    // Computed
    filteredChars,
    hasData,
    // Actions
    loadAll,
    loadCharacterDetail,
    refreshCharacter,
    refreshAllData,
    populateAccountSelect,
  }
})
