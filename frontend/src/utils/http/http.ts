import axios from 'axios'
import { BASE_HOST, ADMIN_HOST} from '@/constants/host.constant'

export const http = axios.create({
  // baseURL: ADMIN_HOST,
  withCredentials: true
})
