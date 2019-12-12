
# # example
# # тут хранится инфа о товаре
# # ключ - код товара
# # значение - массив инфы о товаре
# #  "ключ"     "код товара"  "название"         "цена"  "тип"
# #  '2227302': ['2227302', 'Каша овсяная 300г',  45,    'кг\шт\etc']
prod_codes = {}


# # в основном тут будут баркоды и относящаяся
# # информация к этому баркоду:
# # - код товара,
# # - ratio - что-то вроде количества(в коробке, например),
# # - qty - количество в штуках или в весовых единицах(граммах)
# # {'barcode': ['code', 'ratio', 'qty']}
barcodes = {}


class AppliedBarcodes():
    def __init__(self):
        self.applied_barcodes_map = {}

    def add_barcode(self, bk, qty):
        _qty = self.applied_barcodes_map.get(bk)

        if _qty:
            self.applied_barcodes_map[bk] += _qty
            print(f' ---> increment {bk} to {qty} quantity')
        else:
            self.applied_barcodes_map[bk] = qty
            print(f' ---> inserted barcode: {bk} and quantity: {qty}')

    def remove_barcode(self, bk, qty):
        _qty = self.applied_barcodes_map[bk]

        if _qty - qty <= 0:
            del self.applied_barcodes_map[bk]
            print(f' ---> deleted barcode: {bk}')
        else:
            self.applied_barcodes_map[bk] -= qty
            print(f' ---> decrement {qty} of barcode: {bk}')

    def get_list_from_applied_barcodes(self):
        return [{k: v} for k, v in self.applied_barcodes_map.items()]
