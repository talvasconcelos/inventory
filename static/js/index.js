const mapObject = obj => {
  obj.price = Number(obj.price.toFixed(2))
  if (obj.discount_percentage) {
    obj.discount_percentage = Number(obj.discount_percentage.toFixed(2))
  }
  if (obj.discount_percentage) {
    obj.discount_percentage = Number(obj.discount_percentage.toFixed(2))
  }
  if (obj.unit_cost) {
    obj.unit_cost = Number(obj.unit_cost.toFixed(2))
  }
  if (obj.tax_rate) {
    obj.tax_rate = Number(obj.tax_rate.toFixed(2))
  }
  return obj
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  // Declare models/variables
  data() {
    return {
      tab: 'items',
      tabOptions: [
        {label: 'Items', value: 'items'},
        {label: 'Managers', value: 'managers'},
        {label: 'Services', value: 'services'},
        {label: 'Orders', value: 'orders'}
      ],
      currencyOptions: [],
      inventory: null,
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
            name: 'tags',
            align: 'left',
            label: 'Tags',
            field: 'tags',
            sortable: true,
            format: val => (val ? val.toString() : '')
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
          rowsPerPage: 5,
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
      if (this.inventory) {
        this.inventoryDialog.data = {...this.inventory}
        return
      }
      this.inventoryDialog.data = {}
      this.inventoryDialog.data.is_tax_inclusive = true
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
        this.inventory = {...data} // Change to single inventory
        this.openInventory = this.inventory.id
        this.openInventoryCurrency = this.inventory.currency
        await this.getItemsPaginated()
        await this.getCategories()
        await this.getManagers()
        console.log('Fetched inventory:', this.inventory)
      } catch (error) {
        console.error('Error fetching inventory:', error)
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
        this.inventory = {...createdInventory}
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
        this.inventory = {...updatedInventory}
      } catch (error) {
        console.error('Error updating inventory:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeInventoryDialog()
      }
    },
    async deleteInventory(id) {
      this.$q
        .dialog({
          title: 'Confirm Deletion',
          message: 'Are you sure you want to delete this inventory?',
          cancel: true,
          persistent: true
        })
        .onOk(async () => {
          try {
            await LNbits.api.request(
              'DELETE',
              `/inventory/api/v1/inventories/${id}`
            )
            this.inventory = null
            this.openInventory = null
            this.items = []
          } catch (error) {
            console.error('Error deleting inventory:', error)
            LNbits.utils.notifyError(error)
          }
        })
    },
    // DELETE THIS METHOD IF SINGLE INVENTORY
    // async setOpenInventory(id) {
    //   console.log('Fetching items for inventory:', id)
    //   this.openInventory = id
    //   this.openInventoryCurrency =
    //     this.inventories.find(inv => inv.id === id)?.currency || null
    //   this.categories = []
    //   console.log('Open inventory currency:', this.openInventoryCurrency)
    //   await this.getItemsPaginated()
    //   await this.getCategories()
    //   await this.getManagers()
    // },
    async getItemsPaginated(props) {
      console.log('Getting paginated items with props:', props)
      this.loadingItems = true
      try {
        const params = LNbits.utils.prepareFilterQuery(this.itemsTable, props)
        console.log('Constructed query params:', params)
        const {data} = await LNbits.api.request(
          'GET',
          `/inventory/api/v1/items/${this.openInventory}/paginated?${params}`
        )
        console.log('Fetched paginated items:', data)
        this.items = [...data.data]
        this.itemsTable.pagination.rowsNumber = data.total
        this.itemsTable.pagination.page =
          data.total > 0
            ? Math.ceil(data.total / this.itemsTable.pagination.rowsPerPage)
            : 1
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
    showItemDialog(id) {
      this.itemDialog.show = true
      if (id) {
        const item = this.items.find(it => it.id === id)
        this.itemDialog.data = {...item}
        return
      }
      this.itemDialog.data = {}
    },
    closeItemDialog() {
      this.itemDialog.show = false
      this.itemDialog.data = {}
    },
    submitItemData() {
      if (this.itemDialog.data.id) {
        this.updateItem(this.itemDialog.data)
      } else {
        this.addItem()
      }
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
    async updateItem(data) {
      try {
        const {data: updatedItem} = await LNbits.api.request(
          'PUT',
          `/inventory/api/v1/items/${data.id}`,
          null,
          data
        )
        this.items = this.items.map(item =>
          item.id === updatedItem.id ? mapObject(updatedItem) : item
        )
      } catch (error) {
        console.error('Error updating item:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeItemDialog()
      }
    },
    async deleteItem(id) {
      this.$q
        .dialog({
          title: 'Confirm Deletion',
          message: 'Are you sure you want to delete this item?',
          cancel: true,
          persistent: true
        })
        .onOk(async () => {
          try {
            await LNbits.api.request('DELETE', `/inventory/api/v1/items/${id}`)
            this.items = this.items.filter(item => item.id !== id)
          } catch (error) {
            console.error('Error deleting item:', error)
            LNbits.utils.notifyError(error)
          }
        })
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
        this.managers = [...this.managers, createdManager]
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
          manager.id === updatedManager.id ? updatedManager : manager
        )
      } catch (error) {
        console.error('Error updating manager:', error)
        LNbits.utils.notifyError(error)
      } finally {
        this.closeManagerDialog()
      }
    },
    async getManagerItems(managerId) {
      return await this.getItemsPaginated({
        pagination: {...this.itemsTable.pagination},
        filter: {manager_id: managerId}
      })
      // console.log('Fetched items for manager:', managerItems)
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
