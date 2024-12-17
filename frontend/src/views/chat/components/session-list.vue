<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from '@/utils/request'

const sessionList = ref<Array<{ id: number; session_name: string }>>([]) // 存储所有session

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
    await request.post('/user/session/')
    fetchSessions() // 刷新会话列表
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
      fetchSessions() // 更新列表
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

// 初始化Session列表
onMounted(fetchSessions)
</script>

<template>
    <div class="session-list">
      <!-- 新建对话按钮 -->
      <div class="new-session">
        <el-button type="primary" @click="createSession">新建对话</el-button>
      </div>
      <div
        v-for="session in sessionList"
        :key="session.id"
        class="session-item"
      >
        <span>{{ session.session_name }}</span>
  
        <!-- 设置按钮 -->
        <el-dropdown trigger="click">
          <el-button class="el-dropdown-link" size="small">
            <i class="el-icon-more"></i>
          </el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click="handleEdit(session.id)">修改对话名称</el-dropdown-item>
            <el-dropdown-item @click="handleDelete(session.id)">删除对话</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
  </template>

<style lang="scss" scoped>
.session-list {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.new-session {
  margin-bottom: 15px;
}

.new-session .el-button {
  width: 100%;
  padding: 10px 0;
  font-size: 14px;
}

.session-item {
  position: relative;
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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
</style>
