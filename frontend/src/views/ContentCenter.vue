<template>
  <div class="page-container">
    <div class="section-nav">
      <el-button @click="router.push('/profile')" round>个人资料</el-button>
      <el-button type="primary" plain @click="router.push('/profile/content')" round>内容中心</el-button>
    </div>

    <div class="content-paper">
      <div class="paper-header">
        <h2 class="paper-title">内容中心</h2>
        <p class="paper-subtitle">管理您发布的帖子与收藏列表</p>
      </div>

      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="我的发帖" name="posts">
          <div v-if="myPosts.length" class="list-block">
            <div v-for="item in myPosts" :key="item.id" class="record-card">
              <div class="record-main">
                <div class="record-title">{{ item.title }}</div>
                <div class="record-meta">
                  <span>点赞 {{ item.like_count || 0 }}</span>
                  <span>收藏 {{ item.favorite_count || 0 }}</span>
                  <span>{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
              <div class="record-actions">
                <el-button size="small" plain round @click="goPost(item.id)">查看</el-button>
                <el-button size="small" plain round type="primary" @click="goEdit(item.id)">编辑</el-button>
                <el-button size="small" plain round type="danger" @click="removePost(item)">删除</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="还没有发布过帖子" :image-size="88" />
        </el-tab-pane>
        
        <el-tab-pane label="我的收藏" name="favorites">
          <div v-if="favorites.length" class="list-block">
            <div v-for="item in favorites" :key="item.id" class="record-card">
              <div class="record-main">
                <div class="record-title">{{ item.title }}</div>
                <div class="record-meta">
                  <span>作者 {{ item.author_name || item.author_id }}</span>
                  <span>点赞 {{ item.like_count || 0 }}</span>
                  <span>收藏 {{ item.favorite_count || 0 }}</span>
                </div>
              </div>
              <div class="record-actions">
                <el-button size="small" plain round @click="goPost(item.id)">查看</el-button>
                <el-button size="small" plain round type="warning" @click="unfavorite(item)">取消收藏</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="还没有收藏任何帖子" :image-size="88" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();
const myPosts = ref([]);
const favorites = ref([]);
const activeTab = ref("posts");
const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const formatTime = (value) => {
  if (!value) return "";
  return new Date(value).toLocaleString();
};

const loadMyPosts = async () => {
  const resp = await api.get("/api/v1/users/me/posts");
  myPosts.value = resp.data || [];
};

const loadFavorites = async () => {
  const resp = await api.get("/api/v1/users/me/favorites");
  favorites.value = resp.data || [];
};

const load = async () => {
  await Promise.all([loadMyPosts(), loadFavorites()]);
};

const goPost = (id) => {
  router.push(`/posts/${id}`);
};

const goEdit = (id) => {
  router.push(`/posts/${id}/edit`);
};

const removePost = async (item) => {
  try {
    await ElMessageBox.confirm(`确认删除帖子《${item.title}》吗？`, "重要操作", {
      confirmButtonText: "确认删除",
      cancelButtonText: "暂不",
      type: "warning",
    });
    await api.delete(`/api/v1/posts/${item.id}`);
    ElMessage.success("帖子已完全删除");
    await loadMyPosts();
  } catch (err) {
    if (err === "cancel" || err === "close") {
      return;
    }
    ElMessage.error(getErrorMessage(err, "删除帖子失败"));
  }
};

const unfavorite = async (item) => {
  try {
    await api.delete(`/api/v1/posts/${item.id}/favorite`);
    ElMessage.success("已取消收藏");
    await loadFavorites();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "取消收藏失败"));
  }
};

onMounted(load);
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 32px auto;
  padding: 0 16px;
  display: grid;
  gap: 24px;
}
.section-nav {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.content-paper {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px 40px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  min-height: 500px;
}
.paper-header {
  margin-bottom: 24px;
}
.paper-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}
.paper-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: #64748b;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #f1f5f9;
}
.custom-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
}
.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #2563eb;
  font-weight: 600;
}

.list-block {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}
.record-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #ffffff;
  transition: all 0.2s ease;
}
.record-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  border-color: #cbd5e1;
}
.record-main {
  flex: 1;
}
.record-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
  line-height: 1.4;
}
.record-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: #64748b;
  font-size: 13px;
}
.record-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  opacity: 0.8;
  transition: opacity 0.2s;
}
.record-card:hover .record-actions {
  opacity: 1;
}

@media (max-width: 600px) {
  .content-paper {
    padding: 24px 20px;
  }
  .record-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .record-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: 8px;
  }
}
</style>
