import { createApp, h } from 'vue'
import Chat from './Chat.vue'
import './chat.css'

export function create() {
  const container = document.createElement('div')
  container.id = 'chat-window'
  document.body.appendChild(container)
  createApp({
    render: () => h(Chat)
  }).mount(`#chat-window`)
}
