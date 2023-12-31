import os
from dotenv import load_dotenv
import src.services as services
import src.view as view
import src.admin as admin
from fuzzywuzzy import fuzz
import src.kasir as kasir
import src.service_transaction as service_transaction

load_dotenv()
db_product = os.getenv('DB_PRODUCT')
data_products = services.get(db_product)

global tmp_product
tmp_product = {}


def get_data_product():
    return data_products


def back_to_menu(key, isKasir=False):
    if key == '0' and not isKasir:
        admin.main()
    if key == '0' and isKasir:
        kasir.main()


# LIST PRODUCT
def list_product(data=get_data_product(), isKasir=False, isSearch=False, isAddTransaction=False, data_user={}):
    if isKasir:
        kasir.header('List Product', 'Menu')
    else:
        admin.header('List Product', 'Menu')

    view.text_in_line(liner='-')
    print(f"   {'No.':<5}{'Nama':<25}{'Harga':<15}{'Stok':<10}")
    view.text_in_line(liner='-')
    for i, product in enumerate(data):
        if (i+1) % 6 == 0:
            print()
        print(
            f"   {str(i+1)+'.':<5}{product['name']:<25}{view.format_rupiah(product['price']):<15}{product['quantity']:<10}")
    view.text_in_line(liner='-')
    print()

    if isAddTransaction and data.__len__() == 1:
        service_transaction.add_transaction(data_user, data[0])

    if isSearch:
        search_product(data, isKasir, isSearch, isAddTransaction, data_user)
    else:
        return


def search_product(data, isKasir, isSearch, isAddTransaction, data_user={}):
    found_products = []
    ratio = 80

    view.text_in_line('Enter untuk refresh produk', align='right')
    key = input('   Cari Product [No/Nama] : ')
    back_to_menu(key, isKasir=isKasir)

    if key.__len__() == 0:
        list_product(get_data_product(), isKasir,
                     isSearch, isAddTransaction, data_user)
    elif key.isnumeric():
        if int(key) > data.__len__():
            print()
            view.text_in_line('Produk tidak ditemukan', color='red')
            print()
            input('Enter untuk lanjut')
            list_product(data, isKasir, isSearch, isAddTransaction, data_user)
        found_products.append(data[int(key)-1])
    else:
        for product in data:
            if fuzz.partial_ratio(product['name'].lower(), key.lower()) >= ratio:
                found_products.append(product)

    if found_products.__len__() == 0:
        print()
        view.text_in_line('Produk tidak ditemukan', color='red')
        print()
        input('Enter untuk lanjut')
        list_product(data, isKasir, isSearch, isAddTransaction, data_user)
    else:
        list_product(found_products, isKasir, isSearch,
                     isAddTransaction, data_user)


# ADD PRODUCT
def add_product(data_recall={}):
    admin.header('Tambah Product', 'Menu')
    view.text_in_line(liner='-')

    if data_recall.__len__() >= 1:
        print(f"   {'Nama Produk':<15} : {data_recall['name']}")
    else:
        name = input(f"   {'Nama Produk':<15} : ")
        back_to_menu(name)
        if name.__len__() == 0:
            add_product()
        elif name.__len__() < 3:
            print()
            view.text_in_line('Nama Produk minimal 3 karakter', color='red')
            print()
            input('Enter untuk lanjut')
            add_product()
        elif name.isnumeric():
            print()
            view.text_in_line('Nama Produk tidak valid', color='red')
            print()
            input('Enter untuk lanjut')
            add_product()
        else:
            tmp_product['name'] = name

    if data_recall.__len__() >= 2:
        print(f"   {'Harga Produk':<15} : {data_recall['price']}")
    else:
        price = input(f"   {'Harga Produk':<15} : ")
        back_to_menu(price)
        if price.__len__() == 0:
            add_product(data_recall=tmp_product)
        elif price.__len__() < 3:
            print()
            view.text_in_line('Harga Produk minimal 3 karakter', color='red')
            print()
            input('Enter untuk lanjut')
            add_product(data_recall=tmp_product)
        elif not price.isnumeric():
            print()
            view.text_in_line('Harga Produk tidak valid', color='red')
            print()
            input('Enter untuk lanjut')
            add_product(data_recall=tmp_product)
        else:
            tmp_product['price'] = price

    quantity = input(f"   {'Stok Produk':<15} : ")
    back_to_menu(quantity)
    if quantity.__len__() == 0:
        add_product(data_recall=tmp_product)
    elif not quantity.isnumeric():
        print()
        view.text_in_line('Stok Produk tidak valid', color='red')
        print()
        input('Enter untuk lanjut')
        add_product(data_recall=tmp_product)
    else:
        tmp_product['quantity'] = quantity

    data = get_data_product()
    data += [tmp_product]

    result = services.post(db_product, data)

    print()
    view.text_in_line(
        f"Produk '{result['name']}' berhasil ditambahkan", color='green')
    print()
    input('Enter untuk lanjut')
    admin.main()


