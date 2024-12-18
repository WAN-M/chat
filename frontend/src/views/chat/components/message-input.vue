<script lang="ts" setup>
import { ref } from 'vue'
import { Position } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

type Message = {
  text: string
}
const emit = defineEmits<{
  send: [message: Message]
}>()

// 输入框内的消息
const message = ref<Message>({ text: '' })

const sendMessage = () => {
  if (!message.value.text) {
    ElMessage.warning('请输入消息')
    return
  }
  emit('send', message.value)
  // 发送完清除
  message.value = { text: '' }
}
</script>

<template>
  <div class="message-input">
    <div class="input-container">
      <el-input
        v-model="message.text"
        type="textarea"
        resize="none"
        placeholder="请输入消息..."
        :autosize="{ minRows: 1, maxRows: 2 }"
        class="input-box"
        style="background-color: #f5f5f5;"
        @keydown.enter.prevent="sendMessage"
      />
      <div class="send-button" @click="sendMessage">
        <el-icon size="20">
          <Position />
        </el-icon>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.message-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 20%;
  background-color: #fff;

  .input-container {
    position: relative;
    display: flex;
    align-items: center;
    background-color: #f5f5f5;
    border-radius: 20px;
    padding: 10px 15px;
    box-sizing: border-box;

    ::v-deep .input-box .el-textarea__inner {
      box-shadow: none !important;
      flex: 1;
      background-color: transparent;
      outline: none;
      font-size: 14px;
      box-sizing: border-box;
      padding: 5px 0; 
    }

    .send-button {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #409eff; /* 发送按钮颜色 */
      color: #fff;
      border-radius: 50%; /* 圆形按钮 */
      cursor: pointer;
      margin-left: 5px; /* 按钮与输入框间距 */
      transition: background-color 0.3s;

      &:hover {
        background-color: #66b1ff;
      }
    }
  }
}
</style>
