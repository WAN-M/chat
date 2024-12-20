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
    return res
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      ElMessage.warning({ message: data.message || '请求错误' })

      if (status === 401) {
        ElMessage.error('未授权，跳转到登录页面')
        router.push('/login')
      }
    }

    return Promise.reject(error.response ? error.response.data : error)
  }
)
