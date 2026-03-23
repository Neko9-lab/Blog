<template>
  <div class="page">
    <el-card class="card" shadow="never">
      <template #header>个人资料</template>
      <el-form class="profile-form" @submit.prevent="saveProfile">
        <el-form-item label="头像">
          <div class="avatar-row">
            <img v-if="form.avatar_url" :src="form.avatar_url" class="avatar" />
            <div v-else class="avatar avatar-fallback">{{ initials }}</div>
            <input ref="fileInput" type="file" class="file-input" @change="uploadAvatar" />
            <el-button size="small" @click="triggerUpload">上传头像</el-button>
          </div>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" @click="saveProfile">保存资料</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card class="card" shadow="never">
      <template #header>修改密码</template>
      <el-form class="profile-form" @submit.prevent="changePassword">
        <el-form-item label="旧密码">
          <el-input v-model="password.old" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="password.new" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" @click="changePassword">更新密码</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from "vue";
import { ElMessage } from "element-plus";
import api from "../api";

const form = reactive({ username: "", nickname: "", avatar_url: "" });
const password = reactive({ old: "", new: "" });
const fileInput = ref(null);

const initials = computed(() => {
  const name = form.nickname || form.username || "U";
  return name.slice(0, 1).toUpperCase();
});

const load = async () => {
  const resp = await api.get("/api/v1/users/me");
  form.username = resp.data?.username || "";
  form.nickname = resp.data?.nickname || "";
  form.avatar_url = resp.data?.avatar_url || "";
};

const triggerUpload = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

const uploadAvatar = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const data = new FormData();
  data.append("file", file);
  try {
    const resp = await api.post("/api/v1/uploads", data, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    const apiBase = import.meta.env.VITE_API_BASE || "";
    const rawUrl = resp.data.url;
    form.avatar_url = rawUrl.startsWith("http") ? rawUrl : `${apiBase}${rawUrl}`;
  } catch (err) {
    const msg = err?.response?.data?.msg || "上传失败";
    ElMessage.error(msg);
  } finally {
    e.target.value = "";
  }
};

const saveProfile = async () => {
  await api.put("/api/v1/users/me", form);
  ElMessage.success("已保存");
};

const changePassword = async () => {
  if (!password.old || !password.new) {
    ElMessage.warning("请输入旧密码与新密码");
    return;
  }
  try {
    await api.post("/api/v1/users/change-password", {
      old_password: password.old,
      new_password: password.new,
    });
    ElMessage.success("密码已更新");
    password.old = "";
    password.new = "";
  } catch (err) {
    const msg = err?.response?.data?.msg || "修改失败";
    ElMessage.error(msg);
  }
};

onMounted(load);
</script>

<style scoped>
.page {
  max-width: 760px;
  margin: 24px auto;
  display: grid;
  gap: 16px;
  padding: 0 16px;
}
.card {
  border-radius: 12px;
}
.profile-form :deep(.el-form-item__label) {
  width: 80px;
  color: #475569;
}
.profile-form :deep(.el-form-item) {
  margin-bottom: 18px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.avatar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar {
  width: 48px;
  height: 48px;
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
  font-size: 14px;
  font-weight: 600;
}
.file-input {
  display: none;
}
</style>
