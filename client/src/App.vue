<template>
  <div id="app">
    <div v-if="notification.show" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>
    <NavBar v-if="authStore.isLoggedIn" />
    <router-view />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

const notification = ref({ show: false, message: '', type: 'success' })

const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type }
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

provide('showNotification', showNotification)
</script>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
