<template>
  <div class="editor-container">
    <div class="editor-header">
      <el-button @click="goBack" plain round>⬅ 返回</el-button>
      <div class="header-actions">
        <el-select v-model="form.category_id" placeholder="选择发布节点" class="header-category" clearable>
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="submit" class="publish-btn" round>
          保存修改
        </el-button>
      </div>
    </div>
    
    <div class="editor-paper">
      <input 
        class="title-input" 
        v-model="form.title" 
        placeholder="输入一个吸睛的标题..." 
      />
      <div class="vditor-wrap" :class="{ 'is-loading': editorLoading }">
        <div v-if="editorLoading" class="editor-loading">编辑器装载中...</div>
        <div ref="editorRef" class="vditor-instance"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onBeforeUnmount, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import Vditor from "vditor";
import "vditor/dist/index.css";
import api from "../api";

const route = useRoute();
const router = useRouter();
const categories = ref([]);
const form = reactive({ title: "", content: "", category_id: null });
const editorRef = ref(null);
const editor = ref(null);
const editorLoading = ref(true);

const load = async () => {
  try {
    const resp = await api.get(`/api/v1/posts/${route.params.id}`);
    const post = resp.data || {};
    form.title = post.title || "";
    form.content = post.content || "";
    form.category_id = post.category_id || null;
    
    const c = await api.get("/api/v1/categories");
    categories.value = c.data || [];
    
    if (editor.value) {
      editor.value.setValue(form.content || "");
    }
  } catch (err) {
    ElMessage.error("加载帖子失败");
  }
};

const uploadImages = async (files) => {
  const apiBase = import.meta.env.VITE_API_BASE || "";
  for (const file of files) {
    const data = new FormData();
    data.append("file", file);
    try {
      const resp = await api.post("/api/v1/uploads", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const rawUrl = resp.data.url;
      const fullUrl = rawUrl.startsWith("http") ? rawUrl : `${apiBase}${rawUrl}`;
      editor.value?.insertValue(`\n![](${fullUrl})\n`);
    } catch (err) {
      const msg = err?.response?.data?.msg || "上传失败";
      ElMessage.error(msg);
    }
  }
};

const initEditor = async () => {
  await nextTick();
  if (!editorRef.value || editor.value) {
    editorLoading.value = false;
    return;
  }
  editor.value = new Vditor(editorRef.value, {
    height: 500,
    mode: "ir",
    cache: { enable: false },
    value: form.content,
    placeholder: "正文内容：支持 Markdown 语法，亦可直接粘贴图片...",
    after: () => {
      editorLoading.value = false;
    },
    input: (value) => {
      form.content = value;
    },
    upload: {
      handler: uploadImages,
    },
  });
};

const submit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning("标题和内容不能为空");
    return;
  }
  try {
    await api.put(`/api/v1/posts/${route.params.id}` , {
      title: form.title,
      content: form.content,
      category_id: form.category_id,
    });
    ElMessage.success("已保存");
    router.push(`/posts/${route.params.id}`);
  } catch (err) {
    const msg = err?.response?.data?.msg || "保存失败";
    ElMessage.error(msg);
  }
};

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push(`/posts/${route.params.id}`);
  }
};

onMounted(async () => {
  initEditor();
  await load();
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<style scoped>
.editor-container {
  max-width: 900px;
  margin: 32px auto;
  padding: 0 16px;
}
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}
.header-category {
  width: 140px;
}
.publish-btn {
  padding: 8px 24px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.2s;
}
.publish-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.editor-paper {
  background: #fff;
  border-radius: 12px;
  padding: 36px 48px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.8);
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.title-input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  padding: 8px 0;
  margin-bottom: 20px;
  background: transparent;
  transition: color 0.2s;
}
.title-input::placeholder {
  color: #cbd5e1;
  font-weight: 700;
}

.vditor-wrap {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.vditor-instance {
  flex: 1;
}

/* Override Vditor default themes to seamlessly blend in */
.vditor-wrap :deep(.vditor) {
  border: none !important;
  box-shadow: none !important;
}
.vditor-wrap :deep(.vditor-toolbar) {
  border-bottom: 1px solid #e2e8f0 !important;
  border-top: none !important;
  border-left: none !important;
  border-right: none !important;
  padding: 8px 0 12px 0 !important;
  background: transparent !important;
}
.vditor-wrap :deep(.vditor-content) {
  padding-top: 16px !important;
}
.vditor-wrap :deep(.vditor-reset) {
  font-family: inherit;
  font-size: 16px;
  line-height: 1.8;
  color: #334155;
}

.vditor-wrap.is-loading {
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 8px;
}
.editor-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.05em;
  z-index: 10;
}

/* Tooltip fixes for the toolbar */
.vditor-wrap :deep(.vditor-toolbar__item) {
  position: relative;
}
.vditor-wrap :deep(.vditor-toolbar__item[aria-label]:hover::after) {
  content: attr(aria-label);
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translate(-50%, 6px);
  background: rgba(15, 23, 42, 0.9);
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}

@media (max-width: 768px) {
  .editor-paper {
    padding: 24px;
  }
  .title-input {
    font-size: 24px;
    margin-bottom: 16px;
  }
}
</style>
