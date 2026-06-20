/**
 * WuwaWebTool Frontend API Client
 * Migrated from frontend/js/api.js
 */
import type { StoredAuth } from '@/types/auth'
import type { ApiResponse, RoleAccount, AccountInfo, CalabashData } from '@/types/api'
import type { CharacterEntry, CharacterDetail } from '@/types/character'
import type { ScoreData } from '@/types/scoring'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ─── Auth helpers ───
export function getStoredAuth(): StoredAuth {
  return {
    token: localStorage.getItem('wuwa_token'),
    did: localStorage.getItem('wuwa_did'),
    uid: localStorage.getItem('wuwa_uid'),
    bat: localStorage.getItem('wuwa_bat'),
  }
}

export function storeAuth(
  token: string | null,
  did: string | null,
  uid: string | null,
  bat: string | null
): void {
  if (token) localStorage.setItem('wuwa_token', token)
  if (did) localStorage.setItem('wuwa_did', did)
  if (uid) localStorage.setItem('wuwa_uid', uid)
  if (bat) localStorage.setItem('wuwa_bat', bat)
}

export function clearAuth(): void {
  ;['wuwa_token', 'wuwa_did', 'wuwa_uid', 'wuwa_bat'].forEach((k) =>
    localStorage.removeItem(k)
  )
}

export function isLoggedIn(): boolean {
  const { token, did } = getStoredAuth()
  return !!(token && did)
}

export function initFromUrlParams(): boolean {
  const p = new URLSearchParams(location.search)
  const t = p.get('token')
  const d = p.get('did')
  if (t && d) {
    storeAuth(t, d, null, null)
    history.replaceState({}, document.title, location.pathname)
    return true
  }
  return false
}

// ─── Cache helpers ───
const CP = 'wuwa_'

export function cacheGet<T = unknown>(key: string): T | null {
  try {
    const v = localStorage.getItem(CP + key)
    return v ? (JSON.parse(v) as T) : null
  } catch {
    return null
  }
}

export function cacheSet<T = unknown>(key: string, v: T): void {
  localStorage.setItem(CP + key, JSON.stringify(v))
}

export function cacheClear(): void {
  const AUTH = ['wuwa_token', 'wuwa_did', 'wuwa_uid', 'wuwa_bat']
  Object.keys(localStorage)
    .filter((k) => k.startsWith(CP) && !AUTH.includes(k))
    .forEach((k) => localStorage.removeItem(k))
}

export function cacheGetScore(charId: string): ScoreData | null {
  return cacheGet<ScoreData>('score_' + charId)
}

export function cacheSetScore(charId: string, data: ScoreData): void {
  cacheSet('score_' + charId, data)
}

// ─── API calls ───
export async function apiCall<T = unknown>(
  endpoint: string,
  body: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const r = await fetch(API_BASE + endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`API ${r.status}`)
  return r.json() as Promise<ApiResponse<T>>
}

export function authBody(): Record<string, string> {
  const { uid, token, did, bat } = getStoredAuth()
  return { uid: uid || '', token: token || '', did: did || '', bat: bat || '' }
}

export async function apiRefreshData(): Promise<ApiResponse> {
  return apiCall('/api/game/refresh', authBody())
}

export async function apiGetRoleList(): Promise<ApiResponse<RoleAccount[]>> {
  return apiCall('/api/game/role-list', authBody())
}

export async function apiGetRoleData(): Promise<ApiResponse<CharacterEntry[]>> {
  return apiCall('/api/game/role-data', authBody())
}

export async function apiRefreshBat(): Promise<ApiResponse & { bat?: string }> {
  const { uid, token, did } = getStoredAuth()
  const r = await apiCall<{ bat?: string }>('/api/login/refresh-bat', {
    uid: uid || '',
    token: token || '',
    did: did || '',
  })
  // bat is at the top level of the response, not inside data
  const bat = (r as unknown as Record<string, unknown>).bat as string | undefined
  if (r.success && bat) storeAuth(null, null, null, bat)
  return r
}

