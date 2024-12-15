<script lang="ts" setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { SSE } from 'sse.js'

const API_PREFIX = import.meta.env.VITE_API_PREFIX

const messageListRef = ref<InstanceType<typeof HTMLDivElement>>()
const loading = ref(false)

// 用户输入的文本
const inputText = ref('')

// ChatGPT的回复
const responseMessage = ref({
  id: new Date().getTime().toString(),
  type: 'ASSISTANT',
  textContent: ''
})

// 处理发送消息
const handleSendMessage = async (message: { text: string }) => {
  if (!message.text) {
    ElMessage.warning('请输入消息')
    return
  }

  loading.value = true

  // 创建SSE连接，直接传递 message 参数
  const form = new FormData()
  form.set('message', message.text) // 只传 message 参数
  const evtSource = new SSE(API_PREFIX + '/chat/', {
    withCredentials: true,
    start: false,
    payload: form as any,
    method: 'POST'
  })

  evtSource.addEventListener('message', async (event: any) => {
    console.log(event)
    const response = JSON.parse(event.data)
    if (response.result?.output?.content) {
      responseMessage.value.textContent += response.result.output.content

      // 滚动到底部
      await nextTick(() => {
        messageListRef.value?.scrollTo(0, messageListRef.value.scrollHeight)
      })
    }

    if (response.result?.metadata?.finishReason?.toLowerCase() === 'stop') {
      evtSource.close()
      loading.value = false
    }
  })

  // 发起请求
  evtSource.stream()

  // 清空输入框
  inputText.value = ''

  // 滚动到用户消息位置
  await nextTick(() => {
    messageListRef.value?.scrollTo(0, messageListRef.value.scrollHeight)
  })
}
</script>

<template>
  <div class="home-view">
    <div class="chat-panel" v-loading="loading">
      <!-- 右侧的消息记录 -->
      <div class="message-panel">
        <div ref="messageListRef" class="message-list">
          <!-- 显示回复消息 -->
          <div class="message" v-if="responseMessage.textContent">
            {{ responseMessage.textContent }}
          </div>
        </div>
        <!-- 监听发送事件 -->
        <div class="message-input">
          <el-input
            v-model="inputText"
            placeholder="请输入您的问题"
            @keydown.enter="handleSendMessage({ text: inputText })"
          />
        </div>
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

      .message-input {
        padding: 20px;
      }
    }
  }
}
</style>
