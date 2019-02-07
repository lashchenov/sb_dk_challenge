<template>
  <sui-table selectable celled inverted>
    <sui-table-header>
      <sui-table-row>
        <sui-table-header-cell>{{ th[0] }}</sui-table-header-cell>
        <sui-table-header-cell>{{ th[1] }}</sui-table-header-cell>
        <sui-table-header-cell></sui-table-header-cell>
      </sui-table-row>
    </sui-table-header>
    <sui-table-body>
      <sui-table-row v-for="(item, idx) in items" :key="`tr-${table}-${item.name}`" @click="edit(item)">
        <sui-table-cell>
          <div class="ui inverted transparent input">
            <input
              @blur="update($event, item)"
              @keypress.enter="update($event, item)"
              type="text"
              :value="item.name"
            >
          </div>
        </sui-table-cell>
        <sui-table-cell @click="editable = editable === idx ? -1 : idx">
          <span>
            {{ item.related.map((i) => i.name).join(', ') }}
          </span>
          <sui-dropdown
            v-if="editable === idx"
            fluid
            multiple
            :options="m2m"
            selection
          />
        </sui-table-cell>
        <sui-table-cell>
          <sui-icon name="times" @click="remove(item)" />
        </sui-table-cell>
      </sui-table-row>
    </sui-table-body>
  </sui-table>
</template>

<script>
  import { apiUrl } from "../main";

  export default {
    name: "CRUD",
    props: [
      'items',
      'related',
      'th',
      'table'
    ],
    data() {
      return {
        editable: -1,
        selected: {}
      }
    },
    computed: {
      m2m() {
        return this.related.map((i) => { return { key: `${this.table}-${i.id}`, value: i.id, text: i.name }});
      }
    },
    methods: {
      remove(item) {
        let xhr = new XMLHttpRequest(),
            url = `${apiUrl}/${this.table}/${item.id}`;
        xhr.open('DELETE', url, true);
        xhr.send();
        xhr.onload = () => { this.$emit('refresh')};
        // this.$emit('refresh');
      },
      edit(item) {
        item.editable = true;
        console.log(item);
      },
      update($event, item) {
        $event.target.blur();
        let xhr = new XMLHttpRequest(),
            url = `${apiUrl}/${this.table}/${item.id}`,
            data = JSON.stringify({ name: $event.target.value });
        xhr.open('PUT', url, true);
        xhr.setRequestHeader('Content-Type', 'text/plain');
        item.name !== $event.target.value && xhr.send(data);
      }
    }
  }
</script>

<style scoped>
  /*td,th {*/
    /*width: 50%;*/
  /*}*/
  td:last-child {
    width: 3%
  }
  .input {
    width: 100%;
  }
</style>
