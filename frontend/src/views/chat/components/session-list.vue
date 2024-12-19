<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElDialog, ElButton, ElUpload, ElIcon } from 'element-plus'
import { request } from '@/utils/request'
import { Cloudy } from '@element-plus/icons-vue'

const sessionList = ref<Array<{ id: number; session_name: string }>>([]) // 存储所有session
const userName = ref<string>('') // 用户名
const selectedSessionId = ref<number | null>(null) // 当前选中的sessionId
const hoveredSessionId = ref<number | null>(null) // 当前悬停的sessionId
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
  selectedSessionId.value = sessionId
  emit('sessionSelected', sessionId)
}

// 新建对话
const createSession = async () => {
  try {
    await request.post('/user/session/') // 假设创建会话接口
    ElMessage.success('创建对话成功')
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

// 处理文件上传
const handleFileUpload = async (file: File) => {
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

onMounted(() => {
  fetchSessions()
  fetchUserName()
  fetchKnowledgeList()
})
</script>

<template>
  <div class="session-list">
    <div class="top-bar">
      <div class="greeting">Hi, {{ userName }}</div>
      <div class="icons">
        <el-icon @click="createSession" title="新建会话" style="margin: 10px;"> <Plus /> </el-icon>
        <el-icon @click="knowledgeBaseDialogVisible = true" title="我的知识库"> <Cloudy /> </el-icon>
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
    display: flex;
    justify-content: flex-end;
    padding-top: 15px;
    .button-knowledge {
      background-color: var(--sjtu-red);
      transition: background-color 0.3s;

      &:hover {
        color: #999494
      }
    }
  }
}
</style>
