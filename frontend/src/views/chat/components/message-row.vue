<script lang="ts" setup>
import TextLoading from './text-loading.vue'
import botAva from '@/assets/sjtulogored.png'
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
        <el-avatar :src="botAva" class="avatar" shape="square" style="background-color: transparent;"/>
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
          {{ message.content }}
        </div>
        <el-avatar :src="userAva" class="avatar" shape="square" style="background-color: transparent;"/>
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
        margin-right: 10px;
      }

      .message {
        max-width: 80%;
        border-radius: 7px;
        border: 1px solid rgba(0, 0, 0, 0.1);
      }
    }
  }

  &.right {
    justify-content: flex-end;

    .row {
      display: flex;
      align-items: center;
      justify-content: flex-end;

      .avatar {
        margin-left: 10px;
      }

      .message {
        padding: 10px;
        border-radius: 7px;
        max-width: 70%;
        background-color: var(--slight-pink);
        text-align: left;
        border: 1px solid rgba(0, 0, 0, 0.1);
      }
    }
  }
}
</style>
