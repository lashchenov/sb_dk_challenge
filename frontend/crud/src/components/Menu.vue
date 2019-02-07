<template>
    <sui-menu pointing secondary inverted>
      <a
        v-for="item in items"
        is="sui-menu-item"
        :acitve="active == item"
        :key="item"
        :content="item"
        @click="select(item)"
      />
    </sui-menu>
</template>

<script>
    export default {
      name: "Menu",
      data() {
        return {
          active: 'Books',
          items: [
            'Books',
            'Authors'
          ]
        }
      },
      methods: {
        select(item) {
          this.$emit('switch', item);
        }
      }
    }
</script>

<style scoped>

</style>
