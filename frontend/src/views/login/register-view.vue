<script lang="ts" setup>
import {
  ElAvatar,
  ElButton,
  ElCard,
  ElCol,
  ElForm,
  ElFormItem,
  ElInput,
  ElRow,
  ElMessage,
  type FormInstance,
  type FormRules
} from 'element-plus'
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import logo from '@/assets/sjtulogored.png'
import router from '@/router'
import background from '@/assets/flower-background.png'
import { request } from '@/utils/request'
import { assertFormValidate } from '@/utils/common'

const registerForm = reactive({
  email: '',
  nickname: '',
  password: '',
  verifyCode: ''
})
const ruleFormRef = ref<FormInstance>()

// 表单验证规则
const rules = reactive<FormRules<typeof registerForm>>({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { 
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, 
      message: '请输入有效的邮箱地址', 
      trigger: 'blur' 
    }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { 
      pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]{3,16}$/, 
      message: '昵称应由3到16个字符组成，允许中文、字母、数字或下划线', 
      trigger: 'blur' 
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { 
      pattern: /^.{6,16}$/, 
      message: '密码长度应介于6到16个字符之间', 
      trigger: 'blur' 
    }
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { 
      pattern: /^[a-zA-Z0-9]{6}$/, 
      message: '验证码无效', 
      trigger: 'blur' 
    }
  ]
})

// 发送验证码请求
const sendVerifyCode = async () => {
  try {
    await request.post('/user/send_code/', { email: registerForm.email })
    ElMessage.success('验证码发送成功')
  } catch (error) {
    ElMessage.error('验证码发送失败')
  }
}

// 注册请求
const handleRegister = async () => {
  if (!ruleFormRef.value) return
  await ruleFormRef.value.validate(
    assertFormValidate(() =>
      request.post('/user/register/', registerForm).then((res) => {
        ElMessage.success('注册成功！')
        router.replace({ path: '/login' })
      })
    )
  )
}

//点击回车键注册
const keyDown = (e: KeyboardEvent) => {
	if (e.key === 'Enter') {
		handleRegister()
	}
}

onMounted(() => {
  document.addEventListener('keydown', keyDown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', keyDown)
})
</script>

<template>
  <div>
    <img alt="背景图片" class="background" :src="background" />
    <el-row class="panel-wrapper" justify="center" align="middle">
      <el-col :xs="18" :sm="16" :md="14" :lg="10" :xl="10">
        <transition name="el-zoom-in-top">
          <el-card class="panel">
            <div class="content">
              <div class="panel-left">
                <el-avatar alt="logo" :size="80" shape="square" :src="logo" style="background-color: transparent;"></el-avatar>
                <div class="title">AI助手</div>
                <div class="description">你的专属知识库AI助手</div>
              </div>
              <div class="panel-right">
                <div class="title">注册账号</div>
                <el-form
                  ref="ruleFormRef"
                  :model="registerForm"
                  :rules="rules"
                  class="form"
                  label-position="top"
                  label-width="100px"
                >
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="registerForm.email"></el-input>
                  </el-form-item>
                  <el-form-item label="昵称" prop="nickname">
                    <el-input v-model="registerForm.nickname"></el-input>
                  </el-form-item>
                  <el-form-item label="密码" prop="password">
                    <el-input v-model="registerForm.password" type="password"></el-input>
                  </el-form-item>
                  <el-form-item label="验证码" prop="verifyCode">
                    <div class="sms">
                      <el-input v-model="registerForm.verifyCode"></el-input>
                      <el-button class="send-sms" @click="sendVerifyCode">发送验证码</el-button>
                    </div>
                  </el-form-item>
                </el-form>
                <div class="button-wrapper">
                  <el-button class="register" type="primary" @click="handleRegister" @keydown.enter="keyDown">
                    注册
                  </el-button>
                  <el-button class="login" link @click="router.replace('/login')">
                    登录
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
  margin-left: 50vh;

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
        background-color: var(--slight-pink);
        width: 50%;
        border-radius: 5px;
      }

      .panel-right {
        padding: 30px;
        width: 50%;

        .form {
          margin-top: 30px;

          .sms {
            display: flex;
            align-items: center;
            width: 100%;

            .send-sms {
              margin-left: 20px;
              
              &:hover {
                background-color: var(--light-red);
                color: var(--sjtu-red);
                border: none;
              }
            }
          }
        }

        .button-wrapper {
          margin-top: 40px;
          display: flex;
          justify-content: center;
          position: relative;

          .register {
            width: 120px;
            background-color: var(--sjtu-red);
            border: none;

            &:hover {
              background-color: var(--sjtu-red-darker);
              color: #c5c0c0
            }
          }

          .login {
            width: 120px;
            margin-left: 20px;
            border: 1px solid #c5c0c0;

            &:hover {
              background-color: var(--light-red);
              color: var(--sjtu-red);
              border: none;
            }
          }
        }
      }
    }
  }
}
</style>
