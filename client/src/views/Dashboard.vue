<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>我的物品</h1>
        <router-link to="/add" class="btn btn-primary">+ 添加物品</router-link>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="value">{{ stats.total }}</div>
          <div class="label">总物品</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: var(--danger);">{{ stats.expiring }}</div>
          <div class="label">即将过期</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: var(--gray-500);">{{ stats.expired }}</div>
          <div class="label">已过期</div>
        </div>
      </div>

      <div class="filter-bar">
        <button 
          :class="['filter-btn', { active: filter === 'all' }]"
          @click="filter = 'all'"
        >
          全部
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'active' }]"
          @click="filter = 'active'"
        >
          正常
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'expiring' }]"
          @click="filter = 'expiring'"
        >
          即将过期
        </button>
        <button 
          :class="['filter-btn', { active: filter === 'expired' }]"
          @click="filter = 'expired'"
        >
          已过期
        </button>
      </div>

      <div v-if="loading" style="text-align: center; padding: 40px;">
        加载中...
      </div>

      <div v-else-if="filteredItems.length === 0" class="empty-state">
        <h2>暂无物品</h2>
        <p>点击上方"添加物品"开始记录</p>
      </div>

      <div v-else>
        <ItemCard 
          v-for="item in filteredItems" 
          :key="item.id" 
          :item="item"
          @click="goToDetail(item.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useItemsStore } from '../stores/items'
import ItemCard from '../components/ItemCard.vue'

const router = useRouter()
const itemsStore = useItemsStore()
const showNotification = inject('showNotification')

const filter = ref('all')
const loading = computed(() => itemsStore.loading)

const filteredItems = computed(() => {
  const items = itemsStore.items
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (filter.value === 'all') return items.filter(i => i.status === 'active')
  
  return items.filter(item => {
    if (item.status !== 'active') return false
    const expiryDate = new Date(item.expiry_date)
    const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24))

    if (filter.value === 'active') return daysLeft > 3
    if (filter.value === 'expiring') return daysLeft >= 0 && daysLeft <= 3
    if (filter.value === 'expired') return daysLeft < 0
    return true
  })
})

const stats = computed(() => {
  const items = itemsStore.items.filter(i => i.status === 'active')
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  let expiring = 0
  let expired = 0

  items.forEach(item => {
    const expiryDate = new Date(item.expiry_date)
    const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24))
    
    if (daysLeft < 0) expired++
    else if (daysLeft <= 3) expiring++
  })

  return {
    total: items.length,
    expiring,
    expired
  }
})

const goToDetail = (id) => {
  router.push(`/item/${id}`)
}

onMounted(async () => {
  try {
    await itemsStore.fetchItems()
  } catch (error) {
    showNotification('加载失败', 'error')
  }
})
</script>
