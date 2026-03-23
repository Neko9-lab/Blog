<template>
  <div class="admin-container">
    <div class="admin-header">
      <h2>后台管理中心</h2>
    </div>
    <el-tabs v-model="activeTab" tab-position="left" class="admin-tabs">
      <el-tab-pane label="仪表盘" name="dashboard">
        <el-card shadow="never" class="admin-card borderless-card">
          <template #header>管理统计</template>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_users || 0 }}</div>
              <div class="stat-label">总用户</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_posts || 0 }}</div>
              <div class="stat-label">总帖子</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.new_today || 0 }}</div>
              <div class="stat-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统配置" name="settings">
        <el-card shadow="never" class="admin-card borderless-card">
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
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="users">
        <el-card shadow="never" class="admin-card borderless-card">
          <template #header>用户管理</template>
          <div class="user-tools">
            <el-input v-model.trim="userIdKeyword" placeholder="按用户 ID 查询" clearable class="user-search" />
            <el-button @click="userIdKeyword = ''">清空</el-button>
          </div>
          <el-table :data="filteredUsers" size="small" style="width: 100%">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="display_name" label="用户" min-width="140" />
            <el-table-column label="联系方式" min-width="220">
              <template #default="scope">
                <div>{{ scope.row.email || '-' }}</div>
                <div>{{ scope.row.phone || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="封禁信息" min-width="220">
              <template #default="scope">
                <template v-if="scope.row.is_banned">
                  <div class="ban-text">原因: {{ scope.row.ban_reason || '未填写' }}</div>
                  <div class="ban-text">
                    时长: {{ scope.row.ban_expires_at ? `至 ${formatBanExpires(scope.row.ban_expires_at)}` : '永久封禁' }}
                  </div>
                </template>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="130">
              <template #default="scope">
                <el-tag :type="scope.row.is_banned ? 'danger' : 'success'">
                  {{ scope.row.is_banned ? '已封禁' : '正常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="角色" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.is_admin ? 'warning' : 'info'">
                  {{ scope.row.is_admin ? '管理员' : '用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template #default="scope">
                <el-button
                  v-if="!scope.row.is_banned"
                  size="small"
                  type="danger"
                  :disabled="scope.row.is_admin"
                  @click="openBanDialog(scope.row)"
                >
                  封号
                </el-button>
                <el-button v-else size="small" type="primary" @click="toggleUnban(scope.row)">
                  解封
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="帖子管理" name="posts">
        <el-card shadow="never" class="admin-card borderless-card">
          <template #header>帖子管理</template>
          <div class="post-tools">
            <el-input v-model.trim="postKeyword" placeholder="按标题或作者搜索帖子" clearable class="post-search" />
            <el-button @click="loadPosts">搜索</el-button>
          </div>
          <el-table :data="posts" size="small" style="width: 100%">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
            <el-table-column prop="author_name" label="作者" width="120" />
            <el-table-column prop="category_name" label="分类" width="120" />
            <el-table-column label="状态" width="140">
              <template #default="scope">
                <div class="post-tags">
                  <el-tag v-if="scope.row.is_pinned" size="small" type="danger">置顶</el-tag>
                  <el-tag v-if="scope.row.is_featured" size="small" type="warning">精华</el-tag>
                  <span v-if="!scope.row.is_pinned && !scope.row.is_featured">-</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="互动" width="180">
              <template #default="scope">
                <div class="post-metrics">
                  <span>览 {{ scope.row.view_count || 0 }}</span>
                  <span>评 {{ scope.row.comment_count || 0 }}</span>
                  <span>赞 {{ scope.row.like_count || 0 }}</span>
                  <span>藏 {{ scope.row.favorite_count || 0 }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280">
              <template #default="scope">
                <div class="post-actions">
                  <el-button size="small" @click="openPost(scope.row)">查看</el-button>
                  <el-button
                    size="small"
                    :type="scope.row.is_pinned ? 'info' : 'danger'"
                    @click="togglePinned(scope.row)"
                  >
                    {{ scope.row.is_pinned ? '取消置顶' : '置顶' }}
                  </el-button>
                  <el-button
                    size="small"
                    :type="scope.row.is_featured ? 'info' : 'warning'"
                    @click="toggleFeatured(scope.row)"
                  >
                    {{ scope.row.is_featured ? '取消精华' : '设为精华' }}
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="分类管理" name="categories">
        <el-card shadow="never" class="admin-card borderless-card">
          <template #header>分类管理</template>
          <div class="cat-tools">
            <el-input v-model="newCategory" placeholder="新分类名称" />
            <el-button type="primary" @click="addCategory">添加</el-button>
          </div>
          <el-table :data="categories" size="small" style="width: 100%">
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
      </el-tab-pane>

      <el-tab-pane label="系统日志" name="logs">
        <el-card shadow="never" class="admin-card borderless-card">
          <template #header>日志查看</template>
          <div class="log-tools">
            <el-input-number v-model="lines" :min="50" :max="1000" />
            <el-button @click="loadLogs">刷新</el-button>
          </div>
          <el-scrollbar height="260px" class="log-box">
            <div v-for="(line, idx) in logs" :key="idx" class="log-line">{{ line }}</div>
          </el-scrollbar>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="banVisible" title="封禁用户" width="420px">
      <el-form label-width="90px">
        <el-form-item label="目标用户">
          <div>{{ banTarget?.display_name }} (ID: {{ banTarget?.id }})</div>
        </el-form-item>
        <el-form-item label="封号原因">
          <el-input v-model.trim="banForm.reason" type="textarea" rows="3" placeholder="请输入封号原因" />
        </el-form-item>
        <el-form-item label="封禁类型">
          <el-radio-group v-model="banForm.permanent">
            <el-radio :label="false">临时封禁</el-radio>
            <el-radio :label="true">永久封禁</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="!banForm.permanent" label="封禁天数">
          <el-input-number v-model="banForm.duration_days" :min="1" :max="3650" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="banVisible = false">取消</el-button>
        <el-button type="danger" @click="submitBan">确认封号</el-button>
      </template>
    </el-dialog>

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
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../api';

const activeTab = ref('dashboard');
const stats = ref({ total_users: 0, total_posts: 0, new_today: 0 });
const config = ref({ site_name: '', announcement: '', comment_enabled: true });
const logs = ref([]);
const lines = ref(200);
const users = ref([]);
const userIdKeyword = ref('');
const posts = ref([]);
const postKeyword = ref('');

const categories = ref([]);
const newCategory = ref('');
const editVisible = ref(false);
const editId = ref(null);
const editName = ref('');
const banVisible = ref(false);
const banTarget = ref(null);
const banForm = reactive({ reason: '', permanent: false, duration_days: 7 });

const getErrorMessage = (err, fallback) => err?.response?.data?.detail || err?.response?.data?.msg || fallback;

const filteredUsers = computed(() => {
  if (!userIdKeyword.value) return users.value;
  return users.value.filter((user) => String(user.id) === userIdKeyword.value);
});

const formatBanExpires = (value) => {
  if (!value) return '永久封禁';
  return new Date(value).toLocaleString();
};

const load = async () => {
  try {
    const resp = await api.get('/api/v1/admin/stats');
    stats.value = resp.data || stats.value;
    const cfg = await api.get('/api/v1/admin/config');
    config.value = cfg.data || config.value;
    await Promise.all([loadUsers(), loadPosts(), loadCategories(), loadLogs()]);
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '管理数据加载失败'));
  }
};

const saveConfig = async () => {
  try {
    await api.put('/api/v1/admin/config', config.value);
    ElMessage.success('已保存');
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '保存失败'));
  }
};

const loadUsers = async () => {
  const resp = await api.get('/api/v1/admin/users');
  users.value = resp.data || [];
};

const loadPosts = async () => {
  const resp = await api.get('/api/v1/admin/posts', { params: { q: postKeyword.value || undefined } });
  posts.value = resp.data || [];
};

const openPost = (row) => {
  window.open(`/posts/${row.id}`, '_blank');
};

const togglePinned = async (row) => {
  try {
    await api.post(`/api/v1/admin/posts/${row.id}/pin`, null, { params: { enabled: !row.is_pinned } });
    ElMessage.success(row.is_pinned ? '已取消置顶' : '已置顶');
    await loadPosts();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '置顶操作失败'));
  }
};

const toggleFeatured = async (row) => {
  try {
    await api.post(`/api/v1/admin/posts/${row.id}/feature`, null, { params: { enabled: !row.is_featured } });
    ElMessage.success(row.is_featured ? '已取消精华' : '已设为精华');
    await loadPosts();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '精华操作失败'));
  }
};

