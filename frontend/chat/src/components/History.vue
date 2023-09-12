<template>
  <div class="message-history">
    <Message v-for="(e, i) in props.messageHistory" :key="i" :message-info="e" />
  </div>
</template>

<script lang="ts" setup>
import Message from './Message.vue'
const props = withDefaults(
  defineProps<{
    messageHistory: {
      role: string
      message: string
      loading: boolean
    }[]
  }>(),
  {
    messageHistory: () => []
  }
)
</script>

<style lang="less"></style>
