<template>
  <div class="page-container">
    <div class="notif-paper">
      <div class="paper-header">
        <div class="header-left">
          <h2 class="paper-title">通知中心</h2>
          <p class="paper-subtitle">您收到的互动与系统消息</p>
        </div>
        <el-button size="small" type="primary" plain round @click="markAll">全部标为已读</el-button>
      </div>

      <div class="notif-list" v-if="items.length">
        <div v-for="n in items" :key="n.id" class="notif-item" :class="{ 'is-unread': !n.is_read }">
          <div class="notif-left">
            <img v-if="n.actor_avatar" :src="n.actor_avatar" class="avatar" />
            <div v-else class="avatar avatar-fallback">{{ (n.actor_name || "U").slice(0, 1) }}</div>
          </div>
          <div class="notif-body">
            <div class="notif-content">
              <span v-if="!n.is_read" class="unread-dot"></span>
              {{ n.content }}
            </div>
            <div class="notif-meta">{{ formatTime(n.created_at) }}</div>
          </div>
          <div class="notif-actions">
            <el-button v-if="(n.type === 'like' || n.type === 'comment') && n.source_id" size="small" round @click="goPost(n)">查看详情</el-button>
            <el-button v-if="!n.is_read" size="small" type="primary" plain round @click="markRead(n)">标为已读</el-button>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="暂无新通知" :image-size="88" class="empty-state" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();
const items = ref([]);

const formatTime = (value) => {
  if (!value) return "";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleString();
};

const syncUnreadCount = () => {
  const count = items.value.filter((item) => !item.is_read).length;
  window.dispatchEvent(new CustomEvent("notifications-updated", { detail: count }));
};

const load = async () => {
  const resp = await api.get("/api/v1/notifications");
  items.value = resp.data || [];
  syncUnreadCount();
};

const markRead = async (n) => {
  await api.post(`/api/v1/notifications/${n.id}/read`);
  n.is_read = true;
  syncUnreadCount();
};

const markAll = async () => {
  await api.post("/api/v1/notifications/read-all");
  items.value = items.value.map((n) => ({ ...n, is_read: true }));
  syncUnreadCount();
};

const goPost = async (n) => {
  if (!n.is_read) {
    await markRead(n);
  }
  router.push(`/posts/${n.source_id}`);
};

onMounted(load);
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 32px auto;
  padding: 0 16px;
}

.notif-paper {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px 40px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  min-height: 500px;
}

.paper-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.header-left {
  display: flex;
  flex-direction: column;
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

.notif-list {
  display: flex;
  flex-direction: column;
}

.notif-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}
.notif-item:last-child {
  border-bottom: none;
}
.notif-item:hover {
  background-color: #f8fafc;
  margin: 0 -20px;
  padding: 20px;
  border-radius: 8px;
  border-bottom-color: transparent;
}

.notif-item.is-unread {
  background-color: #f0fdf4;
  margin: 0 -20px;
  padding: 20px;
  border-radius: 8px;
  border-bottom-color: transparent;
}
.notif-item.is-unread:hover {
  background-color: #dcfce7;
}

.notif-left {
  flex-shrink: 0;
}
.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  background: #fff;
}
.avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #475569;
  font-size: 16px;
  font-weight: 600;
}

.notif-body {
  flex: 1;
  min-width: 0; /* for text truncation if needed later */
}
.notif-content {
  font-size: 15px;
  color: #1e293b;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.is-unread .notif-content {
  font-weight: 600;
  color: #0f172a;
}
.unread-dot {
  width: 8px;
  height: 8px;
  background-color: #22c55e;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

.notif-meta {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 6px;
}

.notif-actions {
  display: flex;
  gap: 8px;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.notif-item:hover .notif-actions {
  opacity: 1;
}

.empty-state {
  padding: 60px 0;
}

@media (max-width: 600px) {
  .notif-paper {
    padding: 24px 20px;
  }
  .notif-item {
    flex-wrap: wrap;
    gap: 12px;
  }
  .notif-body {
    min-width: 100%;
    order: 3;
    margin-top: -4px;
  }
  .notif-actions {
    margin-left: auto;
  }
  .notif-item:hover, .notif-item.is-unread {
    margin: 0 -12px;
    padding: 16px 12px;
  }
}
</style>
