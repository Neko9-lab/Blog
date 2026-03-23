<template>
  <div class="page-container">
    <div class="section-nav">
      <el-button type="primary" plain @click="router.push('/profile')" round>个人资料</el-button>
      <el-button @click="router.push('/profile/content')" round>内容中心</el-button>
    </div>

    <div class="profile-paper">
      <div class="paper-header">
        <h2 class="paper-title">个人资料</h2>
        <p class="paper-subtitle">管理您的公开信息和联系邮箱</p>
      </div>
      
      <el-form class="profile-form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled readonly class="readonly-input" />
          <div class="form-help">用户名为系统登录凭证，不允许变更。</div>
        </el-form-item>
        
        <el-form-item label="公开头像">
          <div class="avatar-uploader" @click="triggerUpload">
            <img v-if="form.avatar_url" :src="form.avatar_url" class="avatar-preview" />
            <div v-else class="avatar-fallback">{{ initials }}</div>
            <div class="avatar-overlay">更换头像</div>
            <input ref="fileInput" type="file" class="file-input" @change="uploadAvatar" accept="image/*" />
          </div>
        </el-form-item>

        <div class="form-row">
          <el-form-item label="前台昵称" class="flex-item">
            <el-input v-model="form.nickname" placeholder="其他用户将看到此称呼" />
          </el-form-item>
          <el-form-item label="联系邮箱" class="flex-item">
            <el-input v-model="form.email" placeholder="用于接收通知 (如 mail@example.com)" />
          </el-form-item>
        </div>

        <div class="form-actions">
          <el-button type="primary" class="save-btn" @click="saveProfile" round>保存资料设定</el-button>
        </div>
      </el-form>
    </div>

    <div class="profile-paper">
      <div class="paper-header">
        <h2 class="paper-title">安全中心</h2>
        <p class="paper-subtitle">定期更新密码可以保护您的账号安全</p>
      </div>
      
      <el-form class="profile-form" label-position="top" @submit.prevent="changePassword">
        <div class="form-row">
          <el-form-item label="当前密码" class="flex-item">
            <el-input v-model="password.old" type="password" placeholder="验证您的身份" show-password />
          </el-form-item>
          <el-form-item label="新密码" class="flex-item">
            <el-input v-model="password.new" type="password" placeholder="请填写包含字母和数字的新密码" show-password />
          </el-form-item>
        </div>
        <div class="form-actions">
          <el-button type="primary" plain class="save-btn" @click="changePassword" round>提交修改密码</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import api from "../api";

const router = useRouter();
const store = useAuthStore();
const form = reactive({ username: "", nickname: "", email: "", avatar_url: "" });
const password = reactive({ old: "", new: "" });
const fileInput = ref(null);

const initials = computed(() => {
  const name = form.nickname || form.username || "U";
  return name.slice(0, 1).toUpperCase();
});
const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const loadProfile = async () => {
  try {
    const resp = await api.get("/api/v1/users/me");
    form.username = resp.data?.username || "";
    form.nickname = resp.data?.nickname || "";
    form.email = resp.data?.email || "";
    form.avatar_url = resp.data?.avatar_url || "";
    store.user = resp.data || store.user;
  } catch (err) {
    ElMessage.error("获取个人资料失败");
  }
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
    ElMessage.error(getErrorMessage(err, "上传失败"));
  } finally {
    e.target.value = "";
  }
};

const saveProfile = async () => {
  // 只提交允许修改的列
  const payload = {
    nickname: form.nickname,
    email: form.email,
    avatar_url: form.avatar_url
  };
  try {
    await api.put("/api/v1/users/me", payload);
    await loadProfile();
    ElMessage.success("个人资料已保存！");
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "保存失败"));
  }
};

const changePassword = async () => {
  if (!password.old || !password.new) {
    ElMessage.warning("请完整输入当前密码和新密码");
    return;
  }
  try {
    await api.post("/api/v1/users/change-password", {
      old_password: password.old,
      new_password: password.new,
    });
    ElMessage.success("账号密码已完成更新");
    password.old = "";
    password.new = "";
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "修改密码失败"));
  }
};

onMounted(loadProfile);
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

.profile-paper {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.03);
  border: 1px solid rgba(226, 232, 240, 0.8);
}
.paper-header {
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
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

.profile-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #334155;
  padding-bottom: 6px;
}
.profile-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}
.profile-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1.5px #3b82f6 inset;
}
.readonly-input :deep(.el-input__wrapper) {
  background: #f8fafc;
  box-shadow: none;
}
.readonly-input :deep(.el-input__inner) {
  color: #94a3b8;
  cursor: not-allowed;
}
.form-help {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
  line-height: 1.4;
}

.form-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.flex-item {
  flex: 1;
  min-width: 240px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
.save-btn {
  padding: 10px 28px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.2s;
}
.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.avatar-uploader {
  position: relative;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}
.avatar-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #94a3b8, #64748b);
}
.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.2s;
}
.avatar-uploader:hover .avatar-overlay {
  opacity: 1;
}
.file-input {
  display: none;
}

@media (max-width: 600px) {
  .profile-paper {
    padding: 24px 20px;
  }
}
</style>
