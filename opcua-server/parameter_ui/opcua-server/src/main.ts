import './assets/style.css';

import { createApp } from 'vue';
import { Quasar, Dark } from 'quasar';
import '@quasar/extras/material-icons/material-icons.css';
import 'quasar/src/css/index.sass';

import App from './App.vue';

const myApp = createApp(App);

myApp.use(Quasar, {
  plugins: {},
});
Dark.set(true);

myApp.mount('#app');
