/** Resource URL helpers for game assets */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export function getResourceUrl(type: string, filename: string): string {
  return API_BASE + '/static/resource/' + type + '/' + filename
}

export function getTextureUrl(sub: string, name: string): string {
  return '/assets/textures/texture2d/' + sub + '/' + name
}

export function getAttrIcon(attrName: string): string {
  return getTextureUrl('attribute', 'attr_' + attrName + '.png')
}

export function getWeaponTypeIcon(typeName: string): string {
  return getTextureUrl('weapon_type', 'weapon_type_' + typeName + '.png')
}

export function getAttrEffectIcon(name: string): string {
  return getTextureUrl('attribute_effect', 'attr_' + name + '.png')
}
