<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from '@/utils/request'

const sessionList = ref<Array<{ id: number; session_name: string }>>([]) // 存储所有session
const userName = ref<string>('') // 用户名
const selectedSessionId = ref<number | null>(null) // 当前选中的sessionId
const hoveredSessionId = ref<number | null>(null) // 当前悬停的sessionId

const emit = defineEmits<{
  (e: 'sessionSelected', sessionId: number): void
}>()

// 获取用户信息
const fetchUserName = async () => {
  try {
    const response = await request.get('/user/info/')
    userName.value = response.data.nickname
  } catch (error) {
    ElMessage.error('获取用户名失败')
  }
}

// 选择一个会话
const selectSession = (sessionId: number) => {
  selectedSessionId.value = sessionId
  emit('sessionSelected', sessionId)
}

// 获取所有Session数据
const fetchSessions = async () => {
  try {
    const session_list = await request.get('/user/session/')
    sessionList.value = session_list.data
  } catch (error) {
    ElMessage.error('发生错误')
  }
}

// 新建对话
const createSession = async () => {
  try {
    await request.post('/user/session/') // 假设创建会话接口
    fetchSessions()
  } catch (error) {
    ElMessage.error('创建对话失败')
  }
}

// 修改对话名称
const handleEdit = async (sessionId: number) => {
  try {
    const newSessionName = prompt('请输入新的对话名称:')
    if (newSessionName) {
      await request.put(`/user/session/${sessionId}/`, { session_name: newSessionName })
      fetchSessions()
    }
  } catch (error) {
    ElMessage.error('修改失败')
  }
}

// 删除对话
const handleDelete = async (sessionId: number) => {
  try {
    await request.delete(`/user/session/${sessionId}/`)
    fetchSessions() // 更新列表
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 初始化Session列表和用户名
onMounted(() => {
  fetchSessions()
  fetchUserName()
})
</script>

<template>
  <div class="session-list">
    <div class="top-bar">
      <div class="greeting">Hi, {{ userName }}</div>
      <div class="icons">
        <el-icon @click="createSession" title="新建会话"> <Plus /> </el-icon>
        <el-icon title="我的书架"> <Books /> </el-icon>
      </div>
    </div>

    <div
      v-for="session in sessionList"
      :key="session.id"
      class="session-item"
      @click="selectSession(session.id)"
      @mouseover="hoveredSessionId = session.id"
      @mouseleave="hoveredSessionId = null"
      :class="{'selected': selectedSessionId === session.id, 'hovered': hoveredSessionId === session.id}"
    >
      <span>{{ session.session_name }}</span>

      <el-dropdown v-if="selectedSessionId === session.id || hoveredSessionId === session.id">
        <span class="el-dropdown-link">
          <el-icon><MoreFilled /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click="handleEdit(session.id)">修改对话名称</el-dropdown-item>
            <el-dropdown-item @click="handleDelete(session.id)">删除对话</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.session-list {
  display: flex;
  flex-direction: column;
  flex: 1;

  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #f4f4f4;
    border-bottom: 1px solid #ddd;

    .greeting {
      font-size: 16px;
      font-weight: bold;
    }

    .icons el-icon {
      font-size: 20px;
      cursor: pointer;
      margin-left: 15px;
    }
  }

  .session-item {
    position: relative;
    padding: 10px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background-color 0.3s ease;
    border-radius: 8px;
    margin: 5px 0;

    &.selected {
      background-color: var(--light-red);
    }

    &.hovered:hover {
      background-color: #e0e0e0;
    }

    &:hover {
      background-color: #e0e0e0;
    }
  }

  .el-dropdown-link {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    outline: none;
  }

  .el-dropdown-menu__item {
    cursor: pointer;
  }

  .el-dropdown-menu__item:hover {
    background-color: #f0f0f0;
  }

  .el-icon-more {
    font-size: 18px;
  }
}
</style>
