<script setup lang="ts">
import { ApiFetch } from '@/utils/apiFetch';
import { onMounted, ref } from 'vue';
import { upperFirst, camelCase } from 'lodash'

let config: any = null
const autoPCConfigJson = ref<any>({})
onMounted(async () => {
    config = await ApiFetch.getConfig()
    if (config.success == true && config.json) {
        autoPCConfigJson.value = config.json.autopc
    }
})

const savaConfig = (async () => {
    await ApiFetch.saveConfig(config['json'])
})
</script>
<template>
    <div class="setting-autopc">
        <h2>本体设置</h2>
        <mdui-list class="setting-autopc-lists">
            <mdui-list-item :headline="camelCase(`${key}`)""
                v-for="(value, key, index) in autoPCConfigJson" :description="config.json.descriptions[key]">
                <mdui-text-field slot="end-icon" class="setting-autopc-list-text-field" :value="value"
                    v-if="(typeof value) != 'boolean'" :autosize="(String(key).includes('lines_')) ? true : false"
                    @change="autoPCConfigJson[key] = $event.target.value"></mdui-text-field>
                <mdui-switch v-else :checked="value" slot="end-icon"
                    @change="autoPCConfigJson[key] = ($event.target.checked)"></mdui-switch>
            </mdui-list-item>
        </mdui-list>
        <mdui-fab icon="save" class="setting-autopc-save" @click="savaConfig()"></mdui-fab>
    </div>
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
    min-height: 36px;
    cursor: text;
    transform: scale(0.8);
    margin-right: -48px;
}

.setting-autopc-save {
    position: fixed;
    right: 36px;
    bottom: 36px;
}
</style>