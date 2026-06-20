<script setup lang="ts">
import { ref } from 'vue'
import ToastNotification from '@/components/ToastNotification.vue'

const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

function showToast(msg: string, type: 'success' | 'error') {
  toastMessage.value = msg
  toastType.value = type
  setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
}

// Provide toast globally
import { provide } from 'vue'
provide('toast', showToast)
</script>

<template>
  <RouterView />
  <ToastNotification
    v-if="toastMessage"
    :message="toastMessage"
    :type="toastType"
  />
</template>
