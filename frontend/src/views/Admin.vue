<template>
  <div style="max-width: 900px; margin: 20px auto; display: grid; gap: 16px;">
    <el-card>
      <h3>管理统计</h3>
      <div>总用户: {{ stats.total_users }}</div>
      <div>总帖子: {{ stats.total_posts }}</div>
      <div>今日新增: {{ stats.new_today }}</div>
    </el-card>

    <el-card>
      <template #header>站点配置</template>
      <el-form label-width="100px">
        <el-form-item label="网站名称">
          <el-input v-model="config.site_name" />
        </el-form-item>
        <el-form-item label="公告">
          <el-input v-model="config.announcement" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="评论开关">
          <el-switch v-model="config.comment_enabled" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>分类管理</template>
      <div class="cat-tools">
        <el-input v-model="newCategory" placeholder="新分类名称" />
        <el-button type="primary" @click="addCategory">添加</el-button>
      </div>
      <el-table :data="categories" size="small" style="width: 100%;">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editCategory(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <template #header>日志查看</template>
      <div class="log-tools">
        <el-input-number v-model="lines" :min="50" :max="1000" />
        <el-button @click="loadLogs">刷新</el-button>
      </div>
      <el-scrollbar height="260px" class="log-box">
        <div v-for="(line, idx) in logs" :key="idx" class="log-line">{{ line }}</div>
      </el-scrollbar>
    </el-card>

    <el-dialog v-model="editVisible" title="编辑分类" width="360px">
      <el-input v-model="editName" placeholder="分类名称" />
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "../api";

const stats = ref({ total_users: 0, total_posts: 0, new_today: 0 });
const config = ref({ site_name: "", announcement: "", comment_enabled: true });
const logs = ref([]);
const lines = ref(200);

const categories = ref([]);
const newCategory = ref("");
const editVisible = ref(false);
const editId = ref(null);
const editName = ref("");

const load = async () => {
  const resp = await api.get("/api/v1/admin/stats");
  stats.value = resp.data || stats.value;
  const cfg = await api.get("/api/v1/admin/config");
  config.value = cfg.data || config.value;
  await loadCategories();
  await loadLogs();
};

const saveConfig = async () => {
  await api.put("/api/v1/admin/config", config.value);
  ElMessage.success("已保存");
};

const loadLogs = async () => {
  const resp = await api.get("/api/v1/admin/logs", { params: { lines: lines.value } });
  logs.value = resp.data || [];
};

const loadCategories = async () => {
  const resp = await api.get("/api/v1/admin/categories");
  categories.value = resp.data || [];
};

const addCategory = async () => {
  if (!newCategory.value) return;
  await api.post("/api/v1/admin/categories", { name: newCategory.value });
  newCategory.value = "";
  await loadCategories();
};

const editCategory = (row) => {
  editId.value = row.id;
  editName.value = row.name;
  editVisible.value = true;
};

const saveEdit = async () => {
  await api.put(`/api/v1/admin/categories/${editId.value}`, { name: editName.value });
  editVisible.value = false;
  await loadCategories();
};

const deleteCategory = async (row) => {
  await ElMessageBox.confirm("确认删除该分类？", "提示", {
    confirmButtonText: "删除",
    cancelButtonText: "取消",
    type: "warning",
  });
  await api.delete(`/api/v1/admin/categories/${row.id}`);
  await loadCategories();
};

onMounted(load);
</script>

<style scoped>
.log-tools {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.log-box {
  background: #0b0f14;
  color: #d1d5db;
  padding: 8px;
  border-radius: 6px;
  font-family: Consolas, monospace;
  font-size: 12px;
}
.log-line {
  white-space: pre-wrap;
}
.cat-tools {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
</style>
