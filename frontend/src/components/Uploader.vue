<template>
  <div class="uploader">
    <NUpload v-bind="uploadOptions" :disabled="uploadDisabled" @before-upload="beforeUpload" @change="handleUpload">
      <NUploadDragger>
        <div style="margin-bottom: 12px">
          <NIcon size="48" :depth="3">
            <Archive/>
          </NIcon>
        </div>
        <NText style="font-size: 16px"> 点击或者拖动文件到该区域来上传</NText>
        <NP depth="3" style="margin: 8px 0 0 0"> 已PDF、TXT，每个文件不超过15MB.</NP>
      </NUploadDragger>
    </NUpload>
    <NProgress
        type="line"
        :status="statusType"
        :percentage="current"
        :show-indicator="false"
        processing
    />
  </div>
</template>

<script lang="ts" setup>
import {Archive} from '@vicons/fa'
import {reactive, ref} from 'vue'
import type {UploadFileInfo} from 'naive-ui'
import {message} from '@/utils'
import {DataManageService} from '@/service/data-manage/data-manage.service'

const uploadOptions = reactive({
  action: '/admin/api/upload',
  accept: '.pdf',
  data: {
    user: '',
    name: ''
  },
  showFileList: false
})

const emits = defineEmits(['updateStatus'])

const statusType = ref('info')
const current = ref(0)

const uploadDisabled = ref(false)

const beforeUpload = () => {
  //
}

const handleUpload = async (options: {
  file: UploadFileInfo
  fileList: Array<UploadFileInfo>
  event?: Record<string, any>
}) => {
  uploadOptions.data.name = options.file.name
  uploadOptions.data.user = 'local'
  if (options.file.status === 'finished') {
    statusType.value = 'info'
    current.value = 10
    setTimeout(async () => {
      await getUploadStatus(options)
    }, 1000)
  }
}

const getUploadStatus = async (options: Record<string, any>, requestNum: number = 0) => {
  const resp = JSON.parse(options?.event?.target?.response) || ''
  const {status, data} = await DataManageService.checkStatus({
    task_id: resp?.task_id
  })
  console.log('%c status', 'color: orange', status, data)
  if (requestNum === 20) {
    statusType.value = 'error'
    message.error('上传失败，请重试')
    return
  }
  if (status === 200 && data?.status === 'PROGRESS') {
    current.value = !data?.result?.current ? 10 : data?.result?.current
    setTimeout(async () => {
      requestNum++
      await getUploadStatus(options, requestNum)
    }, 1000)
  } else if (status === 200 && data?.status === 'SUCCESS') {
    statusType.value = 'success'
    current.value = 100
    emits('updateStatus', true)
    message.success('上传成功')
  } else {
    statusType.value = 'error'
    message.error('网络出错，请检查后再试')
  }
}
</script>

<style scoped></style>
