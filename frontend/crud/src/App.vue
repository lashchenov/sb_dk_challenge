<template>
  <div id="app">
    <!--<img src="./assets/logo.png">-->
    <div
      class="ui inverted segment"
      :class="{loading: loading}"
    >
      <selector @switch="visible = $event"></selector>
      <crud
        v-if="visible === 'Books'"
        :items="books"
        :related="authors"
        :table="'books'"
        :th="['Books', 'Authors']"
        key="crud-table-books"
        @refresh="fetchRows('authors'); fetchRows('books')"
      />
      <crud
        v-else
        :items="authors"
        :related="books"
        :table="'authors'"
        :th="['Authors', 'Books']"
        key="crud-table-authors"
        @refresh="fetchRows('authors'); fetchRows('books')"
      />
    </div>
  </div>
</template>

<script>
  import 'babel-polyfill';

  import CRUD from './components/CRUD.vue';
  import Menu from './components/Menu.vue';

  import { apiUrl } from "./main";

  export default {
    name: 'app',
    components: {
      'selector': Menu,
      'crud': CRUD,
    },
    data () {
      return {
        books: [],
        authors: [],
        loading: true,
        visible: 'Books'
      }
    },
    methods: {
      fetchRows: async function(table) {
        this.loading = true;
        let tableResponse = await fetch(`http://localhost:8000/${table}/`);
        let tableJson = await tableResponse.json();
        let result = [];
        for (let obj of tableJson.result) {
          let response = await fetch(`${apiUrl}/${table}/rellist/${obj.id}`);
          let objects = await response.json();
          let related = { related: objects.result };
          result.push({...obj, ...related});
        }
        this[table] = result.sort((a, b) => a.id - b.id);
        this.loading = false;
      }
    },
    created() {
      this.fetchRows('books');
      this.fetchRows('authors');
    }
  }
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

body {
  background-color: #333;
}
</style>
