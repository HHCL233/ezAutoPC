import { generalFetch } from '@/utils/fetch';

export class ApiFetch {
    static async getAllMessages() {
        try {
            const messages = await generalFetch("api/getAllMessages")
            return { 'json': messages.json(), 'success': true }
        } catch (error) {
            console.log("请求错误: ", error)
            return { 'success': false }
        }
    }
}