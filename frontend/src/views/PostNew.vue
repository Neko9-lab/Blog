<template>
  <div class="page">
    <post-editor @posted="goHome" />
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import PostEditor from "../components/PostEditor.vue";

const router = useRouter();

const goHome = () => {
  router.push("/");
};
</script>

<style scoped>
.page {
  max-width: 980px;
  margin: 24px auto;
}
</style>
