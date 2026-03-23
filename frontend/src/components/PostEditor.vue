<template>
  <div class="editor">
    <div class="page-header">
      <div class="page-title">发布帖子</div>
      <el-button size="small" @click="goBack">返回</el-button>
    </div>
    <el-form class="post-form" @submit.prevent="submit">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="请输入标题" />
      </el-form-item>
      <el-form-item label="内容">
        <div class="vditor-wrap">
          <div ref="editorRef"></div>
        </div>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category_id" placeholder="请选择分类" class="category-select">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <div class="form-actions">
        <el-button type="primary" @click="submit">发布</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, reactive, ref } from "vue";
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

const loadCategories = async () => {
  const resp = await api.get("/api/v1/categories");
  categories.value = resp.data || [];
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

const initEditor = () => {
  editor.value = new Vditor(editorRef.value, {
    height: 360,
    mode: "ir",
    cache: { enable: false },
    value: form.content,
    input: (value) => {
      form.content = value;
    },
    upload: {
      handler: uploadImages,
    },
  });
};

const submit = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再发帖");
    router.push("/login");
    return;
  }
  if (!form.title || !form.content) {
    ElMessage.warning("标题和内容不能为空");
    return;
  }
  const payload = { title: form.title, content: form.content };
  if (form.category_id) {
    payload.category_id = form.category_id;
  }
  try {
    await api.post("/api/v1/posts", payload);
    ElMessage.success("发布成功");
    emit("posted");
  } catch (err) {
    const msg = err?.response?.data?.msg || "发布失败";
    ElMessage.error(msg);
  }
};

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
};

onMounted(async () => {
  await loadCategories();
  initEditor();
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<style scoped>
.editor {
  max-width: 980px;
  margin: 24px auto;
  padding: 0 16px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-title {
  font-size: 22px;
  font-weight: 600;
}
.post-form :deep(.el-form-item__label) {
  width: 80px;
  color: #475569;
}
.post-form :deep(.el-form-item) {
  margin-bottom: 18px;
}
.category-select {
  width: 240px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.vditor-wrap {
  border: 1px solid #e6e8ee;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}
.post-form :deep(.vditor-toolbar__item) {
  position: relative;
}
.post-form :deep(.vditor-toolbar__item[aria-label]:hover::after) {
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
}
</style>