export async function apiGetRoleDetail(
  charId: string,
  forceRefresh?: boolean
): Promise<ApiResponse<CharacterDetail>> {
  const ck = 'roledetail_' + charId
  if (!forceRefresh) {
    const cached = cacheGet<ApiResponse<CharacterDetail>>(ck)
    if (cached) return cached
  }
  const r = await apiCall<CharacterDetail>('/api/game/role-detail/' + charId, authBody())
  if (r.success && r.data) cacheSet(ck, r)
  return r
}

export async function apiGetBaseData(): Promise<ApiResponse<AccountInfo>> {
  return apiCall('/api/game/base-data', authBody())
}

export async function apiGetCalabash(): Promise<ApiResponse<CalabashData>> {
  return apiCall('/api/game/calabash', authBody())
}

export async function apiGetRoleDetailBatch(
  charIds: string[]
): Promise<ApiResponse<CharacterDetail[]>> {
  const { uid, token, did, bat } = getStoredAuth()
  return apiCall('/api/game/role-detail-batch', {
    uid: uid || '',
    token: token || '',
    did: did || '',
    bat: bat || '',
    char_ids: charIds,
  })
}

export async function apiScoreCharacter(
  charId: string,
  roleData: CharacterDetail
): Promise<ApiResponse<ScoreData>> {
  return apiCall('/api/score/character', {
    uid: getStoredAuth().uid,
    token: getStoredAuth().token,
    char_id: charId,
    role_data: roleData,
  })
}

export async function apiScoreBatch(
  charIds: string[]
): Promise<ApiResponse<ScoreData[]>> {
  const { uid, token, did, bat } = getStoredAuth()
  return apiCall('/api/score/batch', {
    uid: uid || '',
    token: token || '',
    did: did || '',
    bat: bat || '',
    char_ids: charIds,
  })
}

// ─── Combined: load character detail + score with per-character caching ───
export async function loadCharDetailAndScore(
  charId: string,
  forceRefresh?: boolean
): Promise<{ detail: CharacterDetail; score: ScoreData | null }> {
  if (!forceRefresh) {
    const cachedDetailResp = cacheGet<ApiResponse<CharacterDetail>>('roledetail_' + charId)
    const cachedScore = cacheGetScore(charId)
    if (cachedDetailResp?.data && cachedScore) {
      return { detail: cachedDetailResp.data, score: cachedScore }
    }
  }

  const detailResp = await apiGetRoleDetail(charId, forceRefresh)
  if (!detailResp.success || !detailResp.data) {
    throw new Error(detailResp.msg || '获取角色详情失败')
  }

  const scoreResp = await apiScoreCharacter(charId, detailResp.data)
  let scoreData: ScoreData | null = null
  if (scoreResp.success && scoreResp.data) {
    scoreData = scoreResp.data
    cacheSetScore(charId, scoreData)
  }

  return { detail: detailResp.data, score: scoreData }
}

// ─── Hydrate a role list entry from per-character caches ───
export function hydrateCharFromCache(entry: CharacterEntry): boolean {
  const cid = String(entry.roleId || entry.role?.roleId || '')
  if (!cid) return false
  let changed = false

  const cachedDetailResp = cacheGet<ApiResponse<CharacterDetail>>('roledetail_' + cid)
  if (cachedDetailResp?.data && !entry._detail) {
    entry._detail = cachedDetailResp.data
    changed = true
  }

  const cachedScore = cacheGetScore(cid)
  if (cachedScore != null && entry._score == null) {
    entry._score = cachedScore.total_score || 0
    entry._grade = getCompositeGradeFromCache(entry._score)
    changed = true
  }

  return changed
}

// Re-exported here for hydration use
import { getCompositeGrade } from '@/constants'

function getCompositeGradeFromCache(score: number) {
  return getCompositeGrade(score)
}
