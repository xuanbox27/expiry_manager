<template>
  <div class="page">
    <div class="container">
      <div class="header">
        <h1>添加物品</h1>
      </div>

      <div class="card">
        <div class="form-group">
          <label>扫码或输入条码</label>
          <div style="display: flex; gap: 10px;">
            <input 
              v-model="barcode" 
              type="text" 
              class="input" 
              placeholder="输入条码或扫描"
              @keyup.enter="lookupBarcode"
            />
            <button @click="lookupBarcode" class="btn btn-primary" :disabled="scanning">
              {{ scanning ? '查询中...' : '查询' }}
            </button>
          </div>
          <small v-if="scanResult.found" style="color: var(--success);">
            找到商品：{{ scanResult.name }}
          </small>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>物品名称 *</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="input" 
              placeholder="输入物品名称"
              required
            />
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
              <label>到期日期 *</label>
              <input 
                v-model="form.expiry_date" 
                type="date" 
                class="input" 
                required
              />
            </div>

            <div v-else class="calculate-mode">
              <div class="form-group">
                <label>购买日期 *</label>
                <input 
                  v-model="form.purchase_date" 
                  type="date" 
                  class="input" 
                  :max="todayStr"
                />
              </div>

              <div class="form-group">
                <label>保质期天数 *</label>
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
                <div class="preset-chips">
                  <span 
                    v-for="preset in presetOptions" 
                    :key="preset.days"
                    class="preset-chip"
                    @click="applyPreset(preset)"
                  >
                    {{ preset.label }}
                  </span>
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
            <label>备注</label>
            <textarea 
              v-model="form.notes" 
              class="textarea" 
              placeholder="添加备注（可选）"
            ></textarea>
          </div>

          <div style="display: flex; gap: 10px;">
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? '保存中...' : '保存' }}
            </button>
            <router-link to="/dashboard" class="btn btn-secondary">
              取消
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useItemsStore } from '../stores/items'

const router = useRouter()
const itemsStore = useItemsStore()
const showNotification = inject('showNotification')

const barcode = ref('')
const scanning = ref(false)
const submitting = ref(false)
const scanResult = ref({ found: false })
const dateInputMode = ref('direct')

const todayStr = computed(() => new Date().toISOString().split('T')[0])

const form = ref({
  name: '',
  category: '食品',
  expiry_date: '',
  purchase_date: '',
  shelf_life_days: null,
  notes: ''
})

const presetOptions = [
  { label: '鲜奶/酸奶', days: 7 },
  { label: '面包', days: 5 },
  { label: '叶菜', days: 3 },
  { label: '肉类(冷藏)', days: 3 },
  { label: '肉类(冷冻)', days: 30 },
  { label: '水果', days: 7 },
  { label: '鸡蛋', days: 14 },
  { label: '蛋糕', days: 3 },
  { label: '熟食', days: 2 },
]

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
  if (newMode === 'direct') {
    form.value.purchase_date = ''
    form.value.shelf_life_days = null
  } else {
    form.value.purchase_date = todayStr.value
    form.value.expiry_date = ''
  }
})

const applyPreset = (preset) => {
  form.value.shelf_life_days = preset.days
}

const lookupBarcode = async () => {
  if (!barcode.value) return

  scanning.value = true
  try {
    const result = await itemsStore.scanBarcode(barcode.value)
    scanResult.value = result

    if (result.found) {
      form.value.name = result.name
      form.value.category = result.category
      if (result.suggestedExpiryDate) {
        form.value.expiry_date = result.suggestedExpiryDate
      }
    } else {
      showNotification('未找到商品，请手动输入', 'error')
    }
  } catch (error) {
    showNotification('查询失败', 'error')
  } finally {
    scanning.value = false
  }
}

const handleSubmit = async () => {
  if (dateInputMode.value === 'calculate' && canCalculate.value) {
    form.value.expiry_date = calculatedExpiryDate.value
  }

  if (!form.value.expiry_date) {
    showNotification('请输入到期日期', 'error')
    return
  }

  submitting.value = true
  try {
    await itemsStore.createItem({
      barcode: barcode.value || null,
      name: form.value.name,
      category: form.value.category,
      expiry_date: form.value.expiry_date,
      purchase_date: form.value.purchase_date || null,
      shelf_life_days: form.value.shelf_life_days || null,
      notes: form.value.notes
    })
    showNotification('添加成功！')
    router.push('/dashboard')
  } catch (error) {
    showNotification('添加失败', 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 30)
  form.value.expiry_date = tomorrow.toISOString().split('T')[0]
  form.value.purchase_date = todayStr.value
})
</script>

<style scoped>
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

.preset-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.preset-chip {
  padding: 6px 12px;
  background: white;
  border: 1px solid var(--gray-300);
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-chip:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
</style>
