<script lang="ts" setup>
import {
  ElAvatar,
  ElButton,
  ElCard,
  ElCol,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElRow,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { onMounted, reactive, ref, Transition } from 'vue'
import logo from '@/assets/sjtulogored.png'
import router from '@/router'
import background from '@/assets/background.jpg'
import { request } from '@/utils/request'

// 登录表单
const loginForm = reactive({
  email: '',
  password: ''
})
const ruleFormRef = ref<FormInstance>()
const rules = reactive<FormRules<typeof loginForm>>({
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { max: 16, min: 6, message: '密码长度介于6，16个字符' }
  ]
})

// 控制面板显示
const showPanel = ref(false)
onMounted(() => {
  setTimeout(() => {
    showPanel.value = true
  }, 1000)
})

// 登录请求处理
const handleLogin = async () => {
  try {
    const res = await request.post('/user/login/', loginForm)
    ElMessage.success('登录成功')
    await router.replace({ path: '/chat' })
  } catch (error) {
    ElMessage.error('登录失败')
    console.error(error)
  }
}
</script>

<template>
  <div>
    <img alt="背景图片" class="background" :src="background" />
    <el-row class="panel-wrapper" justify="center" align="middle">
      <el-col :xs="18" :sm="16" :md="14" :lg="10" :xl="10">
        <transition name="el-zoom-in-top">
          <el-card class="panel" v-if="showPanel">
            <div class="content">
              <div class="panel-left">
                <el-avatar alt="logo" :size="80" shape="square" :src="logo" style="background-color: transparent;"></el-avatar>
                <div class="title">AI助手</div>
                <div class="description">你的专属知识库AI助手</div>
              </div>
              <div class="panel-right">
                <div class="title">登录账号</div>
                <el-form
                  ref="ruleFormRef"
                  :model="loginForm"
                  :rules="rules"
                  class="form"
                  label-position="top"
                  label-width="100px"
                >
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="loginForm.email"></el-input>
                  </el-form-item>
                  <el-form-item label="密码" prop="password">
                    <el-input v-model="loginForm.password" type="password"></el-input>
                  </el-form-item>
                </el-form>
                <div class="button-wrapper">
                  <el-button class="login" type="primary" @click="handleLogin"> 登录 </el-button>
                  <el-button
                    class="register"
                    type="info"
                    size="small"
                    link
                    @click="() => router.push('/register')"
                  >
                    注册
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </transition>
      </el-col>
    </el-row>
  </div>
</template>

<style lang="scss" scoped>
.background {
  position: fixed;
  height: 100vh;
  width: 100vw;
  object-fit: cover;
  z-index: -10;
}

.panel-wrapper {
  height: 100vh;

  .panel {
    .content {
      display: flex;
      align-items: stretch;
      height: 50vh;

      .title {
        font-size: var(--el-font-size-extra-large);
        margin-top: 16px;
        font-weight: bold;
      }

      .description {
        margin-top: 20px;
        font-size: var(--el-font-size-base);
        color: var(--el-text-col);
      }

      .panel-left {
        box-sizing: border-box;
        padding: 30px;
        background-color: rgb(243, 245, 249);
        width: 50%;
        border-radius: 5px;
      }

      .panel-right {
        padding: 30px;
        width: 50%;

        .form {
          margin-top: 30px;
        }

        .button-wrapper {
          margin-top: 40px;
          display: flex;
          justify-content: center;
          position: relative;

          .login {
            width: 120px;
          }

          .register {
            position: absolute;
            right: 0;
            bottom: 0;
          }
        }
      }
    }
  }
}
</style>
