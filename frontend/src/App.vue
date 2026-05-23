<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
import {
  Archive,
  Boxes,
  CheckCircle2,
  Download,
  FileJson,
  Grid3X3,
  History,
  ImageDown,
  Layers3,
  LoaderCircle,
  Palette,
  RefreshCw,
  Sparkles,
  WandSparkles,
} from '@lucide/vue'
import { useAssetStore } from './stores/assets'
import { exportSinglePng, exportSpriteSheet, exportZipPackage } from './utils/exportAssets'
import type {
  AssetTypePreset,
  GenerateRequest,
  GeneratedAsset,
  PalettePreset,
  StylePreset,
} from './types/assets'

const store = useAssetStore()

const assetTypes: AssetTypePreset[] = [
  { label: '角色', value: 'character', hint: 'Character' },
  { label: '道具', value: 'item', hint: 'Item' },
  { label: '瓦片', value: 'tile', hint: 'Tile' },
  { label: '背景', value: 'background', hint: 'Background' },
  { label: 'UI', value: 'ui', hint: 'Interface' },
]

const styles: StylePreset[] = [
  { label: '像素', value: 'pixel', hint: 'Pixel art' },
  { label: '卡通', value: 'cartoon', hint: 'Cartoon' },
  { label: '手绘', value: 'ink', hint: 'Ink' },
  { label: '暗黑', value: 'dark', hint: 'Dark' },
  { label: '科幻', value: 'sci-fi', hint: 'Sci-fi' },
]

const palettes: PalettePreset[] = [
  { label: 'Ember', value: 'ember', colors: ['#151515', '#f2552c', '#ffb238', '#f7f1d7'] },
  { label: 'Forest', value: 'forest', colors: ['#163a2f', '#2f8f5b', '#92c96a', '#f4e7ba'] },
  { label: 'Ocean', value: 'ocean', colors: ['#102542', '#1f7a8c', '#7dcfb6', '#f2f7f2'] },
  { label: 'Candy', value: 'candy', colors: ['#2b2d42', '#ff5d8f', '#ffc8dd', '#f8f7ff'] },
  { label: 'Mono', value: 'mono', colors: ['#121212', '#555555', '#aaaaaa', '#f5f5f5'] },
]

const request = reactive<GenerateRequest>({
  projectName: 'Dungeon Starter Kit',
  description: '一套地牢探索游戏里的蓝色魔法水晶、入口石门和发光地砖',
  assetType: 'item',
  style: 'pixel',
  size: 128,
  count: 4,
  transparentBackground: true,
  palette: 'ocean',
  consistencySeed: 'qiniu-first-batch',
})

const activePalette = computed(() => palettes.find((palette) => palette.value === request.palette))
const visibleAssets = computed(() => store.generated.length > 0 ? store.generated : store.history.slice(0, 6))
const canExport = computed(() => store.generated.length > 0)
const canGenerate = computed(() => request.description.trim().length > 0 && !store.loading)

onMounted(() => {
  store.restoreHistory()
})

const runGeneration = async () => {
  await store.generate({ ...request, description: request.description.trim() })
}

const applyHistoryAsset = (asset: GeneratedAsset) => {
  request.assetType = asset.assetType
  request.style = asset.style
  request.size = asset.size
  request.description = String(asset.metadata.source_description ?? request.description)
  request.consistencySeed = asset.seed.split('-').slice(0, -1).join('-') || request.consistencySeed
}

