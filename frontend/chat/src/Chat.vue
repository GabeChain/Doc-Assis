<template>
  <div class="chat-extension—main" :class="collapse && 'chat-extension—main__collapse'">
    <div class="chat-header" :class="collapse && 'chat-header__collapse'">
      <button class="chat-collapse-btn" @click="changeVisible">
        <img v-if="collapse" src="@/assets/fold.svg" alt="default_icon" />
        <img v-else src="@/assets/expand.svg" alt="default_icon" />
      </button>
    </div>
    <div id="chat-log" v-if="!collapse">
      <History :message-history="_history" />
    </div>
    <div class="user-area" v-if="!collapse">
      <div class="input-area">
        <textarea
          id="chat-input"
          :ref="setTextRefer"
          v-model="question"
          maxlength="1200"
          spellcheck="false"
          placeholder="control+enter for submit"
          @keydown.enter="onclickEnter"
        ></textarea>
      </div>
      <button class="submit" v-show="submitBtnVisible" @click="submit">Ask</button>
    </div>
  </div>
</template>

<!--@change="adjustHeight"-->
<!--@paste="adjustHeight"-->
<!--@cut="adjustHeight"-->
<!--@focus="adjustHeight"-->
<script lang="ts" setup>
import { nextTick, ref, watch } from 'vue'
import History from './components/History.vue'

const collapse = ref(false)
function changeVisible() {
  collapse.value = !collapse.value
}

function setTextRefer(el: any) {
  textareaEl.value = el
}
function adjustHeight() {
  if (!textareaEl.value) return
  textareaEl.value.style.height = 'auto'
  textareaEl.value.style.height = `${textareaEl.value.scrollHeight}px`
}
const textareaEl = ref<HTMLElement | null>(null)

const _history = ref<
  Array<{
    role: string
    message: string
    metadata?: string[]
    doc?: string
    loading: boolean
  }>
>([
  {
    role: 'system',
    message: '你好！有什么我可以帮助你的吗？',
    loading: false
  }
])

watch(
  () => _history.value.length,
  async () => {
    await nextTick()
    const i = document.getElementById('chat-log')
    if (i) {
      i.scrollTop = i.scrollHeight
    }
  },
  {}
)

async function getAnswer(question: string) {
  const { body } = await fetch('/chat/stream', {
    method: 'POST',
    credentials: 'omit',
    headers: {
      accept: 'application/json',
      'accept-language': 'zh-CN,zh;q=0.9',
      'cache-control': 'no-cache',
      'content-type': 'application/json;charset=UTF-8',
      pragma: 'no-cache'
    },
    body: JSON.stringify({
      history: JSON.stringify(
        _history.value
          .map(({ role, message }) => {
            if (!message) return
            return role === 'user'
              ? {
                  prompt: message
                }
              : {
                  response: message
                }
          })
          .filter((e) => !!e)
      ),
      question: question
    })
  })

  const reader = body?.getReader()
  const decoder = new TextDecoder()

  let newMessage: any[] = []
  function readStream(): any {
    return reader?.read().then(({ done, value }) => {
      if (done) {
        return newMessage
      }
      const chunk = decoder.decode(value)
      const events = chunk.split('\n\n').map((str) => {
        return str.replace(/data: ?/, '')
      })
      newMessage.push(...events.map((eventData) => {
        if (eventData) {
          try {
            const _eventData = decodeURIComponent(eventData)
            return JSON.parse(_eventData)
          } catch (e) {
            console.error('error in parsing', eventData)
          }
        }
      }))
      return readStream()
    })
  }
  return readStream()
}
const question = ref('')
watch(
  () => question.value,
  (val) => {
    adjustHeight()
  }
)

const submitBtnVisible = ref<boolean>(true)
function onclickEnter(e: KeyboardEvent) {
  if (e.ctrlKey) {
    submit()
  }
}
async function submit() {
  const _question = question.value
  if (!_question) {
    return
  }
  submitBtnVisible.value = false
  question.value = ''
  _history.value.push({
    role: 'user',
    message: _question,
    loading: false
  })
  const newMessage: { role: string; loading: boolean; message: string; metadata: string[] } = {
    role: 'system',
    loading: true,
    message: '',
    metadata: []
  }
  _history.value.push(newMessage)
  const res = await getAnswer(_question)
  _history.value[_history.value.length - 1].message = res
    .map((i: any) => i?.answer)
    .filter((e: any) => !!e)
    .join('')
  _history.value[_history.value.length - 1].metadata = res
    .map((e: any) => e?.metadata?.title)
    .filter((i: any) => !!i)
  _history.value[_history.value.length - 1].loading = false

  submitBtnVisible.value = true
  return
}
</script>

<style lang="less">
@keyframes gradientAnimation {
  0% {
    background-color: #7e5beb;
  }
  50% {
    background-color: rgba(126, 91, 235, 0.7);
  }
  100% {
    background-color: #7e5beb;
  }
}

.chat-extension—main {
  position: fixed;
  top: 100px;
  right: 10px;
  z-index: 9999;
  background-color: #262626;
  padding: 8px 16px;
  border: 1px solid #777;
  width: 800px;
  max-height: 750px;
  border-radius: 4px;
  display: flex;
  transition: all 0.5s;
  flex-direction: column;

  .chat-header {
    display: flex;
    &__collapse {
      img {
        position: relative;
        left: -10px;
      }
    }
    .chat-collapse-btn {
      border: none;
      background-color: transparent;
      img {
        width: 32px;
        height: 32px;
      }
      &:focus-visible {
        border-color: transparent;
      }
    }
  }
  #chat-log {
    //flex: 1;
    max-height: 300px;
    overflow-y: auto;
  }
  .user-area {
    display: flex;
    margin-top: 1rem;
    justify-content: center;
    align-items: center;
    max-height: 300px;
    .input-area {
      gap: 0.25rem;
      display: flex;
      align-items: center;
      flex: 1;
      textarea {
        min-height: 28px;
        width: 100%;
        //width: calc(100% - 10px);
        max-height: 160px;
        overflow-wrap: break-word;
        writing-mode: horizontal-tb;
        outline: 2px solid transparent;
        outline-offset: 2px;
        font-size: 1rem;
        line-height: 1.5rem;
        border-radius: 0.5rem;
        background-color: #323131;
        color: #fff;
        resize: none;
        overflow-y: auto;
        padding: 10px;
        box-sizing: border-box;
        border: 0 solid #e5e7eb;
      }
    }

    .submit {
      //&[disabled] {
      //  display: none;
      //  color: transparent;
      //  animation: gradientAnimation 1.2s linear infinite;
      //  position: relative;
      //}
      transition: background-color 1s ease-in-out;
      font-size: 1rem;
      line-height: 1.5rem;
      padding: 2px 8px;
      background-color: #7e5beb;
      color: rgb(255, 255, 255);
      border-radius: 4px;
      gap: 0.25rem;
      margin: 0 0 0 10px;
      box-sizing: border-box;
      border: 0 solid #e5e7eb;
    }
  }
}
.chat-extension—main__collapse {
  overflow: hidden;
  opacity: 0.8;
  right: -740px;
}
</style>
