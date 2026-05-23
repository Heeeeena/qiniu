import { saveAs } from 'file-saver'
import JSZip from 'jszip'
import type { GeneratedAsset, GenerateRequest, QualityCheck, TargetEngine } from '../types/assets'

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

const assetFileName = (asset: GeneratedAsset, index: number, request?: GenerateRequest) => {
  const prefix = request?.namingPrefix || request?.projectName || asset.name
  return `${safeName(prefix)}-${String(index + 1).padStart(2, '0')}.png`
}

export const exportSinglePng = async (
  asset: GeneratedAsset,
  request?: GenerateRequest,
  index = 0,
) => {
  const blob = await dataUrlToBlob(asset.dataUrl)
  saveAs(blob, request ? assetFileName(asset, index, request) : `${safeName(asset.name)}.png`)
}

const loadImage = (src: string): Promise<HTMLImageElement> =>
  new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = reject
    image.src = src
  })

const canvasToBlob = (canvas: HTMLCanvasElement): Promise<Blob> =>
  new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('Failed to export sprite sheet'))
    }, 'image/png')
  })

const buildSpriteSheet = async (
  assets: GeneratedAsset[],
  request: GenerateRequest,
  fileNames: string[],
) => {
  const images = await Promise.all(assets.map((asset) => loadImage(asset.dataUrl)))
  const cellSize = Math.max(...assets.map((asset) => asset.size))
  const columns = Math.ceil(Math.sqrt(images.length))
  const rows = Math.ceil(images.length / columns)
  const canvas = document.createElement('canvas')
  canvas.width = columns * cellSize
  canvas.height = rows * cellSize

  const context = canvas.getContext('2d')
  if (!context) throw new Error('Canvas is not available')
  context.imageSmoothingEnabled = false
  context.clearRect(0, 0, canvas.width, canvas.height)

  const frames = images.map((image, index) => {
    const column = index % columns
    const row = Math.floor(index / columns)
    const x = column * cellSize
    const y = row * cellSize
    context.drawImage(image, x, y, cellSize, cellSize)

    return {
      name: fileNames[index].replace(/\.png$/i, ''),
      sourceFile: `images/${fileNames[index]}`,
      x,
      y,
      width: cellSize,
      height: cellSize,
      originalWidth: assets[index].size,
      originalHeight: assets[index].size,
      seed: assets[index].seed,
      assetType: assets[index].assetType,
      style: assets[index].style,
    }
  })

  const manifest = {
    version: 1,
    project: request.projectName,
    targetEngine: request.targetEngine,
    image: 'spritesheet/spritesheet.png',
    exportedAt: new Date().toISOString(),
    sheet: {
      width: canvas.width,
      height: canvas.height,
      cellSize,
      columns,
      rows,
    },
    frames,
  }

  return {
    blob: await canvasToBlob(canvas),
    manifest,
  }
}

const engineGuide = (request: GenerateRequest) => {
  const engineGuides: Record<TargetEngine, string[]> = {
    unity: [
      'Copy `images/` or `spritesheet/spritesheet.png` into `Assets/Art/Generated`.',
      'Select `spritesheet.png`, set Texture Type to `Sprite (2D and UI)`, Sprite Mode to `Multiple`, then slice by cell size from `spritesheet.json`.',
      'Use the frame names from `spritesheet.json` when building Sprite Atlas, prefabs, inventory icons, or Tile Palette assets.',
    ],
    godot: [
      'Copy this folder into `res://art/generated/`.',
      'Use individual files from `images/` with Sprite2D, TextureRect, or Button nodes.',
      'For atlas usage, load `spritesheet/spritesheet.png` and map regions using `spritesheet.json` frame coordinates.',
    ],
    cocos: [
      'Copy `images/` or `spritesheet/` into `assets/resources/generated`.',
      'Create SpriteFrame resources from each PNG, or use `spritesheet.json` to map atlas frames in a custom loader.',
      'Keep the generated file names stable so scene references survive future exports.',
    ],
    tiled: [
      'Use individual PNG files for object layers, or import `spritesheet/spritesheet.png` as an external tileset.',
      'Set tile width and height to the `cellSize` recorded in `spritesheet.json`.',
      'For map tiles, prefer square power-of-two sizes and keep naming prefixes aligned with map layers.',
    ],
    aseprite: [
      'Open `spritesheet/spritesheet.png` in Aseprite for manual cleanup.',
      'Use `spritesheet.json` to identify frame regions and original generated names.',
      'Export refined frames with the same prefix to preserve engine references.',
    ],
  }

  return [
    `# ${request.projectName} import guide`,
    '',
    `Target engine: ${request.targetEngine}`,
    `Naming prefix: ${request.namingPrefix || 'not set'}`,
    '',
    ...engineGuides[request.targetEngine].map((step, index) => `${index + 1}. ${step}`),
    '',
    'Package contents:',
    '',
    '- `images/`: individual PNG files',
    '- `spritesheet/spritesheet.png`: generated atlas image',
    '- `spritesheet/spritesheet.json`: frame coordinates and source mapping',
    '- `metadata.json`: prompts, seeds, style pack, request, and quality checks',
  ].join('\n')
}

export const exportZipPackage = async (
  assets: GeneratedAsset[],
  request: GenerateRequest,
  qualityChecks: QualityCheck[] = [],
) => {
  const zip = new JSZip()
  const imageFolder = zip.folder('images')
  const spriteFolder = zip.folder('spritesheet')
  const fileNames = assets.map((asset, index) => assetFileName(asset, index, request))
  const spriteSheet = assets.length ? await buildSpriteSheet(assets, request, fileNames) : undefined

  await Promise.all(
    assets.map(async (asset, index) => {
      const blob = await dataUrlToBlob(asset.dataUrl)
      imageFolder?.file(fileNames[index], blob)
    }),
  )

  if (spriteSheet) {
    spriteFolder?.file('spritesheet.png', spriteSheet.blob)
    spriteFolder?.file('spritesheet.json', JSON.stringify(spriteSheet.manifest, null, 2))
  }

  zip.file(
    'metadata.json',
    JSON.stringify(
      {
        project: request.projectName,
        exportedAt: new Date().toISOString(),
        request,
        qualityChecks,
        spriteSheet: spriteSheet?.manifest,
        assets: assets.map(({ dataUrl, ...asset }, index) => ({
          ...asset,
          fileName: fileNames[index],
          imagePath: `images/${fileNames[index]}`,
        })),
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
      'The generated sprite sheet and frame manifest are stored under `/spritesheet`.',
      'Use `engine-import-guide.md` for target-engine import steps.',
      'Use `metadata.json` to map asset names, prompts, styles, sizes, seeds, and quality checks.',
    ].join('\n'),
  )

  zip.file('engine-import-guide.md', engineGuide(request))

  const blob = await zip.generateAsync({ type: 'blob' })
  saveAs(blob, `${safeName(request.projectName)}-asset-pack.zip`)
}

export const exportSpriteSheet = async (assets: GeneratedAsset[], projectName: string) => {
  if (!assets.length) return

  const request: GenerateRequest = {
    projectName,
    description: '',
    assetType: assets[0].assetType,
    style: assets[0].style,
    size: assets[0].size,
    count: assets.length,
    transparentBackground: true,
    palette: 'ocean',
    consistencySeed: 'spritesheet-export',
    targetEngine: 'unity',
  }
  const fileNames = assets.map((asset, index) => assetFileName(asset, index, request))
  const spriteSheet = await buildSpriteSheet(assets, request, fileNames)
  saveAs(spriteSheet.blob, `${safeName(projectName)}-spritesheet.png`)
}
