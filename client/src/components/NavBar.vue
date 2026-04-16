<template>
  <nav class="nav">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
      <router-link to="/dashboard" class="nav-brand">保质期管家</router-link>
      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link">
          <span>首页</span>
        </router-link>
        <router-link to="/add" class="nav-link">
          <span>添加</span>
        </router-link>
        <router-link to="/family" class="nav-link">
          <span>家庭</span>
        </router-link>
        <router-link to="/notifications" class="nav-link notification-link">
          <span>通知</span>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </router-link>
        <router-link to="/settings" class="nav-link">
          <span>设置</span>
        </router-link>
        <button @click="logout" class="btn btn-secondary" style="margin-left: 10px;">
          退出
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { notificationsApi } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const unreadCount = ref(0)

const fetchUnreadCount = async () => {
  try {
    const response = await notificationsApi.getAll(true)
    unreadCount.value = response.data.length
  } catch (error) {
    console.error('Failed to fetch unread count')
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(fetchUnreadCount)
</script>

<style scoped>
.notification-link {
  position: relative;
}

.badge {
  position: absolute;
  top: -6px;
  right: -10px;
  background: var(--danger);
  color: white;
  font-size: 10px;
  padding: 2px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}
</style>
