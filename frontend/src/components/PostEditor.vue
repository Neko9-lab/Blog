<template>
  <div class="editor-container">
    <div class="editor-header">
      <el-button @click="goBack" plain round>⬅ 返回</el-button>
      <div class="header-actions">
        <el-select v-model="form.category_id" placeholder="选择发布节点" class="header-category" clearable>
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="submit" class="publish-btn" round>
          发布帖子
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
import { useRouter } from "vue-router";
import Vditor from "vditor";
import "vditor/dist/index.css";
import api from "../api";
import { useAuthStore } from "../store/auth";

const emit = defineEmits(["posted"]);
const router = useRouter();
const store = useAuthStore();

const form = reactive({ title: "", content: "", category_id: null });
const categories = ref([]);
const editorRef = ref(null);
const editor = ref(null);
const editorLoading = ref(true);

const toolbarNameMap = {
  emoji: "表情",
  head: "标题",
  bold: "加粗",
  italic: "斜体",
  strike: "删除线",
  link: "链接",
  list: "无序列表",
  "ordered-list": "有序列表",
  check: "任务列表",
  outdent: "减少缩进",
  indent: "增加缩进",
  quote: "引用",
  line: "分割线",
  code: "代码块",
  "inline-code": "行内代码",
  "insert-before": "上方插入",
  "insert-after": "下方插入",
  upload: "上传图片",
  record: "录音",
  table: "表格",
  undo: "撤销",
  redo: "重做",
  both: "编辑预览",
  preview: "预览",
  fullscreen: "全屏",
  "edit-mode": "编辑模式",
  export: "导出",
  outline: "大纲",
  help: "帮助",
  info: "说明",
  br: "换行",
};

const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const loadCategories = async () => {
  try {
    const resp = await api.get("/api/v1/categories");
    categories.value = resp.data || [];
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "分类加载失败"));
  }
};

const applyToolbarTitles = () => {
  const toolbarItems = editorRef.value?.querySelectorAll(".vditor-toolbar button, .vditor-toolbar .vditor-tooltipped");
  toolbarItems?.forEach((item) => {
    const ariaLabel = item.getAttribute("aria-label");
    const dataType = item.getAttribute("data-type");
    const title = ariaLabel || toolbarNameMap[dataType] || item.textContent?.trim() || "编辑器功能";
    item.setAttribute("title", title);
  });
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
      applyToolbarTitles();
    },
    input: (value) => {
      form.content = value;
    },
    upload: {
      accept: "image/*",
      url: `${import.meta.env.VITE_API_BASE || ""}/api/v1/uploads`,
      setHeaders: () => {
        const t = store.token || localStorage.getItem("token") || "";
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
  if (!store.token) {
    ElMessage.warning("请先登录再操作");
    router.push("/login");
    return;
  }
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning("标题和内容不能为空");
    return;
  }
  const payload = { title: form.title, content: form.content };
  if (form.category_id) {
    payload.category_id = form.category_id;
  }
  try {
    await api.post("/api/v1/posts", payload);
    ElMessage.success("发布成功！");
    emit("posted");
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "发布遇到问题"));
  }
};

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
};

onMounted(() => {
  initEditor();
  loadCategories();
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
