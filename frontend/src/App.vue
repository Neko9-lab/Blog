<template>
  <div class="app">
    <header class="topbar">
      <div class="brand" @click="router.push('/')">Blog Forum</div>
      <nav class="nav">
        <el-button link @click="router.push('/')">首页</el-button>
        <el-button link @click="router.push('/profile')">个人中心</el-button>
        <el-button v-if="store.user?.is_admin" link @click="router.push('/admin')">管理员</el-button>
      </nav>
      <div class="auth">
        <template v-if="store.user">
          <el-badge v-if="unreadCount > 0" :value="unreadCount" class="notif-badge">
            <el-button link @click="router.push('/notifications')">通知</el-button>
          </el-badge>
          <el-button v-else link @click="router.push('/notifications')">通知</el-button>
          <div class="user-info">
            <img v-if="store.user.avatar_url" :src="store.user.avatar_url" class="avatar" />
            <div v-else class="avatar avatar-fallback">{{ initials }}</div>
            <span class="user">{{ displayName }}</span>
          </div>
          <el-button size="small" @click="logout">退出</el-button>
        </template>
        <template v-else>
          <el-button size="small" @click="router.push('/login')">登录</el-button>
          <el-button size="small" type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </header>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "./store/auth";
import api from "./api";

const router = useRouter();
const store = useAuthStore();
const unreadCount = ref(0);

const displayName = computed(() => store.user?.display_name || store.user?.nickname || store.user?.username || "用户");
const initials = computed(() => {
  const name = displayName.value || "U";
  return name.slice(0, 1).toUpperCase();
});

const fetchUnread = async () => {
  if (!store.user) return;
  const resp = await api.get("/api/v1/notifications/unread-count");
  unreadCount.value = resp.data?.count || 0;
};

const logout = () => {
  store.clearToken();
  router.push("/login");
};

onMounted(async () => {
  await store.fetchMe();
  await fetchUnread();
});
</script>

<style>
:root {
  --font-sans: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", Arial, sans-serif;
  --bg: #f7f8fb;
  --text: #1f2328;
}

html, body, #app {
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
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand {
  font-weight: 700;
  cursor: pointer;
}

.nav {
  display: flex;
  gap: 8px;
}

.auth {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user {
  font-size: 14px;
}

.avatar {
  width: 28px;
  height: 28px;
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

a {
  color: inherit;
}
</style>
