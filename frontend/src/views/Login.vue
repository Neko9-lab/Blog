<template>
  <div class="login-wrapper">
    <el-card class="login-card" shadow="never">
      <h2 class="login-title">欢迎登录</h2>
      <el-form @submit.prevent="onLogin" label-position="top">
        <el-form-item label="账号">
          <el-input v-model="form.account" placeholder="邮箱或手机或用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item class="submit-item">
          <el-button type="primary" native-type="submit" :loading="loading" class="submit-btn" size="large">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import api from "../api";
import { useAuthStore } from "../store/auth";

const form = reactive({ account: "", password: "" });
const loading = ref(false);
const store = useAuthStore();
const router = useRouter();

const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const onLogin = async () => {
  if (!form.account || !form.password) {
    ElMessage.warning({ message: "请输入账号和密码", offset: 72 });
    return;
  }
  if (loading.value) return;

  loading.value = true;
  try {
    const resp = await api.post("/api/v1/auth/login", form);
    store.setToken(resp.data.access_token);
    await store.fetchMe();
    window.dispatchEvent(new CustomEvent("notifications-updated", { detail: 0 }));
    ElMessage.success({ message: "登录成功", offset: 72 });
    router.push("/");
  } catch (err) {
    ElMessage.error({ message: getErrorMessage(err, "登录失败"), offset: 72 });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px);
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 360px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.login-title {
  text-align: center;
  margin: 10px 0 24px;
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
}
.submit-item {
  margin-top: 30px;
  margin-bottom: 0;
}
.submit-btn {
  width: 100%;
  font-size: 15px;
  border-radius: 6px;
}
.login-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: #64748b;
}
.login-footer a {
  color: #2563eb;
  text-decoration: none;
}
.login-footer a:hover {
  text-decoration: underline;
}
</style>
