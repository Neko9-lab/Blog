<template>
  <div class="home">
    <section class="hero-compact">
      <div class="hero-main">
        <div class="hero-title-row">
          <h1>{{ site.site_name }}</h1>
        </div>
        <p class="hero-announcement">
          {{ site.announcement || "聚焦帖子索引、讨论与快速检索的轻量论坛" }}
        </p>
      </div>
      <div class="hero-stats">
        <div class="hero-stat">
          <strong>{{ total }}</strong>
          <span>帖子</span>
        </div>
        <div class="hero-stat">
          <strong>{{ hotPosts.length }}</strong>
          <span>热帖</span>
        </div>
        <div class="hero-stat">
          <strong>{{ orderLabel }}</strong>
          <span>排序</span>
        </div>
      </div>
    </section>

    <section class="forum-filters">
      <button
        v-for="item in views"
        :key="item.label"
        type="button"
        class="filter-chip"
        :class="{ active: viewMode === item.value && order === item.order }"
        @click="setView(item.value, item.order || order)"
      >
        {{ item.label }}
      </button>
      <button
        v-if="store.user"
        type="button"
        class="filter-chip quick-chip"
        @click="goMyPosts"
      >
        我的发布
      </button>
      <button
        v-if="store.user"
        type="button"
        class="filter-chip quick-chip"
        @click="goParticipated"
      >
        我参与的
      </button>
    </section>

    <section class="toolbar compact-toolbar">
      <el-input
        v-model="q"
        placeholder="搜索标题"
        class="search"
        @keyup.enter="searchPosts"
      />
      <el-select
        v-model="selectedCategory"
        placeholder="全部分类"
        clearable
        class="select"
        @change="searchPosts"
      >
        <el-option label="全部分类" :value="null" />
        <el-option
          v-for="item in categories"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        />
      </el-select>
      <el-select
        v-model="order"
        placeholder="排序"
        class="select"
        @change="searchPosts"
      >
        <el-option label="最新" value="new" />
        <el-option label="最热" value="hot" />
        <el-option label="活跃" value="active" />
      </el-select>
      <el-button @click="searchPosts">搜索</el-button>
    </section>

    <main class="content compact-content">
      <section class="feed forum-table">
        <div class="feed-head forum-head">
          <span class="head-topic">主题</span>
          <span class="head-author">楼主/分类</span>
          <span class="head-data">互动</span>
          <span class="head-active">最后活跃</span>
        </div>

        <router-link
          v-for="item in posts"
          :key="item.id"
          :to="`/posts/${item.id}`"
          class="topic-line"
        >
          <div class="topic-left">
            <div class="topic-title-row">
              <el-tag
                v-if="item.is_pinned"
                size="small"
                type="danger"
                effect="light"
                >置顶</el-tag
              >
              <el-tag
                v-if="item.is_featured"
                size="small"
                type="warning"
                effect="light"
                >精华</el-tag
              >
              <el-tag
                v-if="isToday(item.created_at)"
                size="small"
                type="success"
                effect="light"
                >今日</el-tag
              >
              <el-tag
                v-else-if="isNew(item.created_at)"
                size="small"
                type="info"
                effect="light"
                >新帖</el-tag
              >
              <h3 class="topic-title">{{ item.title }}</h3>
            </div>
          </div>
          <div class="topic-meta-column">
            <div class="person-row">
              <img
                v-if="item.author_avatar"
                :src="item.author_avatar"
                class="tiny-avatar"
              />
              <div v-else class="tiny-avatar tiny-avatar-fallback">
                {{ (item.author_name || "U").slice(0, 1) }}
              </div>
              <span>楼主 {{ item.author_name || item.author_id }}</span>
            </div>
            <button
              class="meta-link"
              type="button"
              @click.prevent="filterByCategory(item.category_id)"
            >
              {{ categoryName(item.category_id) }}
            </button>
          </div>
          <div class="topic-right">
            <div class="metric">
              <strong>{{ item.comment_count || 0 }}</strong
              ><span>评</span>
            </div>
            <div class="metric">
              <strong>{{ item.view_count || 0 }}</strong
              ><span>览</span>
            </div>
            <div class="metric">
              <strong>{{ item.like_count || 0 }}</strong
              ><span>赞</span>
            </div>
            <div class="metric">
              <strong>{{ item.favorite_count || 0 }}</strong
              ><span>藏</span>
            </div>
          </div>
          <div class="topic-active">
            <span>{{
              formatTime(item.last_activity_at || item.created_at)
            }}</span>
            <div class="person-row muted">
              <img
                v-if="item.last_reply_avatar"
                :src="item.last_reply_avatar"
                class="tiny-avatar"
              />
              <div v-else class="tiny-avatar tiny-avatar-fallback">
                {{ (item.last_reply_name || "-").slice(0, 1) }}
              </div>
              <span>{{
                item.last_reply_name
                  ? `回复 ${item.last_reply_name}`
                  : "暂无回复"
              }}</span>
            </div>
          </div>
        </router-link>

        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="size"
          :current-page="page"
          @current-change="handlePage"
        />
      </section>

      <aside class="sidebar compact-sidebar">
        <el-card class="side-card" shadow="never">
          <template #header>快捷入口</template>
          <div class="quick-list">
            <button type="button" class="quick-item" @click="goNewPost">
              发布新帖
            </button>
            <button
              type="button"
              class="quick-item"
              @click="router.push('/notifications')"
            >
              查看通知
            </button>
            <button
              v-if="store.user"
              type="button"
              class="quick-item"
              @click="router.push('/profile/content')"
            >
              内容中心
            </button>
            <button
              v-else
              type="button"
              class="quick-item"
              @click="router.push('/login')"
            >
              登录后参与
            </button>
          </div>
        </el-card>

        <el-card class="side-card" shadow="never">
          <template #header>站点公告</template>
          <div class="announcement-box">
            {{ site.announcement || "暂无公告，欢迎参与讨论与发帖。" }}
          </div>
        </el-card>

        <el-card class="side-card" shadow="never">
          <template #header>热门帖子</template>
          <div v-if="hotPosts.length" class="hot-list">
            <router-link
              v-for="item in hotPosts"
              :key="item.id"
              :to="`/posts/${item.id}`"
              class="hot-item"
            >
              <div class="hot-title">{{ item.title }}</div>
              <div class="hot-meta">
                <span>{{ item.author_name || item.author_id }}</span>
                <span>{{ item.comment_count || 0 }} 评</span>
              </div>
            </router-link>
          </div>
          <el-empty v-else description="暂无热门帖子" :image-size="72" />
        </el-card>

        <el-card class="side-card" shadow="never">
          <template #header>活跃分类</template>
          <div v-if="activeCategories.length" class="category-list">
            <button
              v-for="item in activeCategories"
              :key="item.id"
              type="button"
              class="category-item"
              @click="filterByCategory(item.id)"
            >
              <span>{{ item.name }}</span>
              <span>{{ item.count }}</span>
            </button>
          </div>
          <el-empty v-else description="暂无活跃分类" :image-size="72" />
        </el-card>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import api from "../api";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const store = useAuthStore();