const openBanDialog = (row) => {
  banTarget.value = row;
  banForm.reason = '';
  banForm.permanent = false;
  banForm.duration_days = 7;
  banVisible.value = true;
};

const submitBan = async () => {
  if (!banTarget.value) return;
  if (!banForm.reason) {
    ElMessage.warning('请输入封号原因');
    return;
  }
  if (!banForm.permanent && (!banForm.duration_days || banForm.duration_days < 1)) {
    ElMessage.warning('请输入有效的封禁天数');
    return;
  }

  try {
    await api.post(`/api/v1/admin/users/${banTarget.value.id}/ban`, {
      reason: banForm.reason,
      permanent: banForm.permanent,
      duration_days: banForm.permanent ? null : banForm.duration_days,
    });
    banVisible.value = false;
    ElMessage.success(banForm.permanent ? '已永久封禁该用户' : '已临时封禁该用户');
    await loadUsers();
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '封号失败'));
  }
};

const toggleUnban = async (row) => {
  try {
    await ElMessageBox.confirm(`确认解除用户 ${row.display_name} 的封禁吗？`, '提示', {
      confirmButtonText: '解封',
      cancelButtonText: '取消',
      type: 'info',
    });
    await api.post(`/api/v1/admin/users/${row.id}/unban`);
    ElMessage.success('已解除封禁');
    await loadUsers();
  } catch (err) {
    if (err === 'cancel' || err === 'close') return;
    ElMessage.error(getErrorMessage(err, '解封失败'));
  }
};

const loadLogs = async () => {
  const resp = await api.get('/api/v1/admin/logs', { params: { lines: lines.value } });
  logs.value = resp.data || [];
};

const loadCategories = async () => {
  const resp = await api.get('/api/v1/admin/categories');
  categories.value = resp.data || [];
};

const addCategory = async () => {
  if (!newCategory.value) return;
  await api.post('/api/v1/admin/categories', { name: newCategory.value });
  newCategory.value = '';
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
  await ElMessageBox.confirm('确认删除该分类？', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
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
.cat-tools,
.user-tools,
.post-tools {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.user-search,
.post-search {
  max-width: 280px;
}
.ban-text {
  line-height: 1.5;
  color: #475569;
  font-size: 12px;
}
.post-tags,
.post-metrics,
.post-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}
.admin-card {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  text-align: center;
  padding: 8px 0;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.2;
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #64748b;
}
.admin-container {
  max-width: 1120px;
  margin: 30px auto;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 24px;
  min-height: 60vh;
}
.admin-header h2 {
  margin: 0 0 24px 12px;
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
}
.admin-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  height: 44px;
  line-height: 44px;
  padding: 0 20px;
}
.borderless-card {
  border: none;
}
</style>
