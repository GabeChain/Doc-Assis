<template>
  <div class="title-text">
    <span>{{ text }}</span>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  text: {
    type: String,
    default: '标题'
  }
})
</script>

<style lang="less" scoped>
.title-text {
  box-sizing: border-box;
  font-size: 18px;
  font-weight: bold;
  padding: 10px 0;
}
</style>
