<template>
  <div class="register-wrapper">
    <el-card class="register-card" shadow="never">
      <h2 class="register-title">注册账号</h2>
      <el-form @submit.prevent="onRegister" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model.trim="form.username" placeholder="设置用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model.trim="form.email" placeholder="邮箱地址" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model.trim="form.phone" placeholder="手机号 (可选)" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="code-row">
            <el-input v-model.trim="form.code" placeholder="输入验证码" />
            <el-button @click="sendCode" class="code-btn">获取验证码</el-button>
          </div>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="设置密码 (最少 6 位)" />
        </el-form-item>
        <el-form-item class="submit-item">
          <el-button type="primary" native-type="submit" class="submit-btn" size="large">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        已有账号？<router-link to="/login">直接登录</router-link>
      </div>
    </el-card>
  </div>
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

<style scoped>
.register-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px);
  padding: 20px 20px 60px;
}
.register-card {
  width: 100%;
  max-width: 420px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  background: #ffffff;
  padding: 12px 16px;
}
.register-title {
  text-align: center;
  margin: 10px 0 28px;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.5px;
}
.code-row {
  display: flex;
  gap: 12px;
  width: 100%;
}
.code-btn {
  flex-shrink: 0;
  width: 110px;
}
.submit-item {
  margin-top: 32px;
  margin-bottom: 0;
}
.submit-btn {
  width: 100%;
  font-size: 15px;
  border-radius: 6px;
  background: #2563eb;
  border-color: #2563eb;
}
.submit-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}
.register-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #64748b;
}
.register-footer a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}
.register-footer a:hover {
  text-decoration: underline;
}
</style>
