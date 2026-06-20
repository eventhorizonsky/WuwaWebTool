import { createRouter, createWebHashHistory } from 'vue-router'
import { isLoggedIn, storeAuth } from '@/composables/useApi'

const routes = [
  {
    path: '/',
    name: 'index',
    component: () => import('@/pages/IndexPage.vue'),
  },
  {
    path: '/panel',
    name: 'panel',
    component: () => import('@/pages/PanelPage.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from) => {
  // Handle login redirect: token/did may be in the hash query or in location.search
  const extractParams = (): { token: string; did: string } | null => {
    // Hash-mode query params (e.g. /#/?token=xxx&did=xxx)
    const hToken = to.query.token as string | undefined
    const hDid = to.query.did as string | undefined
    if (hToken && hDid) return { token: hToken, did: hDid }

    // Query params before the hash (e.g. /?token=xxx&did=xxx#/)
    const sp = new URLSearchParams(window.location.search)
    const sToken = sp.get('token')
    const sDid = sp.get('did')
    if (sToken && sDid) return { token: sToken, did: sDid }

    return null
  }

  const params = extractParams()
  if (params) {
    storeAuth(params.token, params.did, null, null)
    // Signal to IndexPage that login was just completed
    sessionStorage.setItem('wuwa_fresh_login', '1')
    // Clean up URL params so they don't linger
    if (window.location.search) {
      history.replaceState({}, document.title, window.location.pathname + window.location.hash)
    }
  }

  // Auth guard: both pages require login
  if (!isLoggedIn()) {
    // For panel page without auth, let the page itself show a login link
    if (to.name === 'panel') {
      return true
    }
    // For index page, redirect to login
    window.location.href = '/login'
    return false
  }
  return true
})

export default router
