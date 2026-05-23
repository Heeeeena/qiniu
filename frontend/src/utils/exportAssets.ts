import { saveAs } from 'file-saver'
import JSZip from 'jszip'
import type { GeneratedAsset, GenerateRequest } from '../types/assets'

const dataUrlToBlob = async (dataUrl: string): Promise<Blob> => {
  const response = await fetch(dataUrl)
  return response.blob()
}

const safeName = (value: string) =>
  value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, '-')
    .replace(/^-|-$/g, '') || 'asset'

export const exportSinglePng = async (asset: GeneratedAsset) => {
  const blob = await dataUrlToBlob(asset.dataUrl)
  saveAs(blob, `${safeName(asset.name)}.png`)
}

export const exportZipPackage = async (assets: GeneratedAsset[], request: GenerateRequest) => {
  const zip = new JSZip()
  const imageFolder = zip.folder('images')

  await Promise.all(
    assets.map(async (asset, index) => {
      const blob = await dataUrlToBlob(asset.dataUrl)
      imageFolder?.file(`${String(index + 1).padStart(2, '0')}-${safeName(asset.name)}.png`, blob)
    }),
  )

  zip.file(
    'metadata.json',
    JSON.stringify(
      {
        project: request.projectName,
        exportedAt: new Date().toISOString(),
        request,
        assets: assets.map(({ dataUrl, ...asset }) => asset),
      },
      null,
      2,
    ),
  )

  zip.file(
    'README.md',
    [
      `# ${request.projectName} asset pack`,
      '',
      'Images are stored under `/images`.',
      'Import the PNG files directly into Unity, Godot, Cocos, Tiled, Aseprite, or a custom 2D pipeline.',
      'Use `metadata.json` to map asset names, prompts, styles, sizes, and seeds.',
    ].join('\n'),
  )

  const blob = await zip.generateAsync({ type: 'blob' })
  saveAs(blob, `${safeName(request.projectName)}-asset-pack.zip`)
}

const loadImage = (src: string): Promise<HTMLImageElement> =>
  new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = reject
    image.src = src
  })

export const exportSpriteSheet = async (assets: GeneratedAsset[], projectName: string) => {
  if (!assets.length) return

  const images = await Promise.all(assets.map((asset) => loadImage(asset.dataUrl)))
  const cellSize = Math.max(...assets.map((asset) => asset.size))
  const columns = Math.ceil(Math.sqrt(images.length))
  const rows = Math.ceil(images.length / columns)
  const canvas = document.createElement('canvas')
  canvas.width = columns * cellSize
  canvas.height = rows * cellSize

  const context = canvas.getContext('2d')
  if (!context) return
  context.imageSmoothingEnabled = false
  context.clearRect(0, 0, canvas.width, canvas.height)

  images.forEach((image, index) => {
    const column = index % columns
    const row = Math.floor(index / columns)
    context.drawImage(image, column * cellSize, row * cellSize, cellSize, cellSize)
  })

  canvas.toBlob((blob) => {
    if (blob) saveAs(blob, `${safeName(projectName)}-spritesheet.png`)
  }, 'image/png')
}
