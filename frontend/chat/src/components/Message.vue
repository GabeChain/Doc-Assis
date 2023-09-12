<template>
  <div class="chat-message-block" :class="`role_${messageInfo.role}`" v-if="messageInfo.role">
    <div v-if="messageInfo.loading" class="chat-message-block-loading">
      <svg width="30" height="30" viewBox="0 0 105 105" fill="#8559F4" data-testid="grid-svg">
        <circle cx="12.5" cy="12.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="0s"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="12.5" cy="52.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="100ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="52.5" cy="12.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="300ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="52.5" cy="52.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="600ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="92.5" cy="12.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="800ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="92.5" cy="52.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="400ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="12.5" cy="92.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="700ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="52.5" cy="92.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="500ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
        <circle cx="92.5" cy="92.5" r="5">
          <animate
            attributeName="fill-opacity"
            begin="200ms"
            dur="1s"
            values="1;.2;1"
            calcMode="linear"
            repeatCount="indefinite"
          ></animate>
        </circle>
      </svg>
      <p>Searching documentation. This may take a second!</p>
    </div>
    <div v-else class="chat-message-block-main">
      <div class="avatar" :class="messageInfo.role" :title="messageInfo.role">
        <img
          v-if="messageInfo.role === 'user'"
          src="@/assets/default_icon.svg"
          alt="default_icon"
        />
        <img v-else src="@/assets/response_icon.svg" alt="response_icon" />
      </div>
      <div class="message" v-html="message"></div>
    </div>
    <div
      class="chat-message-block-refer"
      v-if="messageInfo.metadata && messageInfo.metadata.length"
    >
      <div class="chat-message-block-refer-title">参考数据源:</div>
      <div class="chat-message-block-refer-metadata">
        <span
          class="chat-message-block-refer-metadata-tag"
          v-for="i in messageInfo.metadata"
          :key="i"
          >{{ i }}</span
        >
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
const props = withDefaults(
  defineProps<{
    messageInfo: {
      role: string
      message: string
      metadata?: string[]
      loading: boolean
    }
  }>(),
  {
    messageInfo: () => ({
      role: '',
      message: '',
      loading: false
    })
  }
)
function highlightCodeBlock(text: string): string {
  const searchRegExp = /```([\s\S]*?)```/g
  return text.replace(searchRegExp, (searchValue: string) => {
    const extractRegExp = /```([\s\S]*?)```/
    try {
      const res = extractRegExp.exec(searchValue)
      const extract = res?.[1] || res?.[0]
      if (extract) {
        return `<pre>${hljs.highlightAuto(extract).value}</pre>`
      } else {
        return `<pre>${hljs.highlightAuto(searchValue).value}</pre>`
      }
    } catch (e) {
      console.error(e)
      return searchValue
    }
  })
}
const message = computed(() => {
  if (props.messageInfo.role === 'system') {
    return highlightCodeBlock(props.messageInfo.message)
  } else {
    return props.messageInfo.message
  }
})
</script>

<style lang="less">
.chat-message-block {
  padding: 1rem;
  margin-top: 1rem;
  --tw-border-opacity: 0.2;
  border-bottom: 0.1rem solid #343437;
  display: flex;
  flex-direction: column;
  &-loading {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    color: #f7f7f7;
    p {
      margin-top: 10px;
    }
  }
  &-main {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;

    .avatar {
      align-self: flex-start;
      width: 2rem;
      height: 2rem;
      display: flex;
      justify-content: center;
      align-items: center;
      border: 1px solid #343538;
      border-radius: 0.5rem;
    }
    .system {
      background: linear-gradient(to right, rgb(133, 89, 244), rgba(133, 89, 244, 0.467))
        padding-box;
    }
    .message {
      flex: 1;
      padding-left: 1rem;
      padding-right: 0;
      color: #fff;
      font-size: 16px;
      pre {
        padding: 13px 15px;
        margin-top: 0;
        margin-bottom: 24px;
        font-size: 1em;
        background: #d0d0d0;
        border-radius: 2px;
        overflow-x: auto;
        color: #000;
      }
    }
  }
  &-refer {
    width: 100%;
    display: flex;
    align-items: center;
    margin-top: 10px;
    &-title {
      color: #fff;
      margin-right: 10px;
      width: 80px;
    }
    &-metadata {
      display: flex;
      align-items: center;
      flex: 1;
      flex-wrap: wrap;
      &-tag {
        &:hover {
          border-color: #fff;
          cursor: pointer;
        }
        transition: all 0.5s;
        background-color: rgba(133, 89, 244, 0.333);
        color: #fff;
        font-weight: 500;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        margin: 0 10px 10px 0;
      }
    }
  }
}
.chat-message-block.role_user {
  .chat-message-block-main {
    flex-direction: row-reverse;
    .message {
      position: relative;
      text-align: right;
      padding-left: 0;
      padding-right: 1rem;
    }
  }
}
</style>
