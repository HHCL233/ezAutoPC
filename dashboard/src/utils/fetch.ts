import io from 'socket.io-client';

export async function generalFetch(url = "", data = {}) {
    try {
        const response = await fetch(`http://${location.hostname}:5000/${url}`, data);
        return response
    } catch (error) {
        console.log(`请求端点1错误 ${error},尝试其他URL`);
        try {
            const response = await fetch(`http://${location.host}/${url}`, data);
            return response
        } catch (error2) {
            throw new Error(`所有请求端点均失败,最后错误:${error2}`);
        }
    }

}

export function generalWS(url = "", errorCallback?: () => void) {
    try {
        const socket = io(`http://${location.hostname}:5000/${url}`, {
            transports: ['websocket'],
            reconnection: false,
            reconnectionAttempts: 5,
        });
        return socket
    } catch (error) {
        console.log(`IO请求端点1错误 ${error},尝试其他URL`);
        try {
            const socket = io(`http://${location.host}/${url}`, {
                transports: ['websocket'],
                reconnection: true,
                reconnectionAttempts: 5,
            });
            return socket
        } catch (error2) {
            if (errorCallback) {
                errorCallback()
            }
            throw new Error(`所有IO请求端点均失败,最后错误:${error2}`);
        }
    }

}