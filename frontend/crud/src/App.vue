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
    <div class="ui inverted green button" @click="openAdd = true">
      <i class="plus icon"/>Add
    </div>
    <sui-modal basic inverted v-model="openAdd">
      <sui-modal-content>
        <div class="ui center aligned inverted segment">
        <div class="ui transparent inverted input">
          <input v-model="newItem" type="text" placeholder="Star typing here...">
        </div>
        <div class="ui inverted green button" @click="add">
          <i class="plus icon"/>Add
        </div>
        <div class="ui inverted red button" @click="openAdd = false; newItem = ''">
          <i class="times icon"/>Cancel
        </div>
        </div>
      </sui-modal-content>
    </sui-modal>
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
        visible: 'Books',
        openAdd: false,
        newItem: ''
      }
    },
    methods: {
      add() {
        let xhr = new XMLHttpRequest(),
          url = `${apiUrl}/${this.visible.toLowerCase()}`,
          data = JSON.stringify({ name: this.newItem });
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'text/plain');
        xhr.send(data);
        xhr.onload = () => {
          this.newItem = '';
          this.fetchRows(this.visible.toLowerCase());
          this.openAdd = false;
        };
        // this.openAdd = false;
      },
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
