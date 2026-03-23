<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">通知</div>
      <el-button size="small" @click="markAll">全部标为已读</el-button>
    </div>

    <el-card v-for="n in items" :key="n.id" class="notif-card" shadow="never">
      <div class="notif-row">
        <div class="notif-left">
          <img v-if="n.actor_avatar" :src="n.actor_avatar" class="avatar" />
          <div v-else class="avatar avatar-fallback">{{ (n.actor_name || "U").slice(0, 1) }}</div>
        </div>
        <div class="notif-body">
          <div class="notif-content" :class="{ unread: !n.is_read }">
            {{ n.content }}
          </div>
          <div class="notif-meta">{{ n.created_at || "" }}</div>
        </div>
        <div class="notif-actions">
          <el-button v-if="(n.type === 'like' || n.type === 'comment') && n.source_id" size="small" @click="goPost(n)">查看</el-button>
          <el-button v-if="!n.is_read" size="small" @click="markRead(n)">已读</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();
const items = ref([]);

const load = async () => {
  const resp = await api.get("/api/v1/notifications");
  items.value = resp.data || [];
};

const markRead = async (n) => {
  await api.post(`/api/v1/notifications/${n.id}/read`);
  n.is_read = true;
};

const markAll = async () => {
  await api.post("/api/v1/notifications/read-all");
  items.value = items.value.map((n) => ({ ...n, is_read: true }));
};

const goPost = async (n) => {
  await markRead(n);
  router.push(`/posts/${n.source_id}`);
};

onMounted(load);
</script>

<style scoped>
.page {
  max-width: 900px;
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
.notif-card {
  margin-bottom: 12px;
}
.notif-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.notif-left {
  display: flex;
  align-items: center;
}
.notif-body {
  flex: 1;
}
.notif-content {
  font-size: 14px;
  color: #334155;
}
.notif-content.unread {
  font-weight: 600;
}
.notif-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}
.notif-actions {
  display: flex;
  gap: 8px;
}
.avatar {
  width: 32px;
  height: 32px;
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
