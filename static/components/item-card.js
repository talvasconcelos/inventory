window.app.component('item-card', {
  name: 'item-card',
  props: {
    item: {
      required: true
    }
  },
  data() {
    return {}
  },
  computed: {
    chipColor() {
      if (!this.item.quantity_in_stock) return 'grey'
      return this.item.quantity_in_stock <= this.item.reorder_threshold
        ? 'red'
        : 'green'
    }
  },
  methods: {},
  created() {
    console.log(typeof this.item)
  },
  template: `
  <q-card class="item-card" clickable>
    <q-card-section horizontal>
      <q-img
        class="col-5"
        :src="item.img || 'https://cdn.quasar.dev/img/parallax1.jpg'"
      ></q-img>

      <q-card-section class="overflow-hidden">
        <div class="text-h6 ellipsis q-pb-md" v-text="item.name"></div>
        <div
          class="text-subtitle1 ellipsis q-pb-md"
          v-text="item.description || ' ' "
        ></div>
        <div class="text-subtitle1 text-justify">
          <div>
            <span>Price: </span>
            <span v-text="item.price"></span>
          </div>
        </div>
      </q-card-section>
    </q-card-section>

    <q-separator></q-separator>

    <q-card-actions>
      <q-chip square>
        <div v-if="item.quantity_in_stock">
          <q-avatar
            :color="chipColor"
            text-color="white"
          >
            <span v-text="item.quantity_in_stock"></span>
          </q-avatar>
          Available In Stock
        </div>
      </q-chip>
    </q-card-actions>
  </q-card>
  `
})
