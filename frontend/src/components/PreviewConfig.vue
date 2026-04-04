<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../utils/auth'

const props = defineProps<{
  content: any
}>()

const emit = defineEmits<{
  (e: 'start-recreate', taskId: string): void
  (e: 'back'): void
}>()

// 配置参数
const userPrompt = ref('')
const imageModel = ref('nano-banana-2')
const imageRatio = ref('3:4')
const imageStyleId = ref('notebook')
const loading = ref(false)
const error = ref('')

// 风格列表（从后端获取）
const imageStyles = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await api.get('/api/image-styles')
    imageStyles.value = res.data.styles || []
  } catch {
    // fallback 硬编码
    imageStyles.value = [
      { id: 'notebook', name: '学霸笔记风', description: '手绘涂鸦 + 莫兰迪色系' },
      { id: 'whiteboard', name: '白板纪实风', description: '真实白板 + 干擦记号笔 + 办公室纪实' },
    ]
  }
})

// 图片选择
const selectedImages = ref<number[]>([])

// 全选/取消全选
const toggleSelectAll = () => {
  const totalImages = props.content?.images?.length || 0
  if (selectedImages.value.length === totalImages) {
    // 已全选，取消全选
    selectedImages.value = []
  } else {
    // 未全选，全选
    selectedImages.value = Array.from({ length: totalImages }, (_, i) => i)
  }
}

// 是否全选
const isAllSelected = computed(() => {
  const totalImages = props.content?.images?.length || 0
  return totalImages > 0 && selectedImages.value.length === totalImages
})

// 切换图片选择
const toggleImage = (index: number) => {
  const idx = selectedImages.value.indexOf(index)
  if (idx > -1) {
    selectedImages.value.splice(idx, 1)
  } else {
    selectedImages.value.push(index)
  }
}

// 图片生成模型选项
const imageModelOptions = [
  { value: 'nano-banana-2', label: 'Banana 2', desc: '标准模型，性价比高', icon: 'auto_awesome' },
  { value: 'nano-banana-pro', label: 'Banana Pro', desc: '专业模型，效果更好', icon: 'palette' },
]

// 图片比例选项（优化版：6个常用比例）
const ratioOptions = [
  { value: 'auto', label: '自动', width: 4, height: 4 },
  { value: '1:1', label: '1:1', width: 4, height: 4 },
  { value: '3:4', label: '3:4', width: 3, height: 4 },
  { value: '4:3', label: '4:3', width: 4, height: 3 },
  { value: '9:16', label: '9:16', width: 3, height: 5 },
  { value: '16:9', label: '16:9', width: 5, height: 3 },
]

const selectedCount = computed(() => selectedImages.value.length)

