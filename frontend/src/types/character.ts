/** Lightweight character entry used in role list and grid */
export interface CharacterEntry {
  roleId?: number
  roleName?: string
  starLevel?: number
  attributeId?: number
  weaponTypeId?: number
  level?: number
  chainUnlockNum?: number
  _score: number | null
  _grade: GradeInfo | null
  _detail: CharacterDetail | null
  role?: RoleInfo
}

/** Full character detail from /api/game/role-detail/:id */
export interface CharacterDetail {
  role?: RoleInfo
  roleId?: number
  roleName?: string
  starLevel?: number
  attributeId?: number
  weaponTypeId?: number
  chain?: number
  level?: number
  chainList?: ChainItem[]
  roleSkin?: RoleSkin
  weaponData?: WeaponData
  skillList?: SkillItem[]
  skillBranchList?: SkillBranch[]
  activeBranchId?: number
  roleAttributeList?: AttributeItem[]
  equipPhantomAddPropList?: AttributeItem[]
  phantomData?: PhantomData
  attributeList?: AttributeItem[]
}

export interface RoleInfo {
  roleId?: number
  roleName?: string
  starLevel?: number
  attributeId?: number
  weaponTypeId?: number
  chain?: number
  level?: number
  attributeList?: AttributeItem[]
}

export interface ChainItem {
  unlocked: boolean
}

export interface RoleSkin {
  skinIcon?: string
  skinName?: string
  qualityName?: string
}

export interface WeaponData {
  weapon: WeaponInfo
  level: number
  resonLevel: number
  mainPropList?: AttributeItem[]
}

export interface WeaponInfo {
  weaponId?: number
  weaponName?: string
  weaponStarLevel?: number
  weaponEffectName?: string
  effectDescription?: string
}

export interface SkillItem {
  skill?: SkillDetail
  level?: number
}

export interface SkillDetail {
  type?: string
  name?: string
  iconUrl?: string
  description?: string
}

export interface SkillBranch {
  branchId?: number
  branchName?: string
  skillIcon?: string
  desc?: string
}

export interface AttributeItem {
  attributeName: string
  attributeValue: string
  iconUrl?: string
}

export interface PhantomData {
  equipPhantomList?: EchoData[]
  cost?: number
}

export interface EchoData {
  phantomProp?: EchoProp
  cost?: number
  level?: number
  mainProps?: EchoStat[]
  subProps?: EchoStat[]
  fetterDetail?: FetterDetail
}

export interface EchoProp {
  phantomId?: number
  name?: string
}

export interface EchoStat {
  attributeName: string
  attributeValue: string
}

export interface FetterDetail {
  name: string
  firstDescription?: string
  secondDescription?: string
  tripleDescription?: string
}

export interface GradeInfo {
  min: number
  label: string
  color: string
}
