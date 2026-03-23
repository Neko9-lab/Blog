<template>
  <div class="detail-container">
    <div class="detail-main">
      <el-card class="post-card" shadow="never">
        <h2 class="title">{{ post.title }}</h2>
        <div class="meta">
          <div class="author">
            <img v-if="post.author_avatar" :src="post.author_avatar" class="avatar" />
            <div v-else class="avatar avatar-fallback">{{ (post.author_name || "U").slice(0, 1) }}</div>
            <div class="author-info">
              <span class="author-name">{{ post.author_name || `User${post.author_id}` }}</span>
              <span class="post-time" v-if="post.created_at">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
          <div class="stats">
            <span>👁 阅读 {{ post.view_count || 0 }}</span>
            <span>👍 点赞 {{ post.like_count || 0 }}</span>
            <span>⭐ 收藏 {{ post.favorite_count || 0 }}</span>
          </div>
        </div>
        <div class="content" v-html="rendered"></div>
        <div class="actions bottom-actions">
          <el-button :type="isLiked ? 'primary' : 'default'" @click="like">
            👍 点赞 {{ post.like_count || '' }}
          </el-button>
          <el-button :type="isFavorited ? 'warning' : 'default'" @click="toggleFavorite">
            ⭐ {{ isFavorited ? "已收藏" : "收藏" }}
          </el-button>
          <el-button @click="sharePost">🔗 分享</el-button>
          <el-button v-if="canEdit" @click="goEdit">✏️ 编辑</el-button>
        </div>
      </el-card>

      <el-card class="comment-card" shadow="never" id="comment-section">
        <template #header>评论 ({{ comments.length }})</template>
        <el-alert v-if="!site.comment_enabled" type="warning" title="评论已关闭" show-icon />
        <div v-else class="comment-input-wrapper" id="comment-input-area">
          <el-input 
            v-model="comment" 
            type="textarea" 
            :rows="3" 
            placeholder="发表友善的评论..." 
            ref="commentInputRef" 
            @keydown.ctrl.enter="addComment"
          />
          <div class="comment-submit">
            <el-button type="primary" @click="addComment">发布评论</el-button>
          </div>
        </div>
        <el-divider />
        <div class="comment-list">
          <div v-for="c in comments" :key="c.id" class="comment-item" :class="{'nested-comment': c.level > 1}" :style="{ marginLeft: c.level > 1 ? Math.min((c.level - 1) * 24, 48) + 'px' : '0' }">
            <div class="comment-header">
              <img v-if="c.avatar_url" :src="c.avatar_url" class="avatar-sm" />
              <div v-else class="avatar-sm avatar-fallback">{{ (c.display_name || "U").slice(0, 1) }}</div>
              <div class="comment-meta">
                <strong>{{ c.display_name || c.username }}</strong>
                <span class="comment-time" v-if="c.created_at">{{ formatTime(c.created_at) }}</span>
              </div>
            </div>
            <div class="comment-body">{{ c.content }}</div>
            <div class="comment-actions">
              <span class="action-btn" @click="prepareReply(c)">💬 回复</span>
              <span class="action-btn" v-if="canEditComment(c)" @click="openEdit(c)">✏️ 编辑</span>
              <span class="action-btn text-danger" v-if="canEditComment(c)" @click="confirmDelete(c)">🗑️ 删除</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 悬浮工具栏 -->
    <div class="floating-bar">
      <el-tooltip content="点赞文章" placement="left">
        <div class="fab-btn" :class="{active: isLiked}" @click="like">👍</div>
      </el-tooltip>
      <el-tooltip :content="isFavorited ? '取消收藏' : '收藏文章'" placement="left">
        <div class="fab-btn" :class="{active: isFavorited}" @click="toggleFavorite">⭐</div>
      </el-tooltip>
      <el-tooltip content="直达评论" placement="left">
        <div class="fab-btn" @click="scrollToComment">💬</div>
      </el-tooltip>
      <el-tooltip content="分享链接" placement="left">
        <div class="fab-btn" @click="sharePost">🔗</div>
      </el-tooltip>
      <el-tooltip content="回到顶部" placement="left">
        <div class="fab-btn" @click="scrollToTop">⬆️</div>
      </el-tooltip>
    </div>

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
import { computed, onMounted, ref, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { marked } from "marked";
import api from "../api";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

const route = useRoute();
const router = useRouter();
const store = useAuthStore();
const post = ref({ title: "", content: "", like_count: 0, favorite_count: 0, view_count: 0, author_id: 0, author_name: "", created_at: "" });
const comments = ref([]);
const comment = ref("");
const site = ref({ site_name: "BlogForum", announcement: "", comment_enabled: true });
const isFavorited = ref(false);
const isLiked = ref(false); // local state for UI immediately
const commentInputRef = ref(null);

const editVisible = ref(false);
const editContent = ref("");
const editTarget = ref(null);

const rendered = computed(() => marked.parse(post.value.content || ""));
const canEdit = computed(() => {
  if (!store.user) return false;
  return store.user.is_admin || store.user.id === post.value.author_id;
});
const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const canEditComment = (c) => {
  if (!store.user) return false;
  return store.user.is_admin || store.user.id === c.user_id;
};

const formatTime = (isoString) => {
  if (!isoString) return "";
  const date = new Date(isoString.includes('Z') ? isoString : isoString + 'Z');
  const now = new Date();
  const diff = Math.max(0, (now - date) / 1000);
  if (diff < 60) return "刚刚";
  if (diff < 3600) return Math.floor(diff / 60) + "分钟前";
  if (diff < 86400) return Math.floor(diff / 3600) + "小时前";
  if (diff < 86400 * 30) return Math.floor(diff / 86400) + "天前";
  return date.toLocaleDateString();
};

const loadFavoriteState = async () => {
  if (!store.token) {
    isFavorited.value = false;
    return;
  }
  try {
    const resp = await api.get("/api/v1/users/me/favorites", { params: { post_id: route.params.id } });
    isFavorited.value = (resp.data || []).length > 0;
  } catch {
    isFavorited.value = false;
  }
};

const load = async () => {
  const resp = await api.get(`/api/v1/posts/${route.params.id}`);
  post.value = resp.data || post.value;
  const c = await api.get("/api/v1/comments", { params: { post_id: route.params.id } });
  comments.value = c.data || [];
  const cfg = await api.get("/api/v1/config");
  site.value = cfg.data || site.value;
  await loadFavoriteState();
};

const like = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再点赞");
    router.push("/login");
    return;
  }
  try {
    await api.post(`/api/v1/posts/${route.params.id}/like`);
    isLiked.value = true;
    ElMessage.success("点赞成功");
    await load();
  } catch (err) {
    // If already liked or error, refresh
    await load();
  }
};

