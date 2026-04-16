<template>
  <div class="auth-container">
    <div class="auth-card card">
      <h1>保质期管家</h1>
      
      <div class="auth-tabs">
        <div 
          :class="['auth-tab', { active: activeTab === 'login' }]"
          @click="activeTab = 'login'"
        >
          登录
        </div>
        <div 
          :class="['auth-tab', { active: activeTab === 'register' }]"
          @click="activeTab = 'register'"
        >
          注册
        </div>
      </div>

      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>邮箱</label>
          <input 
            v-model="loginForm.email" 
            type="email" 
            class="input" 
            placeholder="请输入邮箱"
            required
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            class="input" 
            placeholder="请输入密码"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label>邮箱</label>
          <input 
            v-model="registerForm.email" 
            type="email" 
            class="input" 
            placeholder="请输入邮箱"
            required
          />
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input 
            v-model="registerForm.nickname" 
            type="text" 
            class="input" 
            placeholder="请输入昵称（可选）"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            class="input" 
            placeholder="请输入密码"
            required
            minlength="6"
          />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            class="input" 
            placeholder="请再次输入密码"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const showNotification = inject('showNotification')

const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const response = await authApi.login(loginForm.value)
    authStore.setAuth(response.data.user, response.data.token)
    showNotification('登录成功！')
    router.push('/dashboard')
  } catch (error) {
    showNotification(error.response?.data?.error || '登录失败', 'error')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    showNotification('两次密码输入不一致', 'error')
    return
  }

  loading.value = true
  try {
    const response = await authApi.register({
      email: registerForm.value.email,
      password: registerForm.value.password,
      nickname: registerForm.value.nickname
    })
    authStore.setAuth(response.data.user, response.data.token)
    showNotification('注册成功！')
    router.push('/dashboard')
  } catch (error) {
    showNotification(error.response?.data?.error || '注册失败', 'error')
  } finally {
    loading.value = false
  }
}
</script>
