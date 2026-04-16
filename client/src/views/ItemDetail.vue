<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>物品详情</h1>
        <button @click="showDeleteModal = true" class="btn btn-danger">
          删除
        </button>
      </div>

      <div v-if="loading" style="text-align: center; padding: 40px;">
        加载中...
      </div>

      <div v-else-if="item" class="card">
        <div style="margin-bottom: 20px;">
          <h2 style="margin-bottom: 8px;">{{ item.name }}</h2>
          <span class="badge badge-success">{{ item.category }}</span>
          <div v-if="item.purchase_date || item.shelf_life_days" class="purchase-info">
            <span v-if="item.purchase_date">购买于 {{ formatDate(item.purchase_date) }}</span>
            <span v-if="item.purchase_date && item.shelf_life_days">，</span>
            <span v-if="item.shelf_life_days">保质期 {{ item.shelf_life_days }} 天</span>
          </div>
        </div>

        <form @submit.prevent="handleUpdate">
          <div class="date-input-section">
            <div class="date-mode-toggle">
              <button 
                type="button"
                :class="['mode-btn', { active: dateInputMode === 'direct' }]"
                @click="dateInputMode = 'direct'"
              >
                直接输入过期日期
              </button>
              <button 
                type="button"
                :class="['mode-btn', { active: dateInputMode === 'calculate' }]"
                @click="dateInputMode = 'calculate'"
              >
                购买日期+保质期推算
              </button>
            </div>

            <div v-if="dateInputMode === 'direct'" class="form-group">
              <label>到期日期</label>
              <input 
                v-model="form.expiry_date" 
                type="date" 
                class="input" 
                required
              />
            </div>

            <div v-else class="calculate-mode">
              <div class="form-group">
                <label>购买日期</label>
                <input 
                  v-model="form.purchase_date" 
                  type="date" 
                  class="input" 
                  :max="todayStr"
                />
              </div>

              <div class="form-group">
                <label>保质期天数</label>
                <div style="display: flex; gap: 10px; align-items: center;">
                  <input 
                    v-model.number="form.shelf_life_days" 
                    type="number" 
                    class="input" 
                    min="1"
                    placeholder="输入天数"
                    style="flex: 1;"
                  />
                  <span style="color: var(--gray-500); white-space: nowrap;">天</span>
                </div>
              </div>

              <div class="form-group">
                <label>计算结果 - 到期日期</label>
                <input 
                  v-model="calculatedExpiryDate" 
                  type="date" 
                  class="input" 
                  :disabled="!canCalculate"
                  style="background: var(--gray-100);"
                />
                <small style="color: var(--gray-500);">
                  可手动修改计算结果
                </small>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>分类</label>
            <select v-model="form.category" class="select">
              <option value="食品">食品</option>
              <option value="饮料">饮料</option>
              <option value="乳制品">乳制品</option>
              <option value="调味品">调味品</option>
              <option value="零食">零食</option>
              <option value="生鲜">生鲜</option>
              <option value="药品">药品</option>
              <option value="化妆品">化妆品</option>
              <option value="日用品">日用品</option>
              <option value="其他">其他</option>
            </select>
          </div>

          <div class="form-group">
            <label>状态</label>
            <select v-model="form.status" class="select">
              <option value="active">使用中</option>
              <option value="used">已用完</option>
              <option value="discarded">已丢弃</option>
            </select>
          </div>

          <div class="form-group">
            <label>备注</label>
            <textarea 
              v-model="form.notes" 
              class="textarea" 
              placeholder="添加备注"
            ></textarea>
          </div>

          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </form>
      </div>

      <div v-else class="empty-state">
        <h2>物品不存在</h2>
        <router-link to="/dashboard" class="btn btn-primary">返回首页</router-link>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>确认删除</h3>
          <button class="modal-close" @click="showDeleteModal = false">&times;</button>
        </div>
        <p style="margin-bottom: 20px;">确定要删除"{{ item?.name }}"吗？此操作不可恢复。</p>
        <div style="display: flex; gap: 10px;">
          <button @click="handleDelete" class="btn btn-danger">
            删除
          </button>
          <button @click="showDeleteModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemsStore } from '../stores/items'
import { itemsApi } from '../api'

const route = useRoute()
const router = useRouter()
const itemsStore = useItemsStore()
const showNotification = inject('showNotification')

const item = ref(null)
const loading = ref(true)
const submitting = ref(false)
const showDeleteModal = ref(false)
const dateInputMode = ref('direct')

const todayStr = computed(() => new Date().toISOString().split('T')[0])

const form = ref({
  expiry_date: '',
  category: '食品',
  status: 'active',
  notes: '',
  purchase_date: '',
  shelf_life_days: null
})

const canCalculate = computed(() => {
  return form.value.purchase_date && form.value.shelf_life_days > 0
})

const calculatedExpiryDate = computed({
  get() {
    if (!canCalculate.value) return ''
    const date = new Date(form.value.purchase_date)
    date.setDate(date.getDate() + form.value.shelf_life_days)
    return date.toISOString().split('T')[0]
  },
  set(value) {
    form.value.expiry_date = value
  }
})

watch([() => form.value.purchase_date, () => form.value.shelf_life_days], () => {
  if (canCalculate.value && dateInputMode.value === 'calculate') {
    calculatedExpiryDate.value = calculatedExpiryDate.value
  }
})

watch(dateInputMode, (newMode) => {
  if (newMode === 'calculate' && !form.value.purchase_date) {
    form.value.purchase_date = todayStr.value
  }
})

const fetchItem = async () => {
  loading.value = true
  try {
    const response = await itemsApi.getOne(route.params.id)
    item.value = response.data
    form.value = {
      expiry_date: response.data.expiry_date,
      category: response.data.category,
      status: response.data.status,
      notes: response.data.notes || '',
      purchase_date: response.data.purchase_date || '',
      shelf_life_days: response.data.shelf_life_days || null
    }
    if (form.value.purchase_date && form.value.shelf_life_days) {
      dateInputMode.value = 'calculate'
    }
  } catch (error) {
    showNotification('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

const handleUpdate = async () => {
  let payload = {
    category: form.value.category,
    status: form.value.status,
    notes: form.value.notes,
    purchase_date: form.value.purchase_date || null,
    shelf_life_days: form.value.shelf_life_days || null
  }

  if (dateInputMode.value === 'calculate' && canCalculate.value) {
    payload.expiry_date = calculatedExpiryDate.value
  } else {
    payload.expiry_date = form.value.expiry_date
  }

  submitting.value = true
  try {
    await itemsStore.updateItem(route.params.id, payload)
    showNotification('更新成功！')
    fetchItem()
  } catch (error) {
    showNotification('更新失败', 'error')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async () => {
  try {
    await itemsStore.deleteItem(route.params.id)
    showNotification('删除成功！')
    router.push('/dashboard')
  } catch (error) {
    showNotification('删除失败', 'error')
  }
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(fetchItem)
</script>

<style scoped>
.purchase-info {
  margin-top: 8px;
  font-size: 14px;
  color: var(--gray-600);
}

.date-input-section {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--gray-100);
  border-radius: 12px;
}

.date-mode-toggle {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.mode-btn {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid var(--gray-300);
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.mode-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.calculate-mode {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
