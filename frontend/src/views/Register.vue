<template>
  <el-form @submit.prevent="onRegister" label-width="80px" style="max-width: 400px; margin: 40px auto;">
    <el-form-item label="用户名">
      <el-input v-model.trim="form.username" />
    </el-form-item>
    <el-form-item label="邮箱">
      <el-input v-model.trim="form.email" />
    </el-form-item>
    <el-form-item label="手机">
      <el-input v-model.trim="form.phone" />
    </el-form-item>
    <el-form-item label="验证码">
      <el-input v-model.trim="form.code" />
    </el-form-item>
    <el-form-item>
      <el-button @click="sendCode">发送验证码</el-button>
    </el-form-item>
    <el-form-item label="密码">
      <el-input v-model="form.password" type="password" show-password />
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

const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const validateRegisterForm = () => {
  if (!form.username) {
    return "请输入用户名";
  }
  if (!form.email && !form.phone) {
    return "请填写邮箱或手机号";
  }
  if (form.email && !/^\S+@\S+\.\S+$/.test(form.email)) {
    return "邮箱格式不正确";
  }
  if (form.phone && !/^1\d{10}$/.test(form.phone)) {
    return "手机号格式不正确";
  }
  if (!form.code) {
    return "请输入验证码";
  }
  if (!form.password) {
    return "请输入密码";
  }
  if (form.password.length < 6) {
    return "密码长度不能少于 6 位";
  }
  return "";
};

const sendCode = async () => {
  const account = form.email || form.phone;
  if (!account) {
    ElMessage.warning("请输入邮箱或手机号");
    return;
  }
  if (form.email && !/^\S+@\S+\.\S+$/.test(form.email)) {
    ElMessage.warning("邮箱格式不正确");
    return;
  }
  if (form.phone && !/^1\d{10}$/.test(form.phone)) {
    ElMessage.warning("手机号格式不正确");
    return;
  }
  try {
    await api.post("/api/v1/auth/send-code", null, { params: { account } });
    ElMessage.success("验证码已发送（请查看后端日志）");
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "发送失败"));
  }
};

const onRegister = async () => {
  const validationMessage = validateRegisterForm();
  if (validationMessage) {
    ElMessage.warning(validationMessage);
    return;
  }

  try {
    await api.post("/api/v1/auth/register", {
      ...form,
      email: form.email || null,
      phone: form.phone || null,
    });
    ElMessage.success("注册成功，请登录");
    router.push("/login");
  } catch (err) {
    ElMessage.error(getErrorMessage(err, "注册失败"));
  }
};
</script>
