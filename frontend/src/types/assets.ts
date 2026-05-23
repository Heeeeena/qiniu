export type AssetType = 'character' | 'item' | 'tile' | 'background' | 'ui'

export type AssetStyle = 'pixel' | 'cartoon' | 'ink' | 'dark' | 'sci-fi'

export type PaletteName = 'ember' | 'forest' | 'ocean' | 'candy' | 'mono'

export type QualityStatus = 'pass' | 'warn' | 'fail'

export interface GenerateRequest {
  projectName: string
  description: string
  assetType: AssetType
  style: AssetStyle
  size: number
  count: number
  transparentBackground: boolean
  palette: PaletteName
  consistencySeed: string
  stylePackName?: string
}

export interface GeneratedAsset {
  id: string
  name: string
  assetType: AssetType
  style: AssetStyle
  size: number
  dataUrl: string
  seed: string
  prompt: string
  createdAt: string
  metadata: Record<string, string | number | boolean>
}

export interface GenerateResponse {
  requestId: string
  enhancedPrompt: string
  constraints: string[]
  qualityChecks: QualityCheck[]
  assets: GeneratedAsset[]
}

export interface QualityCheck {
  key: string
  label: string
  status: QualityStatus
  detail: string
}

export interface StylePack {
  id: string
  name: string
  description: string
  assetType: AssetType
  style: AssetStyle
  size: number
  transparentBackground: boolean
  palette: PaletteName
  consistencySeed: string
  updatedAt: string
}

export interface StylePreset {
  label: string
  value: AssetStyle
  hint: string
}

export interface AssetTypePreset {
  label: string
  value: AssetType
  hint: string
}

export interface PalettePreset {
  label: string
  value: PaletteName
  colors: string[]
}
