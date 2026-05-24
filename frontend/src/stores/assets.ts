import { defineStore } from 'pinia'
import { generateAssets } from '../api/assets'
import type {
  GeneratedAsset,
  GenerateRequest,
  GenerateResponse,
  QualityCheck,
  StylePack,
} from '../types/assets'

const STORAGE_KEY = 'game-asset-forge-history'
const STYLE_PACKS_KEY = 'game-asset-forge-style-packs'

const defaultStylePacks = (): StylePack[] => [
  {
    id: 'dungeon-pixel-ocean',
    name: 'Dungeon Pixel Pack',
    description: '地牢探索道具、瓦片和 UI 的统一像素风格。',
    assetType: 'item',
    style: 'pixel',
    size: 128,
    transparentBackground: true,
    palette: 'ocean',
    consistencySeed: 'qiniu-dungeon-pack',
    targetEngine: 'unity',
    namingPrefix: 'dungeon_pixel',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'forest-cartoon-kit',
    name: 'Forest Cartoon Kit',
    description: '轻量休闲游戏角色和道具的高对比卡通风格。',
    assetType: 'character',
    style: 'cartoon',
    size: 128,
    transparentBackground: true,
    palette: 'forest',
    consistencySeed: 'qiniu-forest-pack',
    targetEngine: 'godot',
    namingPrefix: 'forest_cartoon',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'sci-fi-ui-kit',
    name: 'Sci-fi UI Kit',
    description: '科幻机甲游戏按钮、面板和技能图标的统一 UI 风格。',
    assetType: 'ui',
    style: 'sci-fi',
    size: 128,
    transparentBackground: true,
    palette: 'mono',
    consistencySeed: 'qiniu-scifi-ui-pack',
    targetEngine: 'cocos',
    namingPrefix: 'scifi_ui',
    updatedAt: new Date().toISOString(),
  },
]

const normalizeStylePack = (pack: Partial<StylePack>, index: number): StylePack => ({
  id: pack.id ?? `style-pack-${index + 1}`,
  name: pack.name ?? `Style Pack ${index + 1}`,
  description: pack.description ?? '',
  assetType: pack.assetType ?? 'item',
  style: pack.style ?? 'pixel',
  size: pack.size ?? 128,
  transparentBackground: pack.transparentBackground ?? true,
  palette: pack.palette ?? 'ocean',
  consistencySeed: pack.consistencySeed ?? `style-pack-${index + 1}`,
  targetEngine: pack.targetEngine ?? 'unity',
  namingPrefix: pack.namingPrefix,
  updatedAt: pack.updatedAt ?? new Date().toISOString(),
})

interface AssetState {
  generated: GeneratedAsset[]
  history: GeneratedAsset[]
  stylePacks: StylePack[]
  enhancedPrompt: string
  constraints: string[]
  qualityChecks: QualityCheck[]
  loading: boolean
  error: string
}

export const useAssetStore = defineStore('assets', {
  state: (): AssetState => ({
    generated: [],
    history: [],
    stylePacks: [],
    enhancedPrompt: '',
    constraints: [],
    qualityChecks: [],
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
    restoreStylePacks() {
      const raw = localStorage.getItem(STYLE_PACKS_KEY)
      if (!raw) {
        this.stylePacks = defaultStylePacks()
        this.persistStylePacks()
        return
      }

      try {
        this.stylePacks = JSON.parse(raw).map(normalizeStylePack)
        this.persistStylePacks()
      } catch {
        this.stylePacks = defaultStylePacks()
        this.persistStylePacks()
      }
    },
    persistHistory() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history.slice(0, 24)))
    },
    persistStylePacks() {
      localStorage.setItem(STYLE_PACKS_KEY, JSON.stringify(this.stylePacks))
    },
    async generate(payload: GenerateRequest): Promise<GenerateResponse | undefined> {
      this.loading = true
      this.error = ''

      try {
        const response = await generateAssets(payload)
        this.generated = response.assets
        this.enhancedPrompt = response.enhancedPrompt
        this.constraints = response.constraints
        this.qualityChecks = response.qualityChecks
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
    saveStylePack(pack: Omit<StylePack, 'updatedAt'>) {
      const nextPack: StylePack = {
        ...pack,
        updatedAt: new Date().toISOString(),
      }
      const index = this.stylePacks.findIndex((item) => item.id === nextPack.id)
      if (index >= 0) {
        this.stylePacks.splice(index, 1, nextPack)
      } else {
        this.stylePacks.unshift(nextPack)
      }
      this.persistStylePacks()
    },
    deleteStylePack(id: string) {
      this.stylePacks = this.stylePacks.filter((pack) => pack.id !== id)
      this.persistStylePacks()
    },
  },
})
