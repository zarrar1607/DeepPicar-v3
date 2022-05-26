import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { Dark, Quasar } from 'quasar'
import quasarUserOptions from './quasar-user-options'


const app = createApp(App)
app.use(Quasar, quasarUserOptions)
Dark.toggle()
app.use(router)
app.mount('#app')