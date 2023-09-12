<template>
  <div class="data-manage">
    <header>
      <TitleText :text="'选择数据源'" />
      <Uploader class="uploader" @update-status="updateStatus" />
    </header>
    <NDivider></NDivider>
    <main class="main">
      <NDataTable :columns="columns" :data="data"></NDataTable>
    </main>
  </div>
</template>

<script setup lang="ts">
import { DataManageService } from '@/service/data-manage/data-manage.service'
import { onMounted, h, ref, type Ref } from 'vue'
import Uploader from '@/components/Uploader.vue'
import { NPopconfirm, NButton } from 'naive-ui'
import TitleText from '@/components/TitleText.vue'
import { message } from '@/utils'

const columns = [
  {
    title: '名称',
    key: 'name'
  },
  {
    title: '模型',
    key: 'model'
  },
  {
    title: '描述',
    key: 'description'
  },
  {
    title: '文件名',
    key: 'filename'
  },
  {
    title: '版本',
    key: 'version'
  },
  {
    title: '上传日期',
    key: 'date'
  },
  {
    title: '操作',
    key: 'actions',
    render(row: Record<string, any>) {
      return h(
        NPopconfirm,
        {
          onPositiveClick: () => deleteItem(row)
        },
        {
          default: () => '删除后将无法恢复，确定要删除吗？',
          trigger: () => {
            return h(
                NButton,
                {
                  strong: true,
                  tertiary: true,
                  size: 'small',
                },
                {
                  default: () => '删除'
                }
            )
          }
        }
      )
    }
  }
]

const data: Ref<Record<string, any>[]> = ref([])

const getList = async () => {
  const resp = await DataManageService.getList()
  if (resp.status === 200) {
    data.value = resp.data
  }
  console.log('%c resp ==>', 'color: orange', resp)
}

const updateStatus = async (status: boolean) => {
  if (status) {
    console.log('%c 触发更新 ==>', 'color: orange', status)
    await getList()
  }
}

const deleteItem = async (item: Record<string, any>) => {
  console.log('%c row ==>', 'color: orange', item)
  const resp = await DataManageService.deleteOld({ path: item.location })
  if (resp?.data?.status === 'ok') {
    message.success('删除成功')
    await getList()
  }
}

onMounted(async () => {
  await getList()
})
</script>

<style lang="less" scoped>
.uploader {
  width: 420px;
}
.main {
  margin-top: 20px;
}
</style>
