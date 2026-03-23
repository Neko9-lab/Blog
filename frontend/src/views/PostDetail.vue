<template>
  <div class="detail">
    <el-card class="post-card" shadow="never">
      <h2 class="title">{{ post.title }}</h2>
      <div class="meta">
        <div class="author">
          <img v-if="post.author_avatar" :src="post.author_avatar" class="avatar" />
          <div v-else class="avatar avatar-fallback">{{ (post.author_name || "U").slice(0, 1) }}</div>
          <span>{{ post.author_name || post.author_id }}</span>
        </div>
        <span>点赞：{{ post.like_count || 0 }}</span>
        <span>收藏：{{ post.favorite_count || 0 }}</span>
      </div>
      <div class="content" v-html="rendered"></div>
      <div class="actions">
        <el-button size="small" @click="like">点赞</el-button>
        <el-button size="small" @click="favorite">收藏</el-button>
        <el-button v-if="canEdit" size="small" @click="goEdit">编辑</el-button>
      </div>
    </el-card>

    <el-card class="comment-card" shadow="never">
      <template #header>评论</template>
      <el-alert v-if="!site.comment_enabled" type="warning" title="评论已关闭" show-icon />
      <el-form v-else @submit.prevent="addComment">
        <el-form-item>
          <el-input v-model="comment" placeholder="发表评论" />
        </el-form-item>
        <el-button type="primary" @click="addComment">提交</el-button>
      </el-form>
      <el-divider />
      <div v-for="c in comments" :key="c.id" class="comment" :style="{ marginLeft: (c.level - 1) * 16 + 'px' }">
        <div class="comment-header">
          <img v-if="c.avatar_url" :src="c.avatar_url" class="avatar-sm" />
          <div v-else class="avatar-sm avatar-fallback">{{ (c.display_name || "U").slice(0, 1) }}</div>
          <strong>{{ c.display_name || c.username }}</strong>
        </div>
        <div class="comment-body">{{ c.content }}</div>
        <div class="comment-actions">
          <el-button size="small" text @click="openEdit(c)">编辑</el-button>
          <el-button size="small" text type="danger" @click="confirmDelete(c)">删除</el-button>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="editVisible" title="编辑评论" width="400px">
      <el-input v-model="editContent" type="textarea" rows="4" />
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { marked } from "marked";
import api from "../api";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

const route = useRoute();
const router = useRouter();
const store = useAuthStore();
const post = ref({ title: "", content: "", like_count: 0, favorite_count: 0, author_id: 0, author_name: "" });
const comments = ref([]);
const comment = ref("");
const site = ref({ site_name: "BlogForum", announcement: "", comment_enabled: true });

const editVisible = ref(false);
const editContent = ref("");
const editTarget = ref(null);

const rendered = computed(() => marked.parse(post.value.content || ""));

const canEdit = computed(() => {
  if (!store.user) return false;
  return store.user.is_admin || store.user.id === post.value.author_id;
});

const load = async () => {
  const resp = await api.get(`/api/v1/posts/${route.params.id}`);
  post.value = resp.data || post.value;
  const c = await api.get("/api/v1/comments", { params: { post_id: route.params.id } });
  comments.value = c.data || [];
  const cfg = await api.get("/api/v1/config");
  site.value = cfg.data || site.value;
};

const like = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再点赞");
    router.push("/login");
    return;
  }
  await api.post(`/api/v1/posts/${route.params.id}/like`);
  await load();
};

const favorite = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再收藏");
    router.push("/login");
    return;
  }
  await api.post(`/api/v1/posts/${route.params.id}/favorite`);
  await load();
};

const goEdit = () => {
  router.push(`/posts/${route.params.id}/edit`);
};

const addComment = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再评论");
    router.push("/login");
    return;
  }
  try {
    await api.post("/api/v1/comments", { post_id: Number(route.params.id), content: comment.value });
    comment.value = "";
    await load();
  } catch (err) {
    const msg = err?.response?.data?.msg || "评论失败";
    ElMessage.error(msg);
  }
};

const openEdit = (c) => {
  if (!store.token) return;
  editTarget.value = c;
  editContent.value = c.content;
  editVisible.value = true;
};

const saveEdit = async () => {
  if (!editTarget.value) return;
  await api.put(`/api/v1/comments/${editTarget.value.id}`, { content: editContent.value });
  editVisible.value = false;
  await load();
};

const confirmDelete = async (c) => {
  if (!store.token) return;
  try {
    await ElMessageBox.confirm("确认删除这条评论吗？", "提示", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning",
    });
    await api.delete(`/api/v1/comments/${c.id}`);
    await load();
  } catch {
    return;
  }
};

onMounted(load);
</script>

<style scoped>
.detail {
  max-width: 900px;
  margin: 24px auto;
  display: grid;
  gap: 16px;
}
.post-card .title {
  margin: 0 0 8px 0;
}
.meta {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}
.author {
  display: flex;
  align-items: center;
  gap: 6px;
}
.content {
  line-height: 1.6;
}
.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}
.comment {
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}
.comment-header {
  font-size: 13px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}
.comment-body {
  margin: 4px 0;
}
.comment-actions {
  display: flex;
  gap: 8px;
}
.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}
.avatar-sm {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}
.avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  color: #334155;
  font-size: 12px;
  font-weight: 600;
}
</style>