const handleStartRecreate = async () => {
  if (selectedImages.value.length === 0) {
    error.value = '请至少选择一张图片'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await api.post('/api/task', {
      url: props.content.url,
      image_count: selectedImages.value.length,
      selected_indices: selectedImages.value,
      user_prompt: userPrompt.value,
      image_model: imageModel.value,
      image_ratio: imageRatio.value,
      image_style_id: imageStyleId.value,
    })

    emit('start-recreate', response.data.task_id)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建任务失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="preview-section">
    <!-- 步骤引导 -->
    <div class="step-indicator">
      <div class="step-item completed">
        <span class="step-number">1</span>
        <span class="step-label">链接导入</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step-item active">
        <span class="step-number">2</span>
        <span class="step-label">内容解析</span>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <span class="step-number">3</span>
        <span class="step-label">重塑创作</span>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <span class="step-number">4</span>
        <span class="step-label">成果展示</span>
      </div>
    </div>

    <div class="preview-grid">
      <!-- 左侧：原始内容预览 -->
      <section class="original-section">
        <div class="section-header">
          <span class="step-badge">STEP 02</span>
          <h2 class="section-title">原始内容预览</h2>
        </div>

        <div class="preview-card">
          <!-- 标题 -->
          <div class="content-block">
            <label class="block-label">原始标题</label>
            <h3 class="content-title">{{ content.title || '无标题' }}</h3>
          </div>

          <!-- 正文 -->
          <div class="content-block">
            <label class="block-label">原始内容</label>
            <p class="content-text">{{ content.description || '无正文' }}</p>
          </div>

          <!-- 标签 -->
          <div class="content-block tags-block" v-if="content.tags?.length">
            <span v-for="tag in content.tags" :key="tag" class="content-tag">#{{ tag }}</span>
          </div>

          <!-- 图片选择 -->
          <div class="content-block images-block" v-if="content.images?.length">
            <div class="images-header">
              <label class="block-label">选择待转换图片 (已选 {{ selectedCount }})</label>
              <button class="select-all-btn" @click="toggleSelectAll">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="select-all-icon">
                  <path v-if="isAllSelected" d="M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  <path v-else d="M9 11l3 3L22 4"/>
                </svg>
                {{ isAllSelected ? '取消全选' : '全选' }}
              </button>
            </div>
            <div class="images-grid">
              <div
                v-for="(img, index) in content.images.slice(0, 9)"
                :key="index"
                class="image-card"
                :class="{ selected: selectedImages.includes(index) }"
                @click="toggleImage(index)"
              >
                <img :src="img" :alt="`图片 ${index + 1}`" loading="lazy" />
                <div class="image-overlay" v-if="selectedImages.includes(index)">
                  <svg viewBox="0 0 24 24" fill="currentColor" class="check-icon">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧：配置 -->
      <section class="config-section">
        <!-- 文案二创配置 -->
        <div class="config-block">
          <h2 class="config-title">文案二创配置</h2>
          <div class="config-card">
            <div class="config-header">
              <label class="config-label">自定义提示词 (可选)</label>
              <span class="ai-badge">AI 智能辅助</span>
            </div>
            <textarea
              v-model="userPrompt"
              class="config-textarea"
              placeholder="例如：语气更幽默一些，突出性价比，增加表情符号..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- 图片二创配置 -->
        <div class="config-block">
          <h2 class="config-title">图片二创配置</h2>
          <div class="config-card">
            <!-- 模型选择 -->
            <div class="config-row">
              <label class="config-label">选择图片模型</label>
              <div class="model-grid">
                <button
                  v-for="opt in imageModelOptions"
                  :key="opt.value"
                  class="model-btn"
                  :class="{ active: imageModel === opt.value }"
                  @click="imageModel = opt.value"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="model-icon">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                  <span class="model-name">{{ opt.label }}</span>
                  <span class="model-desc">{{ opt.desc }}</span>
                </button>
              </div>
            </div>

            <!-- 风格选择 -->
            <div class="config-row" v-if="imageStyles.length > 1">
              <label class="config-label">图片风格</label>
              <div class="style-grid">
                <button
                  v-for="style in imageStyles"
                  :key="style.id"
                  class="style-btn"
                  :class="{ active: imageStyleId === style.id }"
                  @click="imageStyleId = style.id"
                >
                  <span class="style-name">{{ style.name }}</span>
                  <span class="style-desc">{{ style.description }}</span>
                </button>
              </div>
            </div>

            <!-- 比例选择 -->
            <div class="config-row">
              <label class="config-label">输出图像比例</label>
              <div class="ratio-grid">
                <button
                  v-for="opt in ratioOptions"
                  :key="opt.value"
                  class="ratio-btn"
                  :class="{ active: imageRatio === opt.value }"
                  @click="imageRatio = opt.value"
                >
                  <div
                    class="ratio-preview"
                    :style="{ width: opt.width * 4 + 'px', height: opt.height * 4 + 'px' }"
                  ></div>
                  <span class="ratio-label">{{ opt.label }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-message">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="error-icon">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
        </div>

        <!-- 开始按钮 -->
        <button
          class="start-btn"
          :disabled="loading || selectedCount === 0"
          @click="handleStartRecreate"
        >
          <svg v-if="loading" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"/>
          </svg>
          <span v-else>🚀</span>
          <span>{{ loading ? '创建中...' : '开始二创' }}</span>
        </button>
        <p class="btn-hint">预计生成时间约 15 秒</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.preview-section {
  padding: 0 20px 60px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 步骤引导 */
.step-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 40px;
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
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.step-item.active .step-label {
  color: var(--text-primary);
}

.step-line {
  width: 48px;
  height: 1px;
  background: var(--border-color);
  opacity: 0.3;
}

.step-line.active {
  background: var(--primary-color);
  opacity: 0.5;
}

/* 网格布局 */
.preview-grid {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 32px;
}

@media (max-width: 1024px) {
  .preview-grid {
    grid-template-columns: 1fr;
  }
}

/* 左侧预览 */
.original-section {
  min-width: 0;
}

.section-header {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 24px;
}

.step-badge {
  font-size: 12px;
  font-weight: 700;
  color: var(--primary-color);
  background: rgba(230, 0, 35, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

.section-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.preview-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 32px;
  box-shadow: var(--shadow-lg);
}

.content-block {
  margin-bottom: 24px;
}

.content-block:last-child {
  margin-bottom: 0;
}

.block-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.content-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0;
}

.content-text {
  font-size: 15px;
  color: var(--text-color);
  line-height: 1.7;
  margin: 0;
  white-space: pre-wrap;
}

.tags-block {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.content-tag {
  display: inline-block;
  padding: 6px 14px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 20px;
  font-size: 13px;
}

/* 图片网格 */
.images-block {
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.images-header .block-label {
  margin-bottom: 0;
}

.select-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color);
  background: rgba(230, 0, 35, 0.08);
  border: 1px solid rgba(230, 0, 35, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.select-all-btn:hover {
  background: rgba(230, 0, 35, 0.12);
  border-color: rgba(230, 0, 35, 0.3);
}

.select-all-icon {
  width: 14px;
  height: 14px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.image-card {
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.image-card:hover {
  border-color: rgba(230, 0, 35, 0.3);
}

.image-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(230, 0, 35, 0.2);
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-card.selected img {
  opacity: 1;
}

.image-card:not(.selected) img {
  opacity: 0.6;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(230, 0, 35, 0.2);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 8px;
}

.check-icon {
  width: 20px;
  height: 20px;
  color: white;
}

/* 右侧配置 */
.config-section {
  position: sticky;
  top: 100px;
  height: fit-content;
}

.config-block {
  margin-bottom: 32px;
}

.config-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 24px;
}

.config-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.ai-badge {
  font-size: 10px;
  color: var(--text-muted);
  padding: 2px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.config-textarea {
  width: 100%;
  min-height: 100px;
  padding: 16px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: none;
  border-radius: 8px;
  resize: none;
  outline: none;
  transition: box-shadow 0.2s;
}

.config-textarea::placeholder {
  color: var(--text-muted);
}

.config-textarea:focus {
  box-shadow: 0 0 0 2px rgba(230, 0, 35, 0.2);
}

.config-row {
  margin-bottom: 20px;
}

.config-row:last-child {
  margin-bottom: 0;
}

.config-row .config-label {
  margin-bottom: 12px;
  display: block;
}

/* 模型选择 */
.model-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.model-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.model-btn:hover {
  border-color: var(--border-color);
}

.model-btn.active {
  border-color: var(--primary-color);
}

.model-icon {
  width: 24px;
  height: 24px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.model-btn.active .model-icon {
  color: var(--primary-color);
}

.model-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.model-desc {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* 风格选择 */
.style-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.style-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 10px;
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.style-btn:hover {
  border-color: var(--border-color);
}

.style-btn.active {
  border-color: var(--primary-color);
}

.style-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.style-desc {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
  text-align: center;
}

/* 比例选择 */
.ratio-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ratio-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: var(--bg-primary);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 52px;
}

.ratio-btn:hover {
  border-color: var(--border-color);
}

.ratio-btn.active {
  border-color: var(--primary-color);
}

.ratio-preview {
  border: 2px solid var(--text-muted);
  border-radius: 2px;
  margin-bottom: 6px;
}

.ratio-btn.active .ratio-preview {
  border-color: var(--primary-color);
}

.ratio-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.ratio-btn.active .ratio-label {
  color: var(--primary-color);
}

/* 错误提示 */
.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--error-color);
  padding: 14px 16px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 10px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  font-size: 14px;
  margin-bottom: 16px;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  padding: 18px 24px;
  font-size: 18px;
  font-weight: 700;
  color: white;
  background: var(--primary-gradient);
  border: none;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: var(--shadow-btn);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.25s;
}

.start-btn:hover:not(:disabled) {
  transform: scale(1.02);
}

.start-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.start-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .preview-section {
    padding: 0 16px 40px;
  }

  .step-indicator {
    gap: 8px;
  }

  .step-label {
    display: none;
  }

  .step-line {
    width: 24px;
  }

  .section-title,
  .config-title {
    font-size: 24px;
  }

  .preview-card {
    padding: 20px;
  }

  .images-grid {
    gap: 8px;
  }

  .model-grid {
    grid-template-columns: 1fr;
  }

  .ratio-grid {
    justify-content: center;
  }

  .config-section {
    position: static;
  }
}
</style>
