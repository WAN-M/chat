<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElDialog, ElButton, ElUpload, ElIcon, ElInput } from 'element-plus'
import { request } from '@/utils/request'
import { ChatRound, Collection } from '@element-plus/icons-vue'

const sessionList = ref<Array<{ id: number; session_name: string }>>([]) // 存储所有session
const userName = ref<string>('') // 用户名
const selectedSessionId = ref<number | null>(null) // 当前选中的sessionId
const hoveredSessionId = ref<number | null>(null) // 当前悬停的sessionId
const editingSessionId = ref<number | null>(null) // 正在编辑的sessionId
const editedSessionName = ref<string>('') // 正在编辑的session名称
const isEditing = ref<boolean>(false) // 标记是否正在编辑，用于防止重复提交
const knowledgeBaseDialogVisible = ref(false) // 控制知识库弹框显示
const knowledgeList = ref<Array<string>>([]) // 存储知识库列表

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

// 获取所有Session数据
const fetchSessions = async () => {
  try {
    const session_list = await request.get('/user/session/')
    sessionList.value = session_list.data
  } catch (error) {
    ElMessage.error('发生错误')
  }
}

// 获取所有知识库数据
const fetchKnowledgeList = async () => {
  try {
    const knowledge_list = await request.get('/user/knowledge/')
    knowledgeList.value = knowledge_list.data
  } catch (error) {
    ElMessage.error('获取知识库列表失败')
  }
}

// 删除知识库
const deleteKnowledge = async (knowledge: string) => {
  try {
    await request.delete(`/user/knowledge/${knowledge}/`)
    fetchKnowledgeList()
    ElMessage.success('知识库删除成功')
  } catch (error) {
    ElMessage.error('知识库删除失败')
  }
}

// 选择一个会话
const selectSession = (sessionId: number) => {
  if (sessionId == -1) {
    return
  }
  selectedSessionId.value = sessionId
  sessionStorage.setItem('selectedSessionId', sessionId.toString())
  emit('sessionSelected', sessionId)
}

// 新建对话
const createSession = async () => {
  try {
    await request.post('/user/session/') // 假设创建会话接口
    ElMessage.success('创建对话成功')
    sessionStorage.removeItem('selectedSessionId')
    updateSessions()
  } catch (error) {
    ElMessage.error('创建对话失败')
  }
}

// 开始编辑对话名称
const startEditingSession = (sessionId: number, currentName: string) => {
  editingSessionId.value = sessionId
  editedSessionName.value = currentName
  isEditing.value = true // 标记正在编辑
  nextTick(() => {
    const inputElement = document.getElementById(`edit-input-${sessionId}`) as HTMLInputElement
    if (inputElement) {
      inputElement.focus() // 自动聚焦输入框
    }
  })
}

// 提交编辑后的对话名称
const submitSessionNameEdit = async (sessionId: number) => {
  if (isEditing.value && editedSessionName.value) {
    isEditing.value = false // 禁止重复提交

    try {
      await request.put(`/user/session/${sessionId}/`, { session_name: editedSessionName.value })
      ElMessage.success('修改对话名称成功')
      updateSessions()
      editingSessionId.value = null // 结束编辑
    } catch (error) {
      ElMessage.error('修改对话名称失败')
    }
  }
}

