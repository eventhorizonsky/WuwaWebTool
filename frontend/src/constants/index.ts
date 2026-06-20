import type { GradeInfo } from '@/types/character'

// ─── Attributes (element mapping) ───
export const ATTRIBUTES: Record<number, { name: string; color: string }> = {
  1: { name: '冷凝', color: '#3598db' },
  2: { name: '热熔', color: '#ba372a' },
  3: { name: '导电', color: '#b96ad9' },
  4: { name: '气动', color: '#169179' },
  5: { name: '衍射', color: '#f1c40f' },
  6: { name: '湮灭', color: '#843fa1' },
}

// ─── Weapon Types ───
export const WEAPON_TYPES: Record<number, string> = {
  1: '长刃',
  2: '迅刀',
  3: '佩枪',
  4: '臂铠',
  5: '音感仪',
}

// ─── Skill Order (for sorting) ───
export const SKILL_ORDER = [
  '常态攻击',
  '共鸣技能',
  '共鸣回路',
  '共鸣解放',
  '变奏技能',
  '延奏技能',
  '谐度破坏',
]

// ─── Chain Colors & Names ───
export const CHAIN_COLORS: Record<number, string> = {
  0: '#95a5a6',
  1: '#34495e',
  2: '#3598db',
  3: '#169179',
  4: '#b96ad9',
  5: '#cc8c00',
  6: '#ba372a',
}

export const CHAIN_NAMES = [
  '零链', '一链', '二链', '三链', '四链', '五链', '六链',
]

// ─── Standard Banner (non-UP) 5-star characters ───
export const STANDARD_BANNER_NAMES = ['维里奈', '安可', '凌阳', '鉴心', '卡卡罗']

// ─── Composite Grade Thresholds (total_grade * 250) ───
export const GRADE_THRESHOLDS: GradeInfo[] = [
  { min: 210, label: 'SSS', color: '#e63946' },
  { min: 195, label: 'SS', color: '#f4a261' },
  { min: 175, label: 'S', color: '#e9c46a' },
  { min: 150, label: 'A', color: '#b96ad9' },
  { min: 120, label: 'B', color: '#457b9d' },
  { min: 0, label: 'C', color: '#6b8e6e' },
]

export function getCompositeGrade(score: number): GradeInfo {
  for (const g of GRADE_THRESHOLDS) {
    if (score >= g.min) return g
  }
  return GRADE_THRESHOLDS[GRADE_THRESHOLDS.length - 1]
}

// ─── Per-Echo Grade Thresholds (0-50 scale) ───
export const ECHO_GRADES: GradeInfo[] = [
  { min: 41.7, label: 'SSS', color: '#e63946' },
  { min: 38.3, label: 'SS', color: '#f4a261' },
  { min: 35, label: 'S', color: '#e9c46a' },
  { min: 30, label: 'A', color: '#b96ad9' },
  { min: 24, label: 'B', color: '#457b9d' },
  { min: 0, label: 'C', color: '#6b8e6e' },
]

export function getEchoGrade(score: number): GradeInfo {
  for (const g of ECHO_GRADES) {
    if (score >= g.min) return g
  }
  return ECHO_GRADES[ECHO_GRADES.length - 1]
}

// ─── Substat Max/Min Values ───
export const SUBSTAT_MAX: Record<string, number> = {
  '暴击': 10.5,
  '暴击伤害': 21.0,
  '攻击%': 11.6,
  '生命%': 11.6,
  '防御%': 15.0,
  '共鸣效率': 12.4,
  '普攻伤害加成': 11.6,
  '重击伤害加成': 11.6,
  '共鸣技能伤害加成': 11.6,
  '共鸣解放伤害加成': 11.6,
  '治疗效果加成': 11.6,
}

export const SUBSTAT_MIN: Record<string, number> = {
  '暴击': 6.3,
  '暴击伤害': 12.6,
  '攻击%': 6.4,
  '生命%': 6.4,
  '防御%': 8.2,
  '共鸣效率': 6.8,
  '普攻伤害加成': 6.4,
  '重击伤害加成': 6.4,
  '共鸣技能伤害加成': 6.4,
  '共鸣解放伤害加成': 6.4,
  '治疗效果加成': 6.4,
}

// ─── Attribute Elements (for icon lookup) ───
export const ATTR_ELEMENTS = ['冷凝', '热熔', '导电', '气动', '衍射', '湮灭']

// ─── Helper: Weight to Color ───
export function weightColor(weight: number | null | undefined): string {
  if (weight == null) return '#888'
  if (weight >= 0.8) return '#ff6347'
  if (weight >= 0.5) return '#ffd700'
  if (weight >= 0.3) return '#c0c0c0'
  if (weight >= 0.1) return '#888'
  return '#555'
}

// ─── Helper: Substat Quality ───
export function substatQuality(
  name: string,
  valueStr: string
): { tier: string; color: string } {
  const v = parseFloat(valueStr) || 0
  const max = SUBSTAT_MAX[name]
  if (!max) return { tier: 'mid', color: '#c0c0c0' }
  const min = SUBSTAT_MIN[name] || max * 0.6
  const pct = (v - min) / (max - min)
  if (pct >= 0.9) return { tier: 'sss', color: '#ff4500' }
  if (pct >= 0.7) return { tier: 's', color: '#e9c46a' }
  if (pct >= 0.45) return { tier: 'a', color: '#b96ad9' }
  if (pct >= 0.2) return { tier: 'b', color: '#457b9d' }
  return { tier: 'c', color: '#6b8e6e' }
}
