<script lang="ts" setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage, ElDialog, ElButton, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { SSE } from 'sse.js'
import { request } from '@/utils/request'
import MessageRow from './components/message-row.vue'
import MessageInput from './components/message-input.vue'
import SessionList from './components/session-list.vue'

const API_PREFIX = import.meta.env.VITE_API_PREFIX

const messageListRef = ref<InstanceType<typeof HTMLDivElement>>()
const loadingMessageId = ref<string | null>(null) // 用于标记当前 LLM 回复的消息ID
const sessionList = ref<Array<{ id: number; session_name: string }>>([]) // 存储所有session
let selectedSessionId:number = -1 // 默认为 -1 表示需要新建会话

// 用户输入的文本
const inputText = ref('')

// 所有消息的数组
const messages = ref<{ id: string; role: 'user' | 'model'; content: string }[]>([])

// 获取指定Session的所有Message
const fetchMessages = async (sessionId: number) => {
  selectedSessionId = sessionId
  try {
    const all_message = await request.get(`/user/message/${sessionId}/`)
    messages.value = all_message.data
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

  const userMessage = {
    id: '0',
    content: message.text,
    role: 'user' as const
  }
  messages.value.push(userMessage)

  inputText.value = ''

  // 创建SSE连接
  const data = {
    session_id: selectedSessionId,
    message: message.text
  }
  const evtSource = new SSE(API_PREFIX + '/chat/', {
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
      console.log(assistantMessageIndex)
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
      evtSource.close()
      const assistantMessageIndex = messages.value.findIndex(
        msg => msg.id === loadingMessageId.value
      )
      newMessage(selectedSessionId, 'model', messages.value[assistantMessageIndex].content) // 存储完整回复
      loadingMessageId.value = null // 结束加载
    }
  })

  // 发起请求
  evtSource.stream()

  // 滚动到用户消息位置
  await nextTick(() => {
    messageListRef.value?.scrollTo(0, messageListRef.value?.scrollHeight)
  })
}

</script>

<template>
  <div class="home-view">
    <div class="side-panel">
      <SessionList @sessionSelected="fetchMessages"/>
    </div>

    <div class="chat-panel">
      <!-- 右侧的消息记录 -->
      <div class="message-panel">
        <div ref="messageListRef" class="message-list">
          <transition-group name="list">
            <message-row
              v-for="message in messages"
              :key="message.id"
              :message="message"
            ></message-row>
          </transition-group>
        </div>
        <!-- 输入框 -->
        <message-input @send="handleSendMessage"></message-input>
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
    background-color: #f4f4f4;
    border-right: 1px solid #ddd;
  }

  .chat-panel {
    width: 80%;
    display: flex;
    flex-direction: column;
    background-color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

    .message-panel {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;

      .message-list {
        padding: 15px;
        width: 100%;
        flex: 1;
        overflow-y: scroll;
      }
    }
  }
}
</style>
