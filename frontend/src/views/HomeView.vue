<template>
  <NLayout class="n-layout-wrapper" has-sider>
    <NLayoutSider
        collapse-mode="width"
        :collapsed-width="0"
        :width="200"
        show-trigger="arrow-circle"
        content-style="padding: 24px;"
        bordered
        inverted
    >
      <NMenu
          :value="selectMenu"
          :options="menuOptions"
      />
    </NLayoutSider>
    <NLayout>
      <NLayoutHeader position="absolute" class="n-layout-header-wrapper" bordered
      />
      <NLayoutContent content-style="padding: 10px;" class="n-layout-content-wrapper">
        <NCard class="n-layout-content-wrapper__card">
          <RouterView/>
        </NCard>
      </NLayoutContent>
      <NLayoutFooter position="absolute" class="n-layout-footer-wrapper" bordered>
        Copyright © 2023 All rights reserved.
      </NLayoutFooter>
    </NLayout>
  </NLayout>
</template>

<script setup lang="tsx">
import {RouterView} from 'vue-router'
import {computed} from "vue";

const selectMenu = 'data-manage'

const menuOptions = [
  {
    label: '数据源管理',
    key: 'data-manage'
  }
]
</script>

<style lang="less" scoped>
.n-layout-wrapper {
  height: 100vh;
  width: 100vw;
}

.n-layout-header-wrapper {
  height: 50px;
  line-height: 50px;
  padding: 0 20px;
  z-index: 2;
}

.n-layout-content-wrapper {
  margin-top: 50px;
  height: calc(100vh - 100px);

  &__card {
    height: 100%;
    background-color: #ffffff;
    overflow-y: scroll;
  }
}

.n-layout-footer-wrapper {
  height: 50px;
  line-height: 50px;
  padding: 0 20px;
  z-index: 2;
}
</style>