const posts = ref([]);
const hotPosts = ref([]);
const q = ref("");
const order = ref("new");
const page = ref(1);
const size = ref(12);
const total = ref(0);
const selectedCategory = ref(null);
const viewMode = ref("all");
const site = ref({
  site_name: "BlogForum",
  announcement: "",
  comment_enabled: true,
});
const categories = ref([]);
const views = [
  { label: "全部", value: "all", order: "new" },
  { label: "最新", value: "all", order: "new" },
  { label: "最热", value: "all", order: "hot" },
  { label: "活跃", value: "all", order: "active" },
  { label: "精华", value: "featured", order: "active" },
  { label: "未回复", value: "unanswered", order: "active" },
];

const getErrorMessage = (err, fallback) =>
  err?.response?.data?.detail || err?.response?.data?.msg || fallback;
const orderLabel = computed(() => {
  if (order.value === "hot") return "HOT";
  if (order.value === "active") return "ACTIVE";
  return "NEW";
});
const activeCategories = computed(() => {
  const map = new Map();
  for (const item of posts.value) {
    const key = item.category_id || 0;
    map.set(key, (map.get(key) || 0) + 1);
  }
  return [...map.entries()]
    .filter(([key]) => key !== 0)
    .map(([id, count]) => ({ id, count, name: categoryName(id) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
});

const load = async () => {
  try {
    const resp = await api.get("/api/v1/posts", {
      params: {
        q: q.value,
        order: order.value,
        page: page.value,
        size: size.value,
        category_id: selectedCategory.value,
        view: viewMode.value,
      },
    });
    posts.value = resp.data.items || [];
    total.value = resp.data.total || 0;
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "帖子加载失败"));
  }
};

const loadHotPosts = async () => {
  try {
    const resp = await api.get("/api/v1/posts", {
      params: { order: "hot", page: 1, size: 6 },
    });
    hotPosts.value = resp.data.items || [];
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "热门帖子加载失败"));
  }
};

const loadSite = async () => {
  const resp = await api.get("/api/v1/config");
  site.value = resp.data || site.value;
};

const loadCategories = async () => {
  const resp = await api.get("/api/v1/categories");
  categories.value = resp.data || [];
};

const categoryName = (id) => {
  const c = categories.value.find((x) => x.id === id);
  return c ? c.name : "未分类";
};

const formatTime = (value) => {
  if (!value) return "刚刚";
  return new Date(value).toLocaleString();
};

const isNew = (value) => {
  if (!value) return false;
  return Date.now() - new Date(value).getTime() < 1000 * 60 * 60 * 24 * 3;
};

const isToday = (value) => {
  if (!value) return false;
  return new Date(value).toDateString() === new Date().toDateString();
};

