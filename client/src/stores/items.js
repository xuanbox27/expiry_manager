import { defineStore } from 'pinia'
import { ref } from 'vue'
import { itemsApi } from '../api'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchItems(params = {}) {
    loading.value = true
    try {
      const response = await itemsApi.getAll(params)
      items.value = response.data
    } catch (error) {
      console.error('Failed to fetch items:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createItem(data) {
    try {
      const response = await itemsApi.create(data)
      items.value.unshift(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to create item:', error)
      throw error
    }
  }

  async function updateItem(id, data) {
    try {
      const response = await itemsApi.update(id, data)
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to update item:', error)
      throw error
    }
  }

  async function deleteItem(id) {
    try {
      await itemsApi.delete(id)
      items.value = items.value.filter(item => item.id !== id)
    } catch (error) {
      console.error('Failed to delete item:', error)
      throw error
    }
  }

  async function scanBarcode(barcode) {
    try {
      const response = await itemsApi.scan(barcode)
      return response.data
    } catch (error) {
      console.error('Failed to scan barcode:', error)
      throw error
    }
  }

  return {
    items,
    loading,
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    scanBarcode
  }
})