const toggleFavorite = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再收藏");
    router.push("/login");
    return;
  }
  try {
    if (isFavorited.value) {
      await api.delete(`/api/v1/posts/${route.params.id}/favorite`);
      ElMessage.success("已取消收藏");
    } else {
      await api.post(`/api/v1/posts/${route.params.id}/favorite`);
      ElMessage.success("收藏成功");
    }
    await load();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, isFavorited.value ? "取消收藏失败" : "收藏失败"));
  }
};

const goEdit = () => {
  router.push(`/posts/${route.params.id}/edit`);
};

const scrollToComment = () => {
  const el = document.getElementById("comment-input-area");
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    nextTick(() => {
      commentInputRef.value?.focus();
    });
  }
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const sharePost = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    ElMessage.success("链接已复制，去分享吧！");
  } catch (err) {
    ElMessage.error("复制失败");
  }
};

const prepareReply = (c) => {
  const username = c.display_name || c.username;
  if (!comment.value.includes(`@${username}`)) {
    comment.value = `回复 @${username} : ${comment.value}`;
  }
  scrollToComment();
};

const addComment = async () => {
  if (!store.token) {
    ElMessage.warning("请先登录再评论");
    router.push("/login");
    return;
  }
  if (!comment.value.trim()) {
    ElMessage.warning("评论内容不能为空");
    return;
  }
  try {
    await api.post("/api/v1/comments", { post_id: Number(route.params.id), content: comment.value });
    comment.value = "";
    ElMessage.success("发布成功");
    await load();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "评论失败"));
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
  try {
    await api.put(`/api/v1/comments/${editTarget.value.id}`, { content: editContent.value });
    editVisible.value = false;
    ElMessage.success("修改成功");
    await load();
  } catch(err) {
    ElMessage.error(getErrorMessage(err, "保存失败"));
  }
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
    ElMessage.success("删除成功");
    await load();
  } catch {
    return;
  }
};

