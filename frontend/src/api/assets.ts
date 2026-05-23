import axios from 'axios'
import type { GenerateRequest, GenerateResponse } from '../types/assets'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 30000,
})

const toApiPayload = (payload: GenerateRequest) => ({
  project_name: payload.projectName,
  description: payload.description,
  asset_type: payload.assetType,
  style: payload.style,
  size: payload.size,
  count: payload.count,
  transparent_background: payload.transparentBackground,
  palette: payload.palette,
  consistency_seed: payload.consistencySeed,
})

const toClientAsset = (asset: any) => ({
  id: asset.id,
  name: asset.name,
  assetType: asset.asset_type,
  style: asset.style,
  size: asset.size,
  dataUrl: asset.data_url,
  seed: asset.seed,
  prompt: asset.prompt,
  createdAt: asset.created_at,
  metadata: asset.metadata,
})

export const generateAssets = async (payload: GenerateRequest): Promise<GenerateResponse> => {
  const { data } = await apiClient.post('/assets/generate', toApiPayload(payload))

  return {
    requestId: data.request_id,
    enhancedPrompt: data.enhanced_prompt,
    constraints: data.constraints,
    assets: data.assets.map(toClientAsset),
  }
}

export const checkBackendHealth = async () => {
  const { data } = await apiClient.get('/health')
  return data
}
