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
      managers: [],
      items: [],
      inventoryDialog: {
        show: false,
        data: {}
      },
      managerDialog: {
        show: false,
        data: {}
      },
      openInventory: null,
      openInventoryCurrency: null,
      itemDialog: {
        show: false,
        data: {}
      },
      itemsTable: {
        columns: [
          {
            name: 'is_active',
            align: 'left',
            label: '',
            field: 'is_active',
            sortable: false,
            format: (_, row) => (row.is_active === true ? '🟢' : '⚪')
          },
          {
            name: 'name',
            align: 'left',
            label: 'Name',
            field: 'name',
            sortable: true
          },
          {
            name: 'description',
            align: 'left',
            label: 'Description',
            field: 'description',
            sortable: false,
            format: val => (val || '').substring(0, 50)
          },
          {
            name: 'price',
            align: 'left',
            label: 'Price',
            field: 'price',
            sortable: true,
            format: (_, row) =>
              LNbits.utils.formatCurrency(row.price, this.openInventoryCurrency)
          },
          {
            name: 'discount',
            align: 'left',
            label: 'Discount',
            field: 'discount_percentage',
            sortable: true,
            format: val => (val ? `${val}%` : '')
          },
          {
            name: 'quantity_in_stock',
            align: 'left',
            label: 'Quantity',
            field: 'quantity_in_stock',
            sortable: true
          },
          {
            name: 'categories',
            align: 'left',
            label: 'Categories',
            field: 'categories',
            sortable: true,
            format: val => (val ? val.toString() : '')
          },
          {
            name: 'created_at',
            align: 'left',
            label: 'Created At',
            field: 'created_at',
            format: val => LNbits.utils.formatDateString(val),
            sortable: true
          },
          {
            name: 'id',
            align: 'left',
            label: 'ID',
            field: 'id',
            sortable: true
          }
        ],
        pagination: {
          rowsPerPage: 10,
          page: 1,
          rowsNumber: 10
        },
        search: ''
      },
      loadingItems: false,
      categories: []
    }
  },
  watch: {
    'itemsTable.search': {
      handler() {
        this.getItemsPaginated()
      }
    }
  },
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
    closeManagerDialog() {
      this.managerDialog.show = false
      this.managerDialog.data = {}
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
          '/inventory/api/v1/inventories'
        )
        console.log('Fetched inventories:', data)
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
    },
    async setOpenInventory(id) {
      console.log('Fetching items for inventory:', id)
      this.openInventory = id
      this.openInventoryCurrency =
        this.inventories.find(inv => inv.id === id)?.currency || null
      this.categories = []
      console.log('Open inventory currency:', this.openInventoryCurrency)
      await this.getItemsPaginated()
      await this.getCategories()
      await this.getManagers()
    },
    async getItemsPaginated(props) {
      this.loadingItems = true
      try {
        const params = LNbits.utils.prepareFilterQuery(this.itemsTable, props)
        const {data} = await LNbits.api.request(
          'GET',
          `/inventory/api/v1/items/${this.openInventory}/paginated?${params}`
        )
        console.log('Received data:', data)
        this.items = [...data.data]
        this.itemsTable.pagination.rowsNumber = data.total
        // console.log('Fetched items:', this.items)
      } catch (error) {
        console.error('Error fetching items:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.loadingItems = false
      }
    },
    async getCategories() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          `/inventory/api/v1/categories/${this.openInventory}`
        )
        console.log('Fetched categories:', data)
        this.categories = [...data]
      } catch (error) {
        console.error('Error fetching categories:', error)
        LNbits.utils.notifyError(error)
      }
    },
    createNewCategory(val, done) {
      if (val.length === 0) return
    },
    async addItem() {
      this.itemDialog.data.inventory_id = this.openInventory
      try {
        const {data} = await LNbits.api.request(
          'POST',
          `/inventory/api/v1/items`,
          null,
          this.itemDialog.data
        )
        console.log('Item added:', data)
        this.items = [...this.items, data]
      } catch (error) {
        console.error('Error adding item:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.itemDialog.show = false
        this.itemDialog.data = {}
      }
    },
    async getManagers() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          `/inventory/api/v1/managers/${this.openInventory}`
        )
        this.managers = [...data]
      } catch (error) {
        console.error('Error fetching managers:', error)
        LNbits.utils.notifyError(error)
      }
    },
    submitManagerData() { 
      const inventoryId = this.openInventory
      if (!inventoryId) {
        LNbits.utils.notifyError('No inventory selected')
        return
      }
      this.managerDialog.data.inventory_id = inventoryId
      if (this.managerDialog.data.id) {
        this.updateManager(this.managerDialog.data)
      } else {
        this.createManager(this.managerDialog.data)
      }      
    },
    async createManager(data) {
      try {
        const payload = {...data}
        const {data: createdManager} = await LNbits.api.request(
          'POST',
          `/inventory/api/v1/managers/${this.openInventory}`,
          null,
          payload
        )
        this.managers.push(mapObject(createdManager))
      } catch (error) {
        console.error('Error creating manager:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeManagerDialog()
      }
    },
    async updateManager(data) {
      try {
        const {data: updatedManager} = await LNbits.api.request(
          'PUT',
          `/inventory/api/v1/managers/${data.id}`,
          null,
          payload
        )
        this.managers = this.managers.map(manager =>
          manager.id === updatedManager.id ? mapObject(updatedManager) : manager
        )
      } catch (error) {
        console.error('Error updating manager:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeManagerDialog()
      }
    },
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
