import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import 'mdui/mdui.css';
import 'mdui';
import { setColorScheme } from 'mdui/functions/setColorScheme.js';


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

setColorScheme('#0061a4');