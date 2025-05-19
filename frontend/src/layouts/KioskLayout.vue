<template>
  <div class="kiosk-layout">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'KioskLayout'
};
</script>

<style scoped>
.kiosk-layout {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style> 