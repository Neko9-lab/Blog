<template>
  <div class="home">
    <header class="hero">
      <div class="hero-text">
        <h1>{{ site.site_name }}</h1>
        <p>{{ site.announcement || "面向个人开发者与小型技术社区的高性能论坛" }}</p>
        <div class="hero-actions">
          <el-button type="primary" @click="goNewPost">立即发帖</el-button>
          <el-button @click="goHot">热门话题</el-button>
        </div>
      </div>
      <div class="hero-panel">
        <div class="stat">
          <div class="stat-num">{{ total }}</div>
          <div class="stat-label">总帖子</div>
        </div>
        <div class="stat">
          <div class="stat-num">0</div>
          <div class="stat-label">活跃用户</div>
        </div>
        <div class="stat">
          <div class="stat-num">0</div>
          <div class="stat-label">今日新增</div>
        </div>
      </div>
    </header>

    <section class="toolbar">
      <el-input v-model="q" placeholder="搜索帖子" class="search" />
      <el-select v-model="order" placeholder="排序" class="select">
        <el-option label="最新" value="new" />
        <el-option label="最热" value="hot" />
      </el-select>
      <el-button @click="load">搜索</el-button>
    </section>

    <main class="content">
      <section class="feed">
        <el-card v-for="item in posts" :key="item.id" class="post-card" shadow="never">
          <h3>
            <router-link :to="`/posts/${item.id}`">{{ item.title }}</router-link>
          </h3>
          <p class="excerpt">{{ previewText(item.content) }}</p>
          <div class="meta">
            <span>作者: {{ item.author_name || item.author_id }}</span>
            <span>分类: {{ categoryName(item.category_id) }}</span>
          </div>
        </el-card>

        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="size"
          :current-page="page"
          @current-change="handlePage"
        />
      </section>

      <aside class="sidebar">
        <el-card class="side-card" shadow="never">
          <template #header>热门标签</template>
          <div class="tags">
            <el-tag>FastAPI</el-tag>
            <el-tag>Vue3</el-tag>
            <el-tag>Docker</el-tag>
          </div>
        </el-card>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import api from "../api";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const store = useAuthStore();
const posts = ref([]);
const q = ref("");
const order = ref("new");
const page = ref(1);
const size = ref(10);
const total = ref(0);
const site = ref({ site_name: "BlogForum", announcement: "", comment_enabled: true });
const categories = ref([]);

const load = async () => {
  const resp = await api.get("/api/v1/posts", {
    params: { q: q.value, order: order.value, page: page.value, size: size.value },
  });
  posts.value = resp.data.items || [];
  total.value = resp.data.total || 0;
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

const previewText = (text) => {
  if (!text) return "暂无内容";
  return text.replace(/\n/g, " ").slice(0, 80) + (text.length > 80 ? "..." : "");
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
  order.value = "hot";
  load();
};

onMounted(async () => {
  await loadSite();
  await loadCategories();
  await load();
});
</script>

<style scoped>
.home {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
.hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: center;
  background: linear-gradient(135deg, #f6f7fb, #ffffff);
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 24px;
}
.hero-text h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
}
.hero-text p {
  margin: 0 0 16px 0;
  color: #666;
}
.hero-actions {
  display: flex;
  gap: 12px;
}
.hero-panel {
  display: grid;
  gap: 12px;
}
.stat {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 12px;
  text-align: center;
  background: #fff;
}
.stat-num {
  font-size: 22px;
  font-weight: 600;
}
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.search {
  flex: 1;
}
.select {
  width: 140px;
}
.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
.feed {
  display: grid;
  gap: 16px;
}
.post-card h3 {
  margin: 0 0 8px 0;
}
.excerpt {
  margin: 0 0 8px 0;
  color: #666;
}
.meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 12px;
}
.sidebar {
  display: grid;
  gap: 16px;
}
.side-card {
  border-radius: 12px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .content {
    grid-template-columns: 1fr;
  }
}
</style>
