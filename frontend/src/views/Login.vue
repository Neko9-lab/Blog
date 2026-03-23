<template>
  <el-form @submit.prevent="onLogin" label-width="80px" style="max-width: 400px; margin: 40px auto;">
    <el-form-item label="账号">
      <el-input v-model="form.account" placeholder="邮箱或手机或用户名" />
    </el-form-item>
    <el-form-item label="密码">
      <el-input v-model="form.password" type="password" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onLogin">登录</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import api from "../api";
import { useAuthStore } from "../store/auth";

const form = reactive({ account: "", password: "" });
const store = useAuthStore();
const router = useRouter();

const onLogin = async () => {
  try {
    const resp = await api.post("/api/v1/auth/login", form);
    store.setToken(resp.data.access_token);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (err) {
    const msg = err?.response?.data?.msg || "登录失败";
    ElMessage.error(msg);
  }
};
</script>
