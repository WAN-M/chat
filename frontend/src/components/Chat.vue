<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" :class="message.sender">
        <p>{{ message.text }}</p>
      </div>
    </div>
    <div class="input-area">
      <input v-model="userInput" @keypress.enter="sendMessage" placeholder="Type a message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      userInput: '',  // 存储用户输入
      messages: []  // 存储消息历史记录
    };
  },
  methods: {
    async sendMessage() {
      if (this.userInput.trim() === '') return;  // 防止发送空消息
      // 显示用户消息
      this.messages.push({ text: this.userInput, sender: 'user' });
      const userMessage = this.userInput;  // 备份用户输入
      this.userInput = '';  // 清空输入框

      try {
        // 调用后端 API，发送用户输入给 Django 后端
        const response = await axios.post('http://localhost:8000/chat/', { message: userMessage });
        // 显示返回的 LLM 输出
        this.messages.push({ text: response.data.reply, sender: 'bot' });
      } catch (error) {
        console.error('Error communicating with the server:', error);
        this.messages.push({ text: 'Error connecting to the server.', sender: 'bot' });
      }
    }
  }
};
</script>

<style scoped>
.chat-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid #ddd;
  padding: 10px;
  background-color: #f9f9f9;
}

.messages {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.user {
  text-align: right;
  color: blue;
}

.bot {
  text-align: left;
  color: green;
}

.input-area {
  display: flex;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
}

button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
