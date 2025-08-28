const mapObject = obj => {
  // obj.date = Quasar.date.formatDate(new Date(obj.time), 'YYYY-MM-DD HH:mm')
  // here you can do something with the mapped data
  return obj
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  // Declare models/variables
  data() {
    return {
      currencyOptions: [],
      inventories: [],
      inventoryDialog: {
        show: false,
        data: {}
      }
    }
  },
  // Where functions live
  methods: {
    showInventoryDialog() {
      this.inventoryDialog.show = true
      this.inventoryDialog.data.is_tax_inclusive =
        this.inventoryDialog.data.is_tax_inclusive ?? true
    },
    closeInventoryDialog() {
      this.inventoryDialog.show = false
      this.inventoryDialog.data = {}
    },
    createOrUpdateDisabled() {
      if (!this.inventoryDialog.show) return true
      const data = this.inventoryDialog.data
      return !data.name || !data.currency
    },
    async getInventories() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          '/inventory/api/v1/inventories?all_wallets=true',
          this.g.user.wallets[0].inkey
        )
        this.inventories = [...data]
        console.log('Fetched inventories:', this.inventories)
      } catch (error) {
        console.error('Error fetching inventories:', error)
        LNbits.utils.notifyError(error)
      }
    },
    submitInventoryData() {
      if (this.inventoryDialog.data.id) {
        this.updateInventory(this.inventoryDialog.data)
      } else {
        this.createInventory(this.inventoryDialog.data)
      }
    },
    async createInventory(data) {
      try {
        const payload = {...data}
        const {data: createdInventory} = await LNbits.api.request(
          'POST',
          '/inventory/api/v1/inventories',
          null,
          payload
        )
        this.inventories.push(mapObject(createdInventory))
      } catch (error) {
        console.error('Error creating inventory:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeInventoryDialog()
      }
    },
    async updateInventory(data) {
      try {
        const {data: updatedInventory} = await LNbits.api.request(
          'PUT',
          `/inventory/api/v1/inventories/${data.id}`,
          null,
          data
        )
        const index = this.inventories.findIndex(
          inv => inv.id === updatedInventory.id
        )
        if (index !== -1) {
          this.inventories.splice(index, 1, mapObject(updatedInventory))
        }
      } catch (error) {
        console.error('Error updating inventory:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeInventoryDialog()
      }
    }
  },
  // To run on startup
  async created() {
    await this.getInventories()
    await LNbits.api
      .request('GET', '/api/v1/currencies')
      .then(({data}) => {
        this.currencyOptions = ['sats', ...data]
      })
      .catch(error => {
        console.error('Error fetching currencies:', error)
        LNbits.utils.notifyError(error)
      })
  }
})
