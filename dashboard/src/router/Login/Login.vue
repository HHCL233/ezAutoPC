<script setup lang="ts">
import { useConfigStore } from '@/stores/config';
import { ref } from 'vue';
import type { TextField } from 'mdui/components/text-field.js';
import { generalFetch } from '@/utils/fetch';
import { dialog } from "mdui/functions/dialog.js";

const config = useConfigStore()
const loginAccount = ref<TextField | null>(null)
const loginPassword = ref<TextField | null>(null)

const login = async () => {
    if (!loginAccount.value || !loginPassword.value) {
        return;
    }
    const account = loginAccount.value.value
    const password = loginPassword.value.value
    const loginFetch = await generalFetch("api/login", {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            username: account,
            password: password
        }),
    })
    if (loginFetch.status != 200) {
        dialog({
            headline: "遇到了错误",
            description: (await loginFetch.json())?.msg,
            actions: [
                {
                    text: "确定",
                }
            ]
        });
    } else {
        dialog({
            headline: "登录成功",
            description: (await loginFetch.json())?.msg,
            actions: [
                {
                    text: "确定",
                }
            ]
        });
    }
}
</script>
<template>
    <div class="login">
        <h1 class="login-title">登录 ezAutoPC</h1>
        <mdui-text-field variant="outlined" label="账号" class="login-text-field" ref="loginAccount"></mdui-text-field>
        <mdui-text-field variant="outlined" label="密码" type="password" toggle-password class="login-text-field"
            ref="loginPassword"></mdui-text-field>
        <mdui-button class="login-button" @click="login()">登录</mdui-button>
    </div>
</template>
<style scoped>
.login {
    margin: 24px;
}

.login-title {
    font-weight: normal;
}

.login-text-field {
    margin: 0 16px 16px 0;
}

.login-button {
    float: right;
}
</style>