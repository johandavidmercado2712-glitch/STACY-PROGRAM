import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { defineElement } from '@lordicon/element'
import App from './App.vue'
import './style.css'

defineElement()

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
