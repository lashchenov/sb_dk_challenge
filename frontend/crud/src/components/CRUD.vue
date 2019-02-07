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
      <sui-table-row v-for="(item, idx) in items" :key="`tr-${table}-${item.name}`">
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
        <sui-table-cell @click="edit(item, idx)">
          <span>
            {{ item.related.map((i) => i.name).join(', ') }}
          </span>
          <div v-if="editable === idx">
            <sui-dropdown
              style="width: 380px"
              fluid
              multiple
              :options="m2m"
              v-model="addRelated"
              selection
            />
            <div style="margin-top: 10px">
              <div
                class="ui basic inverted green button"
                @click="commitRelated(item)"
              >
                <i class="save icon" />Save
              </div>
              <div
                class="ui basic inverted red button"
                @click.stop.prevent="editable = -1"
              >
                <i class="times icon" />Cancel
              </div>
            </div>
          </div>
        </sui-table-cell>
        <sui-table-cell>
          <div class="ui basic inverted red icon button" @click="remove(item)">
            <i class="trash icon" />
          </div>
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
        selected: {},
        addRelated: [],
        xhrCompleted: 0
      }
    },
    computed: {
      m2m() {
        let used = this.items[this.editable].related.map(i => i.id);
        return this.related
          .filter(i => !used.includes(i.id))
          .map((i) => { return { key: `${this.table}-${i.id}`, value: i.id, text: i.name }});
      }
    },
    watch: {
      addRelated(newVal, oldVal) {
        console.log(newVal, oldVal);
      },
      editable() {
        this.addRelated = []
      },
      xhrCompleted() {
        console.debug(`XHR COMPLETED: ${this.xhrCompleted === this.addRelated.length}`);
        if (this.xhrCompleted === this.addRelated.length) {
          this.editable = -1;
          this.$emit('refresh');
        }
      }
    },
    methods: {
      remove(item) {
        let xhr = new XMLHttpRequest(),
            url = `${apiUrl}/${this.table}/${item.id}`;
        xhr.open('DELETE', url, true);
        xhr.send();
        xhr.onload = () => { this.$emit('refresh')};
      },
      edit(item, idx) {
        this.editable = idx;
      },
      update($event, item) {
        $event.target.blur();
        let xhr = new XMLHttpRequest(),
            url = `${apiUrl}/${this.table}/${item.id}`,
            data = JSON.stringify({ name: $event.target.value });
        xhr.open('PUT', url, true);
        xhr.setRequestHeader('Content-Type', 'text/plain');
        item.name !== $event.target.value && xhr.send(data);
        xhr.onload = () => { this.$emit('refresh') };
      },
      commitRelated(item) {
        for (let id of this.addRelated) {
          let xhr = new XMLHttpRequest(),
            url = `${apiUrl}/${this.table}/${item.id}`,
            relatedField = `${this.th[1].toLowerCase().slice(0, -1)}_id`,
            json = {};
          json[relatedField] = id;
          let data = JSON.stringify(json);
          xhr.open('PUT', url, true);
          xhr.setRequestHeader('Content-Type', 'text/plain');
          xhr.send(data);
          xhr.onload = () => { this.xhrCompleted++ };
        }
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
