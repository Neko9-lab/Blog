import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Home from "../views/Home.vue";
import PostDetail from "../views/PostDetail.vue";
import PostNew from "../views/PostNew.vue";
import PostEdit from "../views/PostEdit.vue";
import Profile from "../views/Profile.vue";
import Admin from "../views/Admin.vue";
import Notifications from "../views/Notifications.vue";

const routes = [
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/", component: Home },
  { path: "/posts/new", component: PostNew, meta: { requiresAuth: true } },
  { path: "/posts/:id/edit", component: PostEdit, meta: { requiresAuth: true } },
  { path: "/posts/:id", component: PostDetail },
  { path: "/profile", component: Profile, meta: { requiresAuth: true } },
  { path: "/notifications", component: Notifications, meta: { requiresAuth: true } },
  { path: "/admin", component: Admin, meta: { requiresAuth: true, requiresAdmin: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  const store = useAuthStore();
  if (store.token && !store.user) {
    try {
      await store.fetchMe();
    } catch {
      store.clearToken();
    }
  }

  if (to.meta.requiresAuth && !store.token) {
    return next("/login");
  }
  if (to.meta.requiresAdmin && !store.user?.is_admin) {
    return next("/");
  }
  return next();
});

export default router;
