<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  original: any
  result: any
}>()

const emit = defineEmits<{
  (e: 'reset'): void
}>()

// 当前选中的标题索引
const selectedTitleIndex = ref(0)

// 图片预览
const previewImage = ref<string | null>(null)

// 所有标题选项
const titleOptions = computed(() => {
  return props.result?.generated_titles || []
})

// 当前选中的标题
const selectedTitle = computed(() => {
  if (titleOptions.value.length > 0) {
    return titleOptions.value[selectedTitleIndex.value]
  }
  return { title: props.result?.generated_title || '', type: '', trigger: '' }
})

// 选择标题
const selectTitle = (index: number) => {
  selectedTitleIndex.value = index
}

// 打开图片预览
const openPreview = (img: string) => {
  previewImage.value = img
  document.body.style.overflow = 'hidden'
}

// 关闭图片预览
const closePreview = () => {
  previewImage.value = null
  document.body.style.overflow = ''
}

// 复制到剪贴板
const copyToClipboard = async (text: string, msg?: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert(msg || '已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert(msg || '已复制到剪贴板')
  }
}

// 复制标题
const copyTitle = async (title: string, event?: Event) => {
  if (event) event.stopPropagation()
  await copyToClipboard(title, '标题已复制')
}

// 复制文案
const copyContent = async () => {
  await copyToClipboard(props.result?.generated_desc || '', '文案已复制')
}

// 复制所有标签
const copyAllTags = async () => {
  const tags = props.original?.tags?.map((t: string) => `#${t}`).join(' ') || ''
  await copyToClipboard(tags, '标签已复制')
}

// 下载图片
const downloadImage = (url: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = url.split('/').pop() || 'image.png'
  link.click()
}

// 当前预览的图片索引
const currentImageIndex = ref(0)

// 所有生成的图片
const generatedImages = computed(() => {
  return props.result?.generated_images || []
})

// 上一张
const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  } else {
    currentImageIndex.value = generatedImages.value.length - 1
  }
  previewImage.value = generatedImages.value[currentImageIndex.value]
}

// 下一张
const nextImage = () => {
  if (currentImageIndex.value < generatedImages.value.length - 1) {
    currentImageIndex.value++
  } else {
    currentImageIndex.value = 0
  }
  previewImage.value = generatedImages.value[currentImageIndex.value]
}

// 打开预览时设置当前索引
const openPreviewWithIndex = (index: number) => {
  currentImageIndex.value = index
  previewImage.value = generatedImages.value[index]
  document.body.style.overflow = 'hidden'
}

// 键盘事件处理
const handleKeydown = (e: KeyboardEvent) => {
  if (!previewImage.value) return

  if (e.key === 'ArrowLeft') {
    prevImage()
  } else if (e.key === 'ArrowRight') {
    nextImage()
  } else if (e.key === 'Escape') {
    closePreview()
  }
}

// 监听键盘事件
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="result-page">
    <!-- 步骤引导 -->
    <div class="step-indicator">
      <div class="step-item completed">
        <span class="step-number">1</span>
        <span class="step-label">链接导入</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step-item completed">
        <span class="step-number">2</span>
        <span class="step-label">内容解析</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step-item completed">
        <span class="step-number">3</span>
        <span class="step-label">重塑创作</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step-item completed">
        <span class="step-number">4</span>
        <span class="step-label">成果展示</span>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 选择标题模块 -->
      <section class="module">
        <div class="module-header">
          <span class="module-tag">SELECT TITLE</span>
          <h2 class="module-title">选择标题</h2>
        </div>
        <div class="title-grid" v-if="titleOptions.length > 0">
          <div
            v-for="(opt, index) in titleOptions"
            :key="index"
            class="title-card"
            :class="{ selected: selectedTitleIndex === index }"
            @click="selectTitle(index)"
          >
            <span class="title-emoji">✨</span>
            <span class="title-text">{{ opt.title }}</span>
            <div class="title-actions">
              <button class="title-copy-btn" @click="copyTitle(opt.title, $event)" title="复制标题">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
              <svg v-if="selectedTitleIndex === index" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
          </div>
        </div>
        <div v-else class="title-card selected">
          <span class="title-emoji">🔍</span>
          <span class="title-text">{{ result?.generated_title || '生成中...' }}</span>
          <button class="title-copy-btn" @click="copyTitle(result?.generated_title || '', $event)" title="复制标题">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </button>
        </div>
      </section>

      <!-- 新文案模块 -->
      <section class="module">
        <div class="module-header-row">
          <div class="module-header-left">
            <span class="module-tag">NEW COPY</span>
            <h2 class="module-title">新文案</h2>
          </div>
          <button class="copy-btn" @click="copyContent">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="copy-icon">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            复制
          </button>
        </div>
        <div class="copy-card">
          <p class="copy-text">{{ result?.generated_desc || '生成中...' }}</p>
        </div>
      </section>

      <!-- 继续二创按钮 -->
      <div class="continue-section">
        <button class="continue-btn" @click="emit('reset')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="plus-icon">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          继续二创
        </button>
      </div>

      <!-- 标签模块 -->
      <section class="module">
        <div class="module-header-row">
          <div class="module-header-left">
            <span class="module-tag">TRENDING TAGS</span>
            <h2 class="module-title">标签</h2>
          </div>
          <button class="copy-btn" @click="copyAllTags">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="copy-icon">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            复制全部
          </button>
        </div>
        <div class="tags-flow">
          <span v-for="tag in original?.tags" :key="tag" class="tag-item">
            #{{ tag }}
          </span>
        </div>
      </section>

      <!-- 生成图片模块 -->
      <section class="module" v-if="generatedImages.length > 0">
        <div class="module-header">
          <span class="module-tag">GENERATED VISUALS</span>
          <h2 class="module-title">生成图片</h2>
        </div>

        <!-- 单张大图展示 -->
        <div class="main-image-container" @click="openPreviewWithIndex(0)">
          <img :src="generatedImages[0]" alt="生成图片" class="main-image" />
          <div class="image-count" v-if="generatedImages.length > 1">
            +{{ generatedImages.length - 1 }}
          </div>
        </div>

        <!-- 多图缩略图 -->
        <div class="thumbnail-row" v-if="generatedImages.length > 1">
          <div
            v-for="(img, index) in generatedImages.slice(0, 4)"
            :key="index"
            class="thumbnail-item"
            @click="openPreviewWithIndex(index)"
          >
            <img :src="img" :alt="`图片 ${index + 1}`" />
          </div>
        </div>
      </section>
    </div>

    <!-- 图片预览模态框 -->
    <Teleport to="body">
      <div v-if="previewImage" class="preview-modal" @click="closePreview">
        <div class="preview-content" @click.stop>
          <button class="preview-close" @click="closePreview">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>

          <img :src="previewImage" alt="预览图片" class="preview-image" />

          <div class="preview-nav" v-if="generatedImages.length > 1">
            <button class="nav-btn prev" @click="prevImage">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <span class="nav-info">{{ currentImageIndex + 1 }} / {{ generatedImages.length }}</span>
            <button class="nav-btn next" @click="nextImage">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>

          <div class="preview-actions">
            <button class="preview-action-btn" @click="downloadImage(previewImage)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              下载图片
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.result-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

