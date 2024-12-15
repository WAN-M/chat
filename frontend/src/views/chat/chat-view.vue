<script lang="ts" setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { SSE } from 'sse.js'
import botAva from '@/assets/bot.png'
import userAva from '@/assets/user.png'

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
          <!-- 遍历并显示每条消息 -->
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'message',
              message.type === 'USER' ? 'user-message' : 'assistant-message'
            ]"
          >
            <!-- 用户头像和消息内容 -->
            <div v-if="message.type === 'USER'" class="user-chat">
              <img class="avatar" :src="userAva" alt="User Avatar" />
              <div class="message-content">
                {{ message.textContent }}
              </div>
            </div>

            <!-- LLM头像和消息内容 -->
            <div v-else class="assistant-chat">
              <img class="avatar" :src="botAva" alt="Assistant Avatar" />
              <div class="message-content">
                {{ message.textContent }}
                <!-- 右下角显示加载动画 -->
                <span v-if="loadingMessageId === message.id" class="loading-dot">...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
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

      .message {
        display: flex;
        align-items: flex-start;
        margin: 10px 0;

        &.user-message {
          justify-content: flex-end;
          .user-chat {
            display: flex;
            flex-direction: row-reverse; /* 头像在右边 */
            align-items: center;
          }
        }

        &.assistant-message {
          justify-content: flex-start;
          .assistant-chat {
            display: flex;
            align-items: center;
          }
        }
      }

      .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 0 10px;
      }

      .message-content {
        max-width: 70%;
        padding: 10px 15px;
        background-color: #f1f1f1;
        border-radius: 10px;
        color: #333;
        position: relative;
      }
      .user-chat {
        margin-right: 10px;
      }
      .user-chat .message-content {
        background-color: #007bff;
        color: white;
        border-bottom-right-radius: 0;
      }

      .assistant-chat .message-content {
        background-color: #e5e5e5;
        color: black;
        border-bottom-left-radius: 0;
      }

      .loading-dot {
        position: absolute;
        right: -20px; // 向右移动至消息框外
        bottom: -10px; // 向下移动到消息框外
        font-size: 20px;
        color: #007bff;
      }
    }
  }
}
</style>
