<script lang="ts" setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { SSE } from 'sse.js'
import MessageRow from './components/message-row.vue'
import MessageInput from './components/message-input.vue'

const API_PREFIX = import.meta.env.VITE_API_PREFIX

const messageListRef = ref<InstanceType<typeof HTMLDivElement>>()
const loadingMessageId = ref<string | null>(null) // 用于标记当前 LLM 回复的消息ID

// 用户输入的文本
const inputText = ref('')

// 所有消息的数组
const messages = ref<{ id: string; type: 'USER' | 'ASSISTANT'; textContent: string }[]>([])

// 处理发送消息
const handleSendMessage = async (message: { text: string }) => {
  if (!message.text) {
    ElMessage.warning('请输入消息')
    return
  }

  // 用户消息
  const userMessage = {
    id: new Date().getTime().toString(),
    textContent: message.text,
    type: 'USER' as const
  }
  messages.value.push(userMessage)

  // 清空输入框
  inputText.value = ''

  // 创建SSE连接，直接传递 message 参数
  const form = new FormData()
  form.set('message', message.text) // 只传 message 参数
  const evtSource = new SSE(API_PREFIX + '/chat/', {
    withCredentials: true,
    start: false,
    payload: form as any,
    method: 'POST'
  })

  // 新建 LLM 回复消息对象
  const assistantMessage = {
    id: new Date().getTime().toString(),
    textContent: '',
    type: 'ASSISTANT' as const
  }
  messages.value.push(assistantMessage)
  loadingMessageId.value = assistantMessage.id // 标记为加载中

  // SSE 监听消息
  evtSource.addEventListener('message', async (event: any) => {
    const response = JSON.parse(event.data)
    if (response.result?.output?.content) {
      // 找到要更新的消息
      // assistantMessage.textContent += response.result.output.content
      const assistantMessageIndex = messages.value.findIndex(
        msg => msg.id === loadingMessageId.value
      )
      if (assistantMessageIndex !== -1) {
        // 更新 LLM 消息内容
        messages.value[assistantMessageIndex + 1].textContent += response.result.output.content
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
    <div class="chat-panel">
      <!-- 右侧的消息记录 -->
      <div class="message-panel">
        <div ref="messageListRef" class="message-list">
          <!-- 过渡效果 -->
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
  align-items: center;
  justify-content: center;

  .chat-panel {
    display: flex;
    background-color: white;
    width: 90%;
    height: 90%;
    box-shadow: 0 0 10px rgba(black, 0.1);
    border-radius: 10px;

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
