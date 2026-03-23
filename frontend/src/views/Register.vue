<template>
  <el-form @submit.prevent="onRegister" label-width="80px" style="max-width: 400px; margin: 40px auto;">
    <el-form-item label="用户名">
      <el-input v-model="form.username" />
    </el-form-item>
    <el-form-item label="邮箱">
      <el-input v-model="form.email" />
    </el-form-item>
    <el-form-item label="手机">
      <el-input v-model="form.phone" />
    </el-form-item>
    <el-form-item label="验证码">
      <el-input v-model="form.code" />
    </el-form-item>
    <el-form-item>
      <el-button @click="sendCode">发送验证码</el-button>
    </el-form-item>
    <el-form-item label="密码">
      <el-input v-model="form.password" type="password" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onRegister">注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import api from "../api";

const form = reactive({ username: "", email: "", phone: "", code: "", password: "" });
const router = useRouter();

const sendCode = async () => {
  const account = form.email || form.phone;
  if (!account) {
    ElMessage.warning("请输入邮箱或手机号");
    return;
  }
  try {
    await api.post("/api/v1/auth/send-code", null, { params: { account } });
    ElMessage.success("验证码已发送（请查看后端日志）");
  } catch (err) {
    const msg = err?.response?.data?.msg || "发送失败";
    ElMessage.error(msg);
  }
};

const onRegister = async () => {
  try {
    await api.post("/api/v1/auth/register", form);
    ElMessage.success("注册成功，请登录");
    router.push("/login");
  } catch (err) {
    const msg = err?.response?.data?.msg || "注册失败";
    ElMessage.error(msg);
  }
};
</script>