/* 步骤引导 */
.step-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
  padding-top: 20px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.4;
}

.step-item.active {
  opacity: 1;
}

.step-item.completed {
  opacity: 1;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
}

.step-item.active .step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.step-item.completed .step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.step-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.step-item.active .step-label,
.step-item.completed .step-label {
  color: var(--text-primary);
}

.step-line {
  width: 32px;
  height: 1px;
  background: var(--border-color);
  opacity: 0.3;
}

.step-line.completed {
  background: var(--primary-color);
  opacity: 0.5;
}

@media (max-width: 768px) {
  .step-indicator {
    gap: 8px;
  }

  .step-label {
    display: none;
  }

  .step-line {
    width: 24px;
  }
}

/* 内容区 */
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 模块通用 */
.module {
  display: flex;
  flex-direction: column;
}

.module-header {
  margin-bottom: 24px;
}

.module-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.module-header-left {
  display: flex;
  flex-direction: column;
}

.module-tag {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.module-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

/* 复制按钮 */
.copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: var(--border-color);
}

.copy-icon {
  width: 14px;
  height: 14px;
}

/* 标题卡片网格 */
.title-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.title-grid .title-card:first-child:nth-last-child(1),
.title-grid .title-card:first-child:nth-last-child(2) ~ .title-card:last-child:nth-child(2) {
  grid-column: span 2;
}

.title-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 18px;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.title-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.title-card.selected {
  background: var(--bg-secondary);
  box-shadow: none;
}

.title-emoji {
  font-size: 16px;
  flex-shrink: 0;
}

.title-text {
  font-size: 15px;
  font-weight: 400;
  color: var(--text-color);
  line-height: 1.4;
  flex: 1;
}

.title-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.title-copy-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.2s;
  opacity: 0;
}

.title-card:hover .title-copy-btn {
  opacity: 1;
}

.title-copy-btn:hover {
  background: var(--bg-secondary);
  color: var(--primary-color);
}

.title-copy-btn svg {
  width: 14px;
  height: 14px;
}

.check-icon {
  width: 16px;
  height: 16px;
  color: var(--primary-color);
  flex-shrink: 0;
}

/* 文案卡片 */
.copy-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.copy-text {
  font-size: 15px;
  font-weight: 400;
  color: var(--text-color);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

/* 继续二创按钮 */
.continue-section {
  display: flex;
  justify-content: center;
}

.continue-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 32px;
  background: var(--bg-secondary);
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.continue-btn:hover {
  background: var(--border-color);
}

.plus-icon {
  width: 16px;
  height: 16px;
}

/* 标签流 */
.tags-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 400;
  color: var(--text-muted);
}

/* 主图容器 */
.main-image-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  aspect-ratio: 5/6;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-count {
  position: absolute;
  bottom: 16px;
  right: 16px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

/* 缩略图行 */
.thumbnail-row {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

.thumbnail-item {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s;
}

.thumbnail-item:hover {
  transform: scale(1.05);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 预览模态框 */
.preview-modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  cursor: zoom-out;
}

.preview-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: default;
}

.preview-close {
  position: absolute;
  top: -48px;
  right: 0;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.preview-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.preview-close svg {
  width: 24px;
  height: 24px;
  color: white;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.preview-nav {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.nav-btn {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-btn svg {
  width: 24px;
  height: 24px;
  color: white;
}

.nav-info {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.preview-actions {
  margin-top: 20px;
}

.preview-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #FFFFFF;
  color: #121212;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.preview-action-btn:hover {
  transform: scale(1.05);
  background: #F3F4F6;
}

.preview-action-btn svg {
  width: 18px;
  height: 18px;
}

/* 响应式 */
@media (max-width: 768px) {
  .step-indicator {
    gap: 8px;
  }

  .step-label {
    display: none;
  }

  .step-line {
    width: 24px;
  }

  .title-grid {
    grid-template-columns: 1fr;
  }

  .main-image-container {
    max-width: 100%;
  }

  .thumbnail-item {
    width: 60px;
    height: 60px;
  }
}
</style>
