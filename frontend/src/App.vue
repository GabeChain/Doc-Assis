<template>
  <NConfigProvider :theme-overrides="themeOverrides" :locale="zh" :date-locale="dateZhCN">
    <RouterView />
  </NConfigProvider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { dateZhCN, NConfigProvider, zhCN as zh, type GlobalThemeOverrides } from 'naive-ui'

const themeOverrides: GlobalThemeOverrides = {
  Layout: {
    color: '#F2F2F2FF'
  }
}
</script>

<style lang="less">
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-button {
  display: none;
}

::-webkit-scrollbar-track {
  background: #e8e8e8;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb {
  background: #bbb;
  border-radius: 8px;
}

::-webkit-scrollbar-corner {
  background: #e8e8e8;
  border-radius: 8px;
}
</style>
