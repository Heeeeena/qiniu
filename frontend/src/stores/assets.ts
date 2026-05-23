import { defineStore } from 'pinia'
import { generateAssets } from '../api/assets'
import type { GeneratedAsset, GenerateRequest, GenerateResponse } from '../types/assets'

const STORAGE_KEY = 'game-asset-forge-history'

interface AssetState {
  generated: GeneratedAsset[]
  history: GeneratedAsset[]
  enhancedPrompt: string
  constraints: string[]
  loading: boolean
  error: string
}

export const useAssetStore = defineStore('assets', {
  state: (): AssetState => ({
    generated: [],
    history: [],
    enhancedPrompt: '',
    constraints: [],
    loading: false,
    error: '',
  }),
  actions: {
    restoreHistory() {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return

      try {
        this.history = JSON.parse(raw)
      } catch {
        this.history = []
      }
    },
    persistHistory() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history.slice(0, 24)))
    },
    async generate(payload: GenerateRequest): Promise<GenerateResponse | undefined> {
      this.loading = true
      this.error = ''

      try {
        const response = await generateAssets(payload)
        this.generated = response.assets
        this.enhancedPrompt = response.enhancedPrompt
        this.constraints = response.constraints
        this.history = [...response.assets, ...this.history].slice(0, 24)
        this.persistHistory()
        return response
      } catch (error) {
        const message = error instanceof Error ? error.message : '生成失败，请检查后端服务'
        this.error = message
        return undefined
      } finally {
        this.loading = false
      }
    },
    clearHistory() {
      this.history = []
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
