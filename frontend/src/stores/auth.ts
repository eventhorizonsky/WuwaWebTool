import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getStoredAuth,
  storeAuth,
  clearAuth,
  cacheClear,
  initFromUrlParams,
} from '@/composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const auth = ref(getStoredAuth())

  const loggedIn = computed(() => !!(auth.value.token && auth.value.did))

  function restoreFromStorage() {
    auth.value = getStoredAuth()
  }

  function login(token: string, did: string) {
    storeAuth(token, did, null, null)
    auth.value = getStoredAuth()
  }

  function logout() {
    clearAuth()
    cacheClear()
    auth.value = { token: null, did: null, uid: null, bat: null }
  }

  function setUid(uid: string) {
    storeAuth(null, null, uid, null)
    auth.value = getStoredAuth()
  }

  function initFromUrl() {
    const handled = initFromUrlParams()
    if (handled) {
      auth.value = getStoredAuth()
    }
    return handled
  }

  return {
    auth,
    loggedIn,
    restoreFromStorage,
    login,
    logout,
    setUid,
    initFromUrl,
  }
})