const exportMetadata = () => {
  const blob = new Blob(
    [
      JSON.stringify(
        {
          request,
          enhancedPrompt: store.enhancedPrompt,
          constraints: store.constraints,
          assets: store.generated.map(({ dataUrl, ...asset }) => asset),
        },
        null,
        2,
      ),
    ],
    { type: 'application/json;charset=utf-8' },
  )
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${request.projectName.toLowerCase().replace(/\s+/g, '-')}-metadata.json`
  anchor.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">GF</span>
        <div>
          <h1>GameAssetForge</h1>
          <p>2D 游戏素材生成工作台</p>
        </div>
      </div>
      <div class="status-pill">
        <CheckCircle2 :size="18" />
        <span>Local generator</span>
      </div>
    </header>

    <main class="workbench">
      <section class="tool-panel controls-panel" aria-label="素材参数">
        <div class="panel-title">
          <WandSparkles :size="20" />
          <h2>生成参数</h2>
        </div>

        <label class="field">
          <span>项目名称</span>
          <input v-model="request.projectName" type="text" />
        </label>

        <label class="field">
          <span>素材需求</span>
          <textarea v-model="request.description" rows="5" />
        </label>

        <div class="field">
          <span>素材类型</span>
          <div class="segmented">
            <button
              v-for="type in assetTypes"
              :key="type.value"
              type="button"
              :class="{ active: request.assetType === type.value }"
              :title="type.hint"
              @click="request.assetType = type.value"
            >
              {{ type.label }}
            </button>
          </div>
        </div>

        <div class="field">
          <span>美术风格</span>
          <div class="segmented">
            <button
              v-for="style in styles"
              :key="style.value"
              type="button"
              :class="{ active: request.style === style.value }"
              :title="style.hint"
              @click="request.style = style.value"
            >
              {{ style.label }}
            </button>
          </div>
        </div>

        <div class="field two-column">
          <label>
            <span>尺寸</span>
            <select v-model.number="request.size">
              <option :value="32">32 x 32</option>
              <option :value="64">64 x 64</option>
              <option :value="128">128 x 128</option>
              <option :value="256">256 x 256</option>
            </select>
          </label>
          <label>
            <span>数量</span>
            <input v-model.number="request.count" type="number" min="1" max="8" />
          </label>
        </div>

        <div class="field">
          <span>色板</span>
          <div class="palette-list">
            <button
              v-for="palette in palettes"
              :key="palette.value"
              type="button"
              :class="{ active: request.palette === palette.value }"
              :title="palette.label"
              @click="request.palette = palette.value"
            >
              <span
                v-for="color in palette.colors"
                :key="color"
                class="swatch"
                :style="{ backgroundColor: color }"
              />
            </button>
          </div>
        </div>

        <label class="field">
          <span>一致性种子</span>
          <input v-model="request.consistencySeed" type="text" />
        </label>

        <label class="toggle">
          <input v-model="request.transparentBackground" type="checkbox" />
          <span>透明背景</span>
        </label>

        <button class="primary-action" type="button" :disabled="!canGenerate" @click="runGeneration">
          <LoaderCircle v-if="store.loading" class="spin" :size="19" />
          <Sparkles v-else :size="19" />
          <span>{{ store.loading ? '生成中' : '生成素材' }}</span>
        </button>
      </section>

      <section class="stage-panel" aria-label="生成结果">
        <div class="stage-toolbar">
          <div>
            <p class="eyebrow">Asset Preview</p>
            <h2>{{ request.projectName }}</h2>
          </div>
          <div class="palette-chip" v-if="activePalette">
            <Palette :size="17" />
            <span>{{ activePalette.label }}</span>
          </div>
        </div>

        <div class="prompt-strip">
          <Sparkles :size="18" />
          <p>{{ store.enhancedPrompt || '生成后这里会显示后端增强后的游戏素材 Prompt。' }}</p>
        </div>

        <div v-if="store.error" class="error-box">{{ store.error }}</div>

        <div class="asset-grid" :class="{ empty: visibleAssets.length === 0 }">
          <article v-for="asset in visibleAssets" :key="asset.id" class="asset-card">
            <div class="asset-canvas">
              <img :src="asset.dataUrl" :alt="asset.name" />
            </div>
            <div class="asset-info">
              <div>
                <h3>{{ asset.name }}</h3>
                <p>{{ asset.size }}px · {{ asset.style }}</p>
              </div>
              <button type="button" title="下载 PNG" @click="exportSinglePng(asset)">
                <Download :size="17" />
              </button>
            </div>
          </article>

          <div v-if="visibleAssets.length === 0" class="empty-state">
            <Boxes :size="32" />
            <p>等待生成第一组素材</p>
          </div>
        </div>

        <div class="constraint-bar" v-if="store.constraints.length">
          <span v-for="constraint in store.constraints" :key="constraint">{{ constraint }}</span>
        </div>
      </section>

      <aside class="tool-panel export-panel" aria-label="导出与历史">
        <div class="panel-title">
          <Archive :size="20" />
          <h2>导出</h2>
        </div>

        <div class="export-actions">
          <button type="button" :disabled="!canExport" @click="exportZipPackage(store.generated, request)">
            <ImageDown :size="18" />
            <span>ZIP</span>
          </button>
          <button type="button" :disabled="!canExport" @click="exportSpriteSheet(store.generated, request.projectName)">
            <Grid3X3 :size="18" />
            <span>Sheet</span>
          </button>
          <button type="button" :disabled="!canExport" @click="exportMetadata">
            <FileJson :size="18" />
            <span>JSON</span>
          </button>
        </div>

        <div class="panel-title compact">
          <Layers3 :size="19" />
          <h2>项目约束</h2>
        </div>
        <dl class="spec-list">
          <div>
            <dt>类型</dt>
            <dd>{{ request.assetType }}</dd>
          </div>
          <div>
            <dt>规格</dt>
            <dd>{{ request.size }}px</dd>
          </div>
          <div>
            <dt>风格</dt>
            <dd>{{ request.style }}</dd>
          </div>
          <div>
            <dt>数量</dt>
            <dd>{{ request.count }}</dd>
          </div>
        </dl>

        <div class="history-head">
          <div class="panel-title compact">
            <History :size="19" />
            <h2>历史</h2>
          </div>
          <button type="button" title="清空历史" @click="store.clearHistory">
            <RefreshCw :size="16" />
          </button>
        </div>

        <div class="history-list">
          <button
            v-for="asset in store.history.slice(0, 8)"
            :key="asset.id"
            type="button"
            @click="applyHistoryAsset(asset)"
          >
            <img :src="asset.dataUrl" :alt="asset.name" />
            <span>{{ asset.name }}</span>
          </button>
          <p v-if="store.history.length === 0" class="muted">暂无历史记录</p>
        </div>
      </aside>
    </main>
  </div>
</template>
