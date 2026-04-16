<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>设置</h1>
      </div>

      <div class="card" style="margin-bottom: 20px;">
        <h3 style="margin-bottom: 20px;">个人信息</h3>
        
        <div class="form-group">
          <label>邮箱</label>
          <input 
            :value="authStore.user?.email" 
            type="email" 
            class="input" 
            disabled
          />
        </div>

        <div class="form-group">
          <label>昵称</label>
          <input 
            v-model="form.nickname" 
            type="text" 
            class="input" 
            placeholder="输入昵称"
          />
        </div>

        <button @click="updateProfile" class="btn btn-primary" :disabled="updating">
          {{ updating ? '保存中...' : '保存' }}
        </button>
      </div>

      <div class="card" style="margin-bottom: 20px;">
        <h3 style="margin-bottom: 20px;">通知设置</h3>
        
        <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
          <input 
            v-model="form.email_notifications" 
            type="checkbox"
            style="width: 18px; height: 18px;"
          />
          <span>启用邮件提醒（到期前48小时发送）</span>
        </label>

        <button @click="updateNotifications" class="btn btn-primary" style="margin-top: 20px;" :disabled="updating">
          {{ updating ? '保存中...' : '保存' }}
        </button>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 20px; color: var(--danger);">危险区域</h3>
        <button @click="handleLogout" class="btn btn-secondary">
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const showNotification = inject('showNotification')

const updating = ref(false)

const form = ref({
  nickname: '',
  email_notifications: true
})

const updateProfile = async () => {
  updating.value = true
  try {
    await authApi.updateSettings({ nickname: form.value.nickname })
    await authStore.fetchUser()
    showNotification('个人信息已更新！')
  } catch (error) {
    showNotification('更新失败', 'error')
  } finally {
    updating.value = false
  }
}

const updateNotifications = async () => {
  updating.value = true
  try {
    await authApi.updateSettings({ email_notifications: form.value.email_notifications })
    await authStore.fetchUser()
    showNotification('通知设置已更新！')
  } catch (error) {
    showNotification('更新失败', 'error')
  } finally {
    updating.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (authStore.user) {
    form.value.nickname = authStore.user.nickname || ''
    form.value.email_notifications = authStore.user.email_notifications !== false
  }
})
</script>
