<script setup lang="ts">
import { ApiFetch } from '@/utils/apiFetch';
import { onMounted, ref } from 'vue';
import { upperFirst, camelCase } from 'lodash';
import { useConfigStore } from '@/stores/config';
import { isDictionary } from '@/utils/type';
import { dialog } from 'mdui/functions/dialog.js';

import type { Tab } from 'mdui/components/tab.js';
import type { Dialog } from 'mdui/components/dialog.js';
import type { TextField } from 'mdui/components/text-field.js';

const autoPCConfigJson = ref<any>({})
const config = useConfigStore()
const settingAutopcConfigTabs = ref<Tab | null>(null)
const objectEdit = ref<Dialog | null>(null)
const objectEditField = ref<TextField | null>(null)

let currentEditKey = ''
let editErrorText = ''

onMounted(async () => {
    await config.getConfig()
    if (config.config.autopc.config_index >= config.config.autopc.config_list.length) {
        correctCurrentIndex(true)
    } else {
        correctCurrentIndex()
    }
})

const savaConfig = (async () => {
    await config.pushConfig()
})

const convertByOriginalType = ((value: any, originalValue: any) => {
    return originalValue.constructor(value);
})

const changeConfigIndex = (async (index: number) => {
    config.config.autopc.config_index = index
    correctCurrentIndex()
    await config.pushConfig()
})

const newConfig = (async () => {
    config.config.autopc.config_list.push(JSON.parse(JSON.stringify(config.config.autopc.template)))
    await config.pushConfig()
    correctCurrentIndex(true)
})

const middleDeleteConfig = (async (event: any, index: number) => {
    if (event.button === 1) {
        deleteConfig(index)
    }
})

const deleteConfig = (async (index: number) => {
    config.config.autopc.config_list.splice(index, 1)
    await config.pushConfig()
    correctCurrentIndex(true)
})

const correctCurrentIndex = ((end?: boolean) => {
    if (end) {
        config.config.autopc.config_index = config.config.autopc.config_list.length - 1
    }
    autoPCConfigJson.value = config.config.autopc.config_list[config.config.autopc.config_index]
    if (settingAutopcConfigTabs.value) {
        settingAutopcConfigTabs.value.value = `tab-${config.config.autopc.config_index}`
    }
    if (end) {
        config.config.autopc.config_index = config.config.autopc.config_list.length
    }
})

const saveObjectEdit = (() => {
    if (!objectEdit.value || !objectEditField.value) return
    const helper = objectEditField.value.querySelector('span')
    try {
        const val = objectEditField.value.value
        const json = JSON.parse(val)
        autoPCConfigJson.value[currentEditKey] = json
        editErrorText = ''
        if (helper) helper.innerHTML = ''
        objectEdit.value.open = false
    } catch (e) {
        editErrorText = `JSON解析错误 ${e}`
        if (helper) helper.innerHTML = editErrorText
    }
})

const showObjectEdit = ((value: object, name: string) => {
    if (!objectEdit.value || !objectEditField.value) return
    currentEditKey = name
    editErrorText = ''
    objectEditField.value.value = JSON.stringify(value, null, 4)
    const helper = objectEditField.value.querySelector('span')
    if (helper) helper.innerHTML = ''
    objectEdit.value.open = true
})
</script>

<template>
    <div class="setting-autopc">
        <h2>本体设置</h2>
        <mdui-tabs value="tab-0" class="setting-autopc-config-tabs" full-width ref="settingAutopcConfigTabs">
            <mdui-tab v-for="(value, index) in config.config?.autopc?.config_list" :value="`tab-${index}`"
                @click="changeConfigIndex(Number(index))" @mousedown="middleDeleteConfig($event, Number(index))"
                class="setting-autopc-config-tab">
                <span slot="custom" class="setting-autopc-config-name">配置 {{ index }}</span>
                <mdui-button-icon icon="delete" slot="custom" class="setting-autopc-config-delete"
                    @click="deleteConfig(Number(index))"></mdui-button-icon>
            </mdui-tab>
            <mdui-tab :value="`tab-new`" @click="newConfig()">新建配置</mdui-tab>
        </mdui-tabs>
        <mdui-list class="setting-autopc-lists">
            <mdui-list-item :headline="camelCase(`${key}`)" :key="key" v-for="(value, key, index) in autoPCConfigJson"
                :description="config.config.descriptions[key]">
                <mdui-text-field slot="end-icon" class="setting-autopc-list-text-field" :value="value"
                    v-if="(typeof value) == 'string'" :type="typeof value == 'number' ? 'number' : 'text'"
                    :autosize="(String(key).includes('lines_')) ? true : false"
                    @change="autoPCConfigJson[key] = convertByOriginalType($event.target.value, autoPCConfigJson[key])"></mdui-text-field>
                <mdui-button v-else-if="isDictionary(value)" slot="end-icon"
                    @click="showObjectEdit(value, String(key))">编辑</mdui-button>
                <mdui-switch v-else :checked="value" slot="end-icon"
                    @change="autoPCConfigJson[key] = convertByOriginalType($event.target.checked, autoPCConfigJson[key])"></mdui-switch>
            </mdui-list-item>
        </mdui-list>
        <mdui-fab icon="save" class="setting-autopc-save" @click="savaConfig()"></mdui-fab>
    </div>

    <mdui-dialog close-on-overlay-click fullscreen headline="编辑" class="object-edit" ref="objectEdit">
        <mdui-text-field autosize label="" class="object-edit-field" ref="objectEditField">
            <span slot="helper" style="color: red"></span>
        </mdui-text-field>
        <mdui-button slot="action" variant="tonal" @click="saveObjectEdit()">确定</mdui-button>
    </mdui-dialog>
</template>

<style scoped>
.setting-autopc-lists {
    margin: -8px -16px;
}

.setting-autopc {
    margin: 16px;
}

.setting-autopc-list-text-field {
    width: 480px;
    cursor: text;
}

.setting-autopc-save {
    position: fixed;
    right: 36px;
    bottom: 36px;
}

.setting-autopc-config-delete {
    height: 24px;
    width: 24px;
    margin-left: 24px;
}

.object-edit-field {
    min-width: 100%;
}
</style>