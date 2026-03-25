import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ApiFetch } from '@/utils/apiFetch';

export const useConfigStore = defineStore('config', () => {
  const config = ref({})
  async function getConfig() {
    config.value = (await ApiFetch.getConfig()).json
  }
  async function pushConfig() {
    await ApiFetch.saveConfig(config.value)
  }

  return { config, getConfig, pushConfig }
})