// 删除对话
const handleDelete = async (sessionId: number) => {
  try {
    await request.delete(`/user/session/${sessionId}/`)
    sessionStorage.removeItem('selectedSessionId')
    updateSessions() // 更新列表
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 处理文件上传
const handleFileUpload = async (file: File) => {
  // 限制文件类型及大小
  const fileSuffix = file.name.substring(file.name.lastIndexOf(".") + 1);
  const whiteList = ["pdf"];
  if (whiteList.indexOf(fileSuffix) === -1) {
    ElMessage.error('上传文件只能是 pdf格式');
    return false;
  }
 
  const sizeOk = file.size / 1024 / 1024 < 20;
  if (!sizeOk) {
    ElMessage.error('上传文件大小不能超过 20MB');
    return false;
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    await request.post('/user/knowledge/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('知识库上传成功')
    fetchKnowledgeList()
  } catch (error) {
    ElMessage.error('知识库上传失败')
  }
}

const updateSessions = async () => {
  await fetchSessions()
  const storedSessionId = sessionStorage.getItem('selectedSessionId');
  let session_id = -1
  console.log(sessionList.value.length)
  if (storedSessionId) {
    session_id = parseInt(storedSessionId, 10);
  } else if (sessionList.value.length > 0) {
    session_id = sessionList.value[0].id;
  }
  console.log(session_id)
  selectSession(session_id)
}

onMounted(() => {
  fetchUserName()
  fetchKnowledgeList()
  updateSessions()
})
</script>

<template>
  <div class="session-list">
    <div class="top-bar">
      <div class="greeting">Hi, {{ userName }}</div>
      <div class="icons">
        <el-icon @click="createSession" title="新建会话"> <ChatRound /> </el-icon>
        <el-icon @click="knowledgeBaseDialogVisible = true" title="我的知识库"> <Collection /> </el-icon>
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
      <span>
        <el-input
          v-if="editingSessionId === session.id"
          v-model="editedSessionName"
          :id="`edit-input-${session.id}`"
          @blur="submitSessionNameEdit(session.id)"
          @keydown.enter="submitSessionNameEdit(session.id)"
          placeholder="请输入对话名称"
        />
        <span v-else>{{ session.session_name }}</span>
      </span>

      <el-dropdown
        v-if="selectedSessionId === session.id || hoveredSessionId === session.id"
      >
        <span class="el-dropdown-link" v-if="selectedSessionId === session.id">
          <el-icon class="more-icon"><MoreFilled /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu class="dropdown-menu" slot="dropdown">
            <el-dropdown-item @click="startEditingSession(session.id, session.session_name)">修改对话名称</el-dropdown-item>
            <el-dropdown-item @click="handleDelete(session.id)">删除对话</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
  <!-- 知识库弹框 -->
  <el-dialog
    class="dialog"
    v-model="knowledgeBaseDialogVisible"
    title="我的知识库"
    @close="knowledgeBaseDialogVisible = false"
    width="50%"
    :before-close="() => { knowledgeBaseDialogVisible = false }"
  >
    <el-card class="knowledge-card">
      <p v-if="knowledgeList.length === 0">暂无知识库</p>
      <div
        v-else
        v-for="knowledge in knowledgeList"
        :key="knowledge"
        class="knowledge-item"
      >
        <!-- 知识库内容，限制宽度，并支持滚动 -->
        <span class="knowledge-text">{{ knowledge }}</span>
        <!-- 删除图标靠右展示 -->
        <el-icon
          class="delete-icon"
          @click="deleteKnowledge(knowledge)"
          title="删除知识库"
        >
          <Delete />
        </el-icon>
      </div>
    </el-card>
    <el-upload
      class="upload-knowledge"
      :action="''"
      :show-file-list="false"
      :before-upload="handleFileUpload"
      accept=".pdf"
    >
      <el-button class="button-knowledge" slot="trigger" size="small" type="primary">上传知识库</el-button>
    </el-upload>
  </el-dialog>
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
    border-bottom: 1px solid #ddd;

    .greeting {
      font-size: 24px;
      font-weight: bold;
    }
    .icons .el-icon {
      font-size: 20px;
      cursor: pointer;
      margin: 10px;
      
    }
  }

  .el-icon {
    color: var(--sjtu-red);
    &:hover {
      color: var(--sjtu-red-darker)
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
    border-radius: 14px;
    color: #5e5757;

    &.selected {
      background-color: var(--light-red);
    }

    &.hovered:hover {
      background-color: var(--slight-pink);
    }

    &:hover {
      background-color: var(--slight-pink);
    }

    el-input {
      font-size: 16px;
      font-family: 'Arial', sans-serif;
      padding: 5px;
      border-radius: 4px;
      width: 150px;
    }

    span {
      font-size: 16px;
      font-family: 'Arial', sans-serif;
    }
  }

  .el-dropdown-link {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    outline: none;
  }
}

:deep(.el-dropdown-menu__item) {
  cursor: pointer;
  // color: #c79191;
  &:hover {
    color: var(--sjtu-red);
    background-color: var(--slight-pink);
  }
}

.dialog {
  .knowledge-card {
    position: relative;

    .knowledge-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;

      .knowledge-text {
        max-width: 90%;
        overflow-x: auto;
        white-space: nowrap;
        text-overflow: ellipsis;
        scrollbar-width: thin;
      }

      .delete-icon {
        cursor: pointer;
        color: #f56c6c;
        font-size: 18px;
      }

      .delete-icon:hover {
        color: var(--sjtu-red);
      }
    }
  }

  .upload-knowledge {
    text-align: right;
  }

  .button-knowledge {
    background-color: var(--sjtu-red);
    margin-top: 20px;
    border: none;

    &:hover {
      background-color: var(--sjtu-red-darker);
      color: #c5c0c0
    }
  }
}
</style>
