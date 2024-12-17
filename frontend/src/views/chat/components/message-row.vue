<script lang="ts" setup>
import TextLoading from './text-loading.vue'
import botAva from '@/assets/bot.png'
import userAva from '@/assets/user.png'
import MarkdownMessage from './markdown-message.vue'
import { defineProps } from 'vue'

const props = defineProps<{
  message: {
    id: string;
    content: string;
    role: 'user' | 'model';
  };
  avatar?: string;
}>()
</script>

<template>
  <div :class="['message-row', message.role === 'user' ? 'right' : 'left']">
    <div class="row">
      <template v-if="message.role === 'model'">
        <el-avatar :src="botAva" class="avatar" shape="square" />
        <div class="message">
          <markdown-message
            :type="message.role"
            :message="message.content"
            v-if="message.content"
          ></markdown-message>
          <TextLoading v-if="!message.content"></TextLoading>
        </div>
      </template>

      <template v-else>
        <div class="message">
          {{message.content}}
        </div>
        <el-avatar :src="avatar || userAva" class="avatar" shape="square" />
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.message-row {
  display: flex;
  margin-bottom: 10px;

  &.left {
    justify-content: flex-start;
    .row {
      display: flex;
      align-items: center;

      .avatar {
        margin-right: 10px; /* 机器人头像和消息之间的间距 */
      }

      .message {
        // background-color: #f4f4f5;
        border-radius: 7px;
        padding: 10px;
        max-width: 70%;
        border: 1px solid rgba(0, 0, 0, 0.1);
      }
    }
  }

  &.right {
    justify-content: flex-end;
    .row {
      display: flex;
      align-items: center;

      .avatar {
        margin-left: 10px; /* 用户头像和消息之间的间距 */
      }

      .message {
        background-color: rgb(231, 248, 255);
        border-radius: 7px;
        padding: 10px;
        max-width: 70%;
        border: 1px solid rgba(0, 0, 0, 0.1);
        text-align: right;
      }
    }
  }
}
</style>
