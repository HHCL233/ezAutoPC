import { generalFetch } from '@/utils/fetch';

interface GetConfigAPI {
    config: any,
    message: string,
    success: boolean
}

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
    static async getConfig() {
        try {
            const messages = await generalFetch("api/config")
            const data = await messages.json() as GetConfigAPI
            return { 'json': data['config'], 'success': true }
        } catch (error) {
            console.log("请求错误: ", error)
            return { 'success': false }
        }
    }
    static async saveConfig(config: any) {
        try {
            await generalFetch("api/config", {
                "method": "PUT",
                "body": JSON.stringify(config),
                "headers": {
                    "Content-Type": "application/json",
                },
            })
            return { 'success': true }
        } catch (error) {
            console.log("请求错误: ", error)
            return { 'success': false }
        }
    }
}