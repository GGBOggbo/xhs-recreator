<script setup lang="ts">
defineProps<{
  content: any
  taskId: string
}>()
</script>

<template>
  <div class="card">
    <h2 class="card-title">原始内容预览</h2>

    <div v-if="content" class="preview-content">
      <div class="info-row">
        <span class="info-label">标题：</span>
        <span class="info-value">{{ content.title }}</span>
      </div>

      <div class="info-row">
        <span class="info-label">作者：</span>
        <span class="info-value">{{ content.author }}</span>
      </div>

      <div class="info-row">
        <span class="info-label">描述：</span>
        <p class="description">{{ content.description }}</p>
      </div>

      <div class="info-row">
        <span class="info-label">标签：</span>
        <div class="tags">
          <span v-for="tag in content.tags" :key="tag" class="tag">
            #{{ tag }}
          </span>
        </div>
      </div>

      <div v-if="content.images?.length" class="info-row">
        <span class="info-label">图片 ({{ content.images.length }}张)：</span>
        <div class="image-grid">
          <div
            v-for="(img, index) in content.images"
            :key="index"
            class="image-item"
          >
            <img :src="img" :alt="`图片 ${index + 1}`" />
          </div>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      <p>正在获取内容...</p>
    </div>
  </div>
</template>

<style scoped>
.preview-content {
  margin-top: 16px;
}

.info-row {
  margin-bottom: 16px;
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 8px;
}

.info-value {
  color: var(--text-color);
}

.description {
  color: var(--text-color);
  line-height: 1.8;
}

.tags {
  display: flex;
  flex-wrap: wrap;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
