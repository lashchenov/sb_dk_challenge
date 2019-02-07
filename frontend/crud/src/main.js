import Vue from 'vue'
import App from './App.vue'

import SuiVue from 'semantic-ui-vue';

Vue.use(SuiVue);

export let apiUrl = 'http://localhost:8000';

new Vue({
  el: '#app',
  render: h => h(App)
});