onMounted(load);
</script>

<style scoped>
.detail-container {
  max-width: 900px;
  margin: 24px auto;
  position: relative;
  display: flex;
  justify-content: center;
}
.detail-main {
  flex: 1;
  min-width: 0; /* prevent flex blowout */
  display: grid;
  gap: 20px;
}
.post-card .title {
  margin: 0 0 16px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.4;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 24px;
}
.author {
  display: flex;
  align-items: center;
  gap: 12px;
}
.author-info {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-weight: 500;
  font-size: 15px;
  color: #334155;
}
.post-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
.stats {
  font-size: 13px;
  color: #64748b;
  display: flex;
  gap: 16px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}
.avatar-fallback {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  color: #334155;
  font-size: 18px;
  font-weight: 600;
  border-radius: 50%;
}

/* Markdown Content Styling Enhancements */
.content {
  font-size: 16px;
  line-height: 1.8;
  color: #334155;
  word-wrap: break-word;
}
.content :deep(h1), .content :deep(h2), .content :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: #0f172a;
}
.content :deep(p) {
  margin-bottom: 1em;
}
.content :deep(pre) {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  line-height: 1.5;
}
.content :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
  color: #ef4444;
}
.content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}
.content :deep(blockquote) {
  border-left: 4px solid #cbd5e1;
  margin: 1em 0;
  padding-left: 16px;
  color: #64748b;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
}
.content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  margin: 16px 0;
}

.bottom-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* Comment section styles */
.comment-input-wrapper {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}
.comment-submit {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
.comment-list {
  display: flex;
  flex-direction: column;
}
.comment-item {
  padding: 16px 0;
  border-bottom: 1px dashed #e2e8f0;
  transition: background-color 0.2s;
}
.comment-item:hover {
  background-color: #f8fafc;
}
.nested-comment {
  border-left: 2px solid #cbd5e1;
  padding-left: 16px;
  margin-top: 8px;
  background-color: #f8fafc;
  border-bottom: none;
  border-radius: 0 4px 4px 0;
}
.comment-header {
  font-size: 13px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.comment-meta {
  display: flex;
  flex-direction: column;
}
.comment-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}
.comment-body {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
}
.comment-actions {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}
.action-btn {
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
  user-select: none;
}
.action-btn:hover {
  color: #3b82f6;
}
.text-danger:hover {
  color: #ef4444;
}
.avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}

/* Floating Bar */
.floating-bar {
  position: fixed;
  right: max(24px, calc(50vw - 480px - 80px));
  bottom: 80px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}
.fab-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}
.fab-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}
.fab-btn.active {
  color: #3b82f6;
  border-color: #bfdbfe;
  background-color: #eff6ff;
}

@media (max-width: 1080px) {
  .floating-bar {
    right: 16px;
    bottom: 80px;
  }
}
@media (max-width: 768px) {
  .floating-bar {
    display: none; /* Hide on small mobile */
  }
}
</style>