const searchPosts = () => {
  page.value = 1;
  load();
};

const filterByCategory = (categoryId) => {
  selectedCategory.value = categoryId;
  searchPosts();
};

const setView = (view, nextOrder) => {
  viewMode.value = view;
  order.value = nextOrder;
  searchPosts();
};

const handlePage = (p) => {
  page.value = p;
  load();
};

const goNewPost = () => {
  if (!store.token) {
    ElMessage.warning("请先登录再发帖");
    router.push("/login");
    return;
  }
  router.push("/posts/new");
};

const goHot = () => {
  setView("all", "hot");
};

const goMyPosts = () => {
  router.push("/profile/content");
};

const goParticipated = async () => {
  if (!store.token) {
    router.push("/login");
    return;
  }
  try {
    const resp = await api.get("/api/v1/users/me/participated-posts");
    posts.value = resp.data || [];
    total.value = posts.value.length;
    viewMode.value = "participated";
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "参与帖子加载失败"));
  }
};

onMounted(async () => {
  await Promise.all([loadSite(), loadCategories(), load(), loadHotPosts()]);
});
</script>

<style scoped>
.home {
  padding: 32px 24px 64px;
  max-width: 1280px;
  margin: 0 auto;
}
.hero-compact {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 48px 0;
  margin-bottom: 32px;
  background: transparent;
  border: none;
  border-bottom: 2px solid #e2e8f0;
  border-radius: 0;
}
.hero-main {
  min-width: 0;
}
.hero-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.hero-title-row h1 {
  margin: 0;
  font-size: 40px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -1px;
  line-height: 1.2;
}
.hero-announcement {
  margin: 12px 0 0;
  color: #475569;
  font-size: 16px;
  line-height: 1.6;
}
.hero-stats {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}
.hero-stat {
  min-width: 72px;
  padding: 0;
  background: transparent;
  border: none;
  text-align: right;
}
.hero-stat strong {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 4px;
  line-height: 1;
}
.hero-stat span {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.forum-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}
.filter-chip {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-chip.active,
.filter-chip:hover,
.quick-chip:hover {
  border-color: #2563eb;
  color: #2563eb;
  background: #eff6ff;
}
.compact-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px 120px auto;
  gap: 16px;
  margin-bottom: 32px;
}
.search,
.select {
  width: 100%;
}
.compact-content {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 32px;
}
.forum-table {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.feed {
  display: block;
}
.feed-head {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}
.forum-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 160px 120px;
  gap: 16px;
  padding: 12px 20px;
  align-items: center;
  min-height: 0;
  line-height: 1.2;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.topic-line {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 160px 120px;
  gap: 16px;
  align-items: flex-start;
  padding: 24px 20px;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;
}
.topic-line:last-of-type {
  border-bottom: 0;
}
.topic-line:hover {
  background: #f8fafc;
}
.topic-left {
  min-width: 0;
}
.topic-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.topic-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: #1e293b;
  transition: color 0.1s ease;
}
.topic-line:hover .topic-title {
  color: #2563eb;
}
.topic-meta-column {
  display: grid;
  gap: 6px;
  color: #64748b;
  font-size: 13px;
}
.person-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.person-row.muted {
  color: #94a3b8;
}
.tiny-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}
.tiny-avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
}
.meta-link {
  padding: 0;
  border: 0;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
  font: inherit;
  text-align: left;
}
.topic-right {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
}
.metric {
  width: 44px;
  text-align: center;
}
.metric strong {
  display: block;
  font-size: 14px;
  color: #334155;
  line-height: 1.2;
}
.metric span {
  font-size: 12px;
  color: #94a3b8;
}
.topic-active {
  display: grid;
  gap: 4px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.3;
}
.compact-sidebar {
  display: grid;
  gap: 24px;
}
.side-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  background: #ffffff;
}
.quick-list,
.hot-list,
.category-list {
  display: grid;
  gap: 12px;
}
.quick-item,
.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #ffffff;
  color: #334155;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.quick-item:hover,
.category-item:hover {
  border-color: #93c5fd;
  color: #1e40af;
  background: #eff6ff;
}
.announcement-box {
  font-size: 14px;
  line-height: 1.6;
  color: #475569;
}
.hot-item {
  display: block;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}
.hot-item:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}
.hot-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin-bottom: 4px;
}
.hot-item:hover .hot-title {
  color: #1e40af;
}
.hot-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
}
@media (max-width: 1200px) {
  .forum-head,
  .topic-line {
    grid-template-columns: minmax(0, 1fr) 126px 148px 108px;
  }
}
@media (max-width: 1080px) {
  .compact-content {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 900px) {
  .hero-compact {
    flex-direction: column;
    align-items: stretch;
  }
  .hero-title-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .compact-toolbar {
    grid-template-columns: 1fr;
  }
  .forum-head {
    display: none;
  }
  .topic-line {
    grid-template-columns: 1fr;
  }
  .topic-right {
    justify-content: flex-start;
  }
}
</style>
