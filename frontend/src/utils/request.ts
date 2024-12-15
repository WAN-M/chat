import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const BASE_URL = import.meta.env.VITE_API_PREFIX
axios.defaults.withCredentials = true;
export const request = axios.create({
  baseURL: BASE_URL,
  timeout: 60000
})
request.interceptors.response.use(
  (res) => {
    return res.data
  },
  ({ res }) => {
    if (res.data.code !== 200) {
      ElMessage.warning({ message: res.data.message })
    }
    // FIX 似乎没起作用，后面再调试
    // token存储在cookie中，如果之前登录过，想重新登录，此时发送登录请求同样会携带token，不符合预期：1. 前端不携带token 2. 后端不验证登录接口的token
    if (res.data.code === 401) {
      router.push('/login')
    }
    return Promise.reject(res.data)
  }
)
