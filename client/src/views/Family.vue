<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>家庭管理</h1>
      </div>

      <div v-if="!inFamily" class="card">
        <h3 style="margin-bottom: 20px;">加入或创建家庭</h3>
        
        <div style="margin-bottom: 30px;">
          <h4 style="margin-bottom: 10px;">加入已有家庭</h4>
          <div style="display: flex; gap: 10px;">
            <input 
              v-model="joinCode" 
              type="text" 
              class="input" 
              placeholder="输入家族码"
              style="text-transform: uppercase;"
              maxlength="8"
            />
            <button @click="handleJoin" class="btn btn-primary" :disabled="joining">
              {{ joining ? '加入中...' : '加入' }}
            </button>
          </div>
        </div>

        <div>
          <h4 style="margin-bottom: 10px;">或等待家人邀请</h4>
          <p style="color: var(--gray-500); font-size: 14px;">
            让家人先创建家庭，获取家族码后加入
          </p>
        </div>
      </div>

      <div v-else class="card">
        <div style="text-align: center; margin-bottom: 20px;">
          <h3>家族码</h3>
          <div class="family-code">{{ familyData.family_code }}</div>
          <p style="color: var(--gray-500); font-size: 14px;">
            分享给家人，让他们加入你的家庭
          </p>
          <button @click="copyCode" class="btn btn-secondary" style="margin-top: 10px;">
            复制邀请信息
          </button>
        </div>

        <hr style="margin: 20px 0; border: none; border-top: 1px solid var(--gray-200);">

        <h4 style="margin-bottom: 15px;">家庭成员 ({{ familyData.members?.length || 0 }})</h4>
        
        <div v-if="familyData.owner" style="margin-bottom: 10px; padding: 12px; background: var(--gray-100); border-radius: 8px;">
          <strong>{{ familyData.owner.nickname || familyData.owner.email }}</strong>
          <span style="margin-left: 8px; font-size: 12px; color: var(--primary);">创建者</span>
        </div>

        <div 
          v-for="member in familyData.members" 
          :key="member.id"
          style="margin-bottom: 10px; padding: 12px; background: var(--gray-100); border-radius: 8px;"
        >
          <strong>{{ member.nickname || member.email }}</strong>
          <span style="margin-left: 8px; font-size: 12px; color: var(--gray-500);">
            加入于 {{ formatDate(member.joined_at) }}
          </span>
        </div>

        <div v-if="!familyData.is_owner" style="margin-top: 30px;">
          <button @click="handleLeave" class="btn btn-secondary" style="width: 100%;">
            退出家庭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { familyApi } from '../api'

const showNotification = inject('showNotification')

const joinCode = ref('')
const joining = ref(false)
const inFamily = ref(false)
const familyData = ref({})

const handleJoin = async () => {
  if (!joinCode.value) {
    showNotification('请输入家族码', 'error')
    return
  }

  joining.value = true
  try {
    await familyApi.join(joinCode.value)
    showNotification('加入成功！')
    fetchFamily()
  } catch (error) {
    showNotification(error.response?.data?.error || '加入失败', 'error')
  } finally {
    joining.value = false
  }
}

const handleLeave = async () => {
  if (!confirm('确定要退出家庭吗？')) return

  try {
    await familyApi.leave()
    showNotification('已退出家庭')
    inFamily.value = false
    familyData.value = {}
  } catch (error) {
    showNotification(error.response?.data?.error || '退出失败', 'error')
  }
}

const copyCode = async () => {
  const message = `邀请你加入保质期管家家庭，家族码：${familyData.value.family_code}`
  try {
    await navigator.clipboard.writeText(message)
    showNotification('已复制到剪贴板！')
  } catch {
    showNotification('复制失败，请手动复制', 'error')
  }
}

const fetchFamily = async () => {
  try {
    const response = await familyApi.getMembers()
    familyData.value = response.data
    inFamily.value = !!response.data.family_code
  } catch (error) {
    console.error('Failed to fetch family:', error)
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(fetchFamily)
</script>
