<script lang="ts" setup>
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { SSE } from 'sse.js'
import { request } from '@/utils/request'
import MessageRow from './components/message-row.vue'
import MessageInput from './components/message-input.vue'
import SessionList from './components/session-list.vue'

const API_PREFIX = import.meta.env.VITE_API_PREFIX

const messageListRef = ref<InstanceType<typeof HTMLDivElement>>()
const sessionListRef = ref<InstanceType<typeof SessionList>>()
const loadingMessageId = ref<string | null>(null) // 标记当前 LLM 回复的消息ID
let evtSource: SSE | null = null

// 用户输入的文本
const inputText = ref('')

// 所有消息的数组
const messages = ref<{ id: string; role: 'user' | 'model'; content: string }[]>([])

// 获取指定Session的所有Message
const fetchMessages = async (sessionId: number) => {
  // 切断之前的SSE连接
  clearSSEResponse()

  // 与组件内保持一致
  if (sessionId === -1) {
    messages.value = []
    return
  }

  try {
    const all_message = await request.get(`/user/message/${sessionId}/`)
    messages.value = all_message.data
    
    await nextTick(() => {
      messageListRef.value?.scrollTo(0, messageListRef.value?.scrollHeight)
    })
  } catch (error) {
    ElMessage.error('发生错误')
  }
}

// 存储新消息
const newMessage = async (sessionId: number, role: string, content: string) => {
  const data = {
    'session_id': sessionId,
    'role': role,
    'content': content,
  }
  await request.post('/user/message/', data)
}

// 处理发送消息
const handleSendMessage = async (message: { text: string }) => {
  if (!message.text) {
    ElMessage.warning('请输入消息')
    return
  }

  if (sessionListRef.value?.selectedSessionId == -1) {
    ElMessage.warning('请创建新对话')
    return
  }

  const userMessage = {
    id: '0',
    content: message.text,
    role: 'user' as const
  }
  messages.value.push(userMessage)

  inputText.value = ''

  // 创建SSE连接
  const data = {
    session_id: sessionListRef.value?.selectedSessionId,
    message: message.text
  }
  evtSource = new SSE(API_PREFIX + '/chat/', {
    withCredentials: true,
    start: false,
    headers: {'Content-Type': 'application/json;charset=UTF-8'},
    payload: JSON.stringify(data),
    method: 'POST'
  })

  const assistantMessage = {
    id: new Date().getTime().toString(),
    content: '',
    role: 'model' as const
  }
  messages.value.push(assistantMessage)
  loadingMessageId.value = assistantMessage.id // 标记为加载中

  // SSE 监听消息
  evtSource.addEventListener('message', async (event: any) => {
    const response = JSON.parse(event.data)
    if (response.result?.output?.content) {
      // 找到要更新的消息
      const assistantMessageIndex = messages.value.findIndex(
        msg => msg.id === loadingMessageId.value
      )

      if (assistantMessageIndex !== -1) {
        // 更新 LLM 消息内容
        messages.value[assistantMessageIndex].content += response.result.output.content
        // 强制 Vue 响应更新
        messages.value = [...messages.value]
      }

      // 滚动到底部
      await nextTick(() => {
        messageListRef.value?.scrollTo(0, messageListRef.value?.scrollHeight)
      })
    }

    // 判断是否结束
    if (response.result?.metadata?.finishReason?.toLowerCase() === 'stop') {
      clearSSEResponse()
    }
  })

  // 发起请求
  evtSource.stream()

  // 滚动到用户消息位置
  await nextTick(() => {
    messageListRef.value?.scrollTo(0, messageListRef.value?.scrollHeight)
  })
}

const clearSSEResponse = () => {
  if (evtSource) {
    // 保存未结束的回复
    const assistantMessageIndex = messages.value.findIndex(
      msg => msg.id === loadingMessageId.value
    )
    if (assistantMessageIndex !== -1 && sessionListRef.value) {
      newMessage(sessionListRef.value.selectedSessionId, 'model', messages.value[assistantMessageIndex].content)
    }

    evtSource.close()
    evtSource = null
    loadingMessageId.value = null
  }
}

// 刷新页面时切断SSE并保存回复
window.addEventListener('beforeunload', clearSSEResponse)

</script>

<template>
  <div class="home-view">
    <div class="side-panel">
      <SessionList ref="sessionListRef" @sessionSelected="fetchMessages"/>
    </div>

    <div class="chat-panel">
      <div class="message-panel">
        <div ref="messageListRef" class="message-list">
          <transition-group name="list">
            <message-row
              v-for="(message, index) in messages"
              :key="index"
              :message="message"
            ></message-row>
          </transition-group>
        </div>
        <message-input @send="handleSendMessage" :isLoading="loadingMessageId !== null"></message-input>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.home-view {
  width: 100vw;
  height: 100vh;
  display: flex;

  .side-panel {
    width: 20%;
    padding: 20px;
    background-color: var(--session-list-pink);
    border-right: 1px solid #ddd;
  }

  .chat-panel {
    width: 80%;
    display: flex;
    flex-direction: column;
    background-color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    align-items: center;

    .message-panel {
      width: 70%;
      height: 100%;
      display: flex;
      flex-direction: column;

      .message-list {
        padding: 15px;
        box-sizing: border-box;
        width: 100%;
        flex: 1;
        overflow-y: scroll;
        scrollbar-width: none;
      }
    }
  }
}
</style>
