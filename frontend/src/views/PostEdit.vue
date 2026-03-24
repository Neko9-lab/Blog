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
      accept: "image/*",
      url: `${import.meta.env.VITE_API_BASE || ""}/api/v1/uploads`,
      setHeaders: () => {
        const t = localStorage.getItem("token") || "";
        return t ? { Authorization: `Bearer ${t}` } : {};
      },
      fieldName: "file",
      format: (files, responseText) => {
        let res;
        try {
          res = JSON.parse(responseText);
        } catch { return responseText; }
        const url = res.data?.url || "";
        const apiBase = import.meta.env.VITE_API_BASE || "";
        const fullUrl = url.startsWith("http") ? url : `${apiBase}${url}`;
        const name = files.length > 0 ? files[0].name : "image.png";
        return JSON.stringify({
          msg: res.msg || "",
          code: res.code === 200 ? 0 : 1,
          data: {
            errFiles: [],
            succMap: { [name]: fullUrl }
          }
        });
      }
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
  border-radius: 6px;
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
  transition: all 0.2s ease;
}
.publish-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  color: #fff;
}

.editor-paper {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  border: 1px solid #e2e8f0;
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.title-input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  padding: 8px 0;
  margin-bottom: 24px;
  background: transparent;
  transition: color 0.2s;
}
.title-input::placeholder {
  color: #94a3b8;
  font-weight: 600;
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
