<template>
  <div class="app">
    <header class="topbar">
      <div class="brand" @click="router.push('/')">Blog Forum</div>
      <nav class="nav">
        <el-button link @click="router.push('/')">首页</el-button>
        <el-button link @click="router.push('/profile')">个人中心</el-button>
        <el-button
          v-if="store.user?.is_admin"
          link
          @click="router.push('/admin')"
          >管理员</el-button
        >
      </nav>
      <div class="auth">
        <el-button type="primary" class="nav-post-btn" @click="goNewPost" round>
          发布新帖
        </el-button>
        <template v-if="store.user">
          <el-badge
            v-if="showUnreadBadge"
            :value="unreadCount"
            class="notif-badge"
          >
            <el-button link @click="router.push('/notifications')"
              >通知</el-button
            >
          </el-badge>
          <el-button v-else link @click="router.push('/notifications')"
            >通知</el-button
          >
          <div class="user-info">
            <img
              v-if="store.user.avatar_url"
              :src="store.user.avatar_url"
              class="avatar"
            />
            <div v-else class="avatar avatar-fallback">{{ initials }}</div>
            <span class="user">{{ displayName }}</span>
          </div>
          <el-button size="small" @click="logout">退出</el-button>
        </template>
        <template v-else>
          <el-button size="small" @click="router.push('/login')"
            >登录</el-button
          >
          <el-button
            size="small"
            type="primary"
            @click="router.push('/register')"
            >注册</el-button
          >
        </template>
      </div>
    </header>
    <router-view />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "./store/auth";
import api from "./api";

const router = useRouter();
const route = useRoute();
const store = useAuthStore();
const unreadCount = ref(0);

const displayName = computed(
  () =>
    store.user?.display_name ||
    store.user?.nickname ||
    store.user?.username ||
    "用户",
);
const initials = computed(() => {
  const name = displayName.value || "U";
  return name.slice(0, 1).toUpperCase();
});
const showUnreadBadge = computed(() => Number(unreadCount.value || 0) > 0);

const fetchUnread = async () => {
  if (!store.token || !store.user) {
    unreadCount.value = 0;
    return;
  }
  try {
    const resp = await api.get("/api/v1/notifications/unread-count");
    unreadCount.value = Number(resp.data?.count || 0);
  } catch {
    unreadCount.value = 0;
  }
};

const handleNotificationsUpdated = (event) => {
  const nextCount = Number(event.detail);
  if (Number.isFinite(nextCount)) {
    unreadCount.value = Math.max(0, nextCount);
    return;
  }
  fetchUnread();
};

const goNewPost = () => {
  if (!store.token) {
    ElMessage.warning("请先登录再发帖");
    router.push("/login");
    return;
  }
  router.push("/posts/new");
};

const logout = () => {
  store.clearToken();
  unreadCount.value = 0;
  router.push("/login");
};

watch(
  () => route.fullPath,
  () => {
    fetchUnread();
  },
);

watch(
  () => store.token,
  async (token) => {
    if (!token) {
      unreadCount.value = 0;
      return;
    }
    if (!store.user) {
      try {
        await store.fetchMe();
      } catch {
        store.clearToken();
        unreadCount.value = 0;
        return;
      }
    }
    await fetchUnread();
  },
  { immediate: true },
);

onMounted(async () => {
  if (store.token && !store.user) {
    try {
      await store.fetchMe();
    } catch {
      store.clearToken();
    }
  }
  await fetchUnread();
  window.addEventListener("notifications-updated", handleNotificationsUpdated);
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "notifications-updated",
    handleNotificationsUpdated,
  );
});
</script>

<style scoped>
:root {
  --font-sans:
    "Inter", "Helvetica Neue", "PingFang SC", "Microsoft YaHei",
    "Hiragino Sans GB", Arial, sans-serif;
  --bg: #f8fafc;
  --text: #0f172a;
}

html,
body,
#app {
  height: 100%;
}

body {
  margin: 0;
  font-family: var(--font-sans);
  color: var(--text);
  background: var(--bg);
}

.app {
  min-height: 100%;
}

.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.05),
    0 4px 12px rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s ease;
}

.brand {
  font-size: 24px;
  font-weight: 800;
  cursor: pointer;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
  margin-right: 32px;
}

.nav {
  display: flex;
  gap: 16px;
  flex: 1;
}

.nav .el-button {
  font-size: 15px;
  font-weight: 500;
  color: #475569;
  position: relative;
  transition: color 0.2s ease;
}

.nav .el-button:hover {
  color: #2563eb;
  background: transparent;
}

.auth {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f1f5f9;
}

.user {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.avatar-fallback {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e2e8f0, #cbd5e1);
  color: #334155;
  font-size: 14px;
  font-weight: 600;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.nav-post-btn {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.2s;
  padding: 8px 20px;
}
.nav-post-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

a {
  color: inherit;
  text-decoration: none;
}
</style>
