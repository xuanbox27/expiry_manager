<template>
  <div :class="['item-card', { expired: isExpired, expiring: isExpiringSoon }]">
    <div class="item-info">
      <h3>{{ item.name }}</h3>
      <div class="item-meta">
        <span class="badge" :class="categoryClass">{{ item.category }}</span>
        <span v-if="item.owner_name && showOwner" style="margin-left: 8px;">
          {{ item.owner_name }}的
        </span>
      </div>
      <div v-if="item.purchase_date" class="purchase-meta">
        {{ formatDate(item.purchase_date) }} 购买
      </div>
    </div>
    <div class="item-status">
      <div :class="statusClass">{{ daysLeftText }}</div>
      <small style="color: var(--gray-500);">{{ formatDate(item.expiry_date) }}</small>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  showOwner: {
    type: Boolean,
    default: true
  }
})

const today = new Date()
today.setHours(0, 0, 0, 0)

const expiryDate = computed(() => new Date(props.item.expiry_date))

const daysLeft = computed(() => {
  const diff = expiryDate.value - today
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const isExpired = computed(() => daysLeft.value < 0)
const isExpiringSoon = computed(() => daysLeft.value >= 0 && daysLeft.value <= 3)

const daysLeftText = computed(() => {
  if (daysLeft.value < 0) return `已过期${Math.abs(daysLeft.value)}天`
  if (daysLeft.value === 0) return '今天到期'
  if (daysLeft.value === 1) return '明天到期'
  return `剩余${daysLeft.value}天`
})

const statusClass = computed(() => {
  if (isExpired.value) return 'status-expired'
  if (isExpiringSoon.value) return 'status-expiring'
  return 'status-fresh'
})

const categoryClass = computed(() => {
  const map = {
    '食品': 'badge-warning',
    '饮料': 'badge-info',
    '乳制品': 'badge-success',
    '调味品': 'badge-warning',
    '零食': 'badge-warning',
    '生鲜': 'badge-fresh',
    '药品': 'badge-danger',
    '化妆品': 'badge-info',
    '日用品': 'badge-secondary'
  }
  return map[props.item.category] || 'badge-secondary'
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.badge-info {
  background: #E3F2FD;
  color: var(--info);
}

.badge-fresh {
  background: #E8F5E9;
  color: #2E7D32;
}

.badge-secondary {
  background: var(--gray-200);
  color: var(--gray-600);
}

.expired {
  border-left: 4px solid var(--danger);
  opacity: 0.8;
}

.expiring {
  border-left: 4px solid var(--warning);
}

.purchase-meta {
  font-size: 12px;
  color: var(--gray-500);
  margin-top: 4px;
}
</style>
