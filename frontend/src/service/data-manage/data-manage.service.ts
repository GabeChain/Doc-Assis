import { http } from '@/utils/http'
export class DataManageService {
  static getList = async () => http('api/combine', { method: 'GET' })

  static checkStatus = async (data: Record<string, any>) =>
    http('api/task_status', { method: 'GET', params: data })

  static deleteOld = async (data: Record<string, any>) =>
    http('api/delete_old', { method: 'GET', params: data })
}
