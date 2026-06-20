/** Generic API response wrapper */
export interface ApiResponse<T = unknown> {
  success: boolean
  msg?: string
  data?: T
}

/** Role list entry from /api/game/role-list */
export interface RoleAccount {
  roleId: number
  roleName: string
}

/** Role list response */
export interface RoleListResponse {
  roleList: RoleAccount[]
  list?: RoleAccount[]
}

/** Treasure box item in account info */
export interface TreasureBoxItem {
  id: number
  name: string
  num: number
}

/** Base data response (account info) from /api/game/base-data */
export interface AccountInfo {
  id?: number
  name?: string
  level?: number
  worldLevel?: number
  creatTime?: number
  activeDays?: number
  roleNum?: number
  achievementCount?: number
  achievementStar?: number
  smallCount?: number
  bigCount?: number
  treasureBoxList?: TreasureBoxItem[]
}

/** Calabash (data dock) response */
export interface CalabashData {
  isUnlock: boolean
  level: number
}