# UPDATE PRODUCT
def update_product(data=get_data_product()):
    found_products = []
    admin.header('Update Produk', 'Menu')
    list_product(data)

    key = input("   Pilih Produk [No/Nama] : ")
    back_to_menu(key)

    if key.__len__() == 0:
        update_product()
    elif key.isnumeric():
        tmp_product = data[int(key)-1]
        list_product([tmp_product])
    elif not key.isnumeric():
        for product in data:
            if fuzz.partial_ratio(key, product['name']) >= 80:
                found_products.append(product)

        if found_products.__len__() < 1:
            print()
            view.text_in_line('Produk tidak ditemukan', color='red')
            print()
            input('Enter untuk lanjut')
        elif found_products.__len__() == 1:
            tmp_product = found_products[0]
            list_product(found_products)
        elif found_products.__len__() > 1:
            print()
            view.text_in_line('Ditemukan lebih dari 1 produk', color='green')
            print()
            input('Enter untuk lanjut')
            list_product(found_products)
            tmp_product = research_products(found_products)

    admin.header('Update Produk', 'Menu')
    list_product([tmp_product])
    product = input_product(data_product=tmp_product)

    all_products = get_data_product()
    for i, item in enumerate(all_products):
        if tmp_product['name'] == item['name'] and tmp_product['price'] == item['price']:
            all_products[i] = product

    services.post(db_product, all_products)

    print()
    view.text_in_line(
        f"Produk '{tmp_product['name']}' berhasil diubah", color='green')
    print()
    input('Enter untuk lanjut')
    update_product()


def input_product(data={}, data_product={}):
    admin.header('Update Produk', 'Menu')
    list_product([data_product])
    if data.__len__() >= 1:
        print(f"   {'Nama produk baru':<17} : {data['name']}")
    else:
        name = input(f"   {'Nama produk baru':<17} : ")
        back_to_menu(name)
        if name.__len__() < 3:
            print()
            view.text_in_line('Nama minimal 3 karakter', color='red')
            print()
            input('Enter untuk lanjut')
            input_product(data_product=data_product)
        elif name.isnumeric():
            print()
            view.text_in_line('Nama tidak valid', color='red')
            print()
            input('Enter untuk lanjut')
            input_product(data_product=data_product)
        else:
            data['name'] = name

    if data.__len__() >= 2:
        print(f"   {'Harga produk baru':<17} : {data['price']}")
    else:
        price = input(f"   {'Harga produk baru':<17} : ")
        back_to_menu(price)
        if price.__len__() < 3:
            print()
            view.text_in_line('Nama minimal 3 karakter', color='red')
            print()
            input('Enter untuk lanjut')
            input_product(data, data_product=data_product)
        elif not price.isnumeric():
            print()
            view.text_in_line('Harga tidak valid', color='red')
            print()
            input('Enter untuk lanjut')
            input_product(data, data_product=data_product)
        else:
            data['price'] = price

    quantity = input(f"   {'Stok produk baru:':<17} : ")
    back_to_menu(quantity)
    if quantity.__len__() == 0:
        input_product(data, data_product=data_product)
    elif not quantity.isnumeric():
        print()
        view.text_in_line('Quantity tidak valid', color='red')
        input()
        print()
        input_product(data, data_product=data_product)
    else:
        data['quantity'] = quantity

    return data


def research_products(data):
    admin.header('Update Product', 'Menu')
    list_product(data)
    key = input("   'Pilih Produk [No] : ")
    back_to_menu(key)
    if key.__len__() == 0:
        research_products(data)
    if not key.isnumeric():
        print()
        view.text_in_line(
            f'Pilih hanya No 1 sampai {data.__len__()}', color='red')
        print()
        input('Enter untuk lanjut')
        research_products(data)
    if key.isnumeric():
        return data[int(key)-1]


# DELETE PRODUCT
def delete_product(data=get_data_product(), isRecall=False):
    selected_products = []
    ratio = 80
    index = 0
    key = ''

    admin.header('Delete Produk', 'Menu')

    list_product(data)

    if isRecall:
        key = input('   Pilih Produk [No] : ')
        if not key.isnumeric():
            print()
            view.text_in_line(
                f'Pilih hanya No 1 sampai {data.__len__()}', color='red')
            print()
            input('Enter untuk lanjut')
            delete_product(data)
    else:
        key = input('   Pilih Produk [No/Name] : ')
    back_to_menu(key)

    if key.__len__() == 0:
        delete_product()
    elif key.isnumeric():
        deleting_product(data[int(key)-1])
    else:
        for product in data:
            if fuzz.partial_ratio(key, product['name']) >= ratio:
                selected_products.append(product)

        if selected_products.__len__() == 0:
            print()
            view.text_in_line('Produk tidak ditemukan', color='red')
            print()
            input('Enter untuk lanjut')
            delete_product()
        elif selected_products.__len__() > 1:
            print()
            view.text_in_line('Ditemukan lebih dari 1 produk', color='green')
            print()
            input('Enter untuk lanjut')
            delete_product(selected_products, True)
        else:
            deleting_product(selected_products[0])


def deleting_product(data):
    tmp_product = data
    all_data_product = get_data_product()

    list_product([data])
    konfirm = input('   Anda yakin? [Y/N] : ').upper()

    if konfirm != 'Y' and konfirm != 'N':
        print()
        view.text_in_line('Inputkan Y atau N')
        print()
        input('Enter untuk lanjut')

    if konfirm == 'Y':
        for index, user in enumerate(all_data_product):
            if data == user:
                del all_data_product[index]

        print()
        view.text_in_line(
            f"Produk '{tmp_product['name']}' berhasil dihapus", color='green')
        print()
        input('Enter untuk lanjut')

        services.post(db_product, all_data_product)
        delete_product()

    if konfirm == 'N':
        delete_product()


def subtract_quantity(subtraction):
    data = services.get(db_product)
    for product in subtraction:
        for i, item in enumerate(data):
            if product['name'] == item['name']:
                data[i]['quantity'] = str(
                    int(item['quantity']) - int(product['quantity'])
                )
                break
    services.post(db_product, data)
