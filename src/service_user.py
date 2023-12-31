import os
from dotenv import load_dotenv
import src.services as services
import src.view as view
import src.admin as admin
from fuzzywuzzy import fuzz

load_dotenv()
db_user = os.getenv('DB_USER')
data_db_user = services.get(db_user)

global tmp_user
tmp_user = {}


def data_users():
    return data_db_user


def login(username, password):
    for user in data_users():
        if username == user['username']:
            if password == user['password']:
                return user
            else:
                return 'password salah'
    return 'user tidak ditemukan'


def back_to_menu(key):
    if key == '0':
        admin.main()


# LIST USER
def list_user(data=data_users(), isBack=False, isPwd=False):
    view.text_in_line(liner='-')
    if isPwd:
        print(f"   {'No.':<5}{'Username':<15}{'Password':<15}{'Role':<15}")
    else:
        print(f"   {'No.':<5}{'Username':<15}{'Role':<15}")
    view.text_in_line(liner='-')
    for i, user in enumerate(data):
        if isPwd:
            print(
                f"   {str(i+1)+'.':<5}{user['username']:<15}{user['password']:<15}{user['role']:<15}")
        else:
            print(
                f"   {str(i+1)+'.':<5}{user['username']:<15}{user['role']:<15}")
    view.text_in_line(liner='-')
    print()
    if isBack:
        input('Enter untuk kembali ke Menu')
        admin.main()


# ADD USER
def add_user(isBack=False):
    admin.header('Tambah User', 'Menu')
    view.text_in_line(liner='-')

    if isBack:
        print(f"   {'Username':<9} : "+tmp_user['username'])
        print(f"   {'Password':<9} : "+tmp_user['password'])
        tmp_user['role'] = input(
            f"   {'Role [A]->(Admin), [K]->(Kasir)':<9} : ").upper()
        back_to_menu(tmp_user['role'])
    else:
        tmp_user['username'] = input(f"   {'Username':<9} : ")
        back_to_menu(tmp_user['username'])

        for item in data_users():
            if item['username'] == tmp_user['username']:
                print()
                view.text_in_line(
                    f"Username '{item['username']}' telah terpakai", color='red')
                print()
                input()
                add_user()

        tmp_user['password'] = input(f"   {'Password':<9} : ")
        back_to_menu(tmp_user['password'])

        tmp_user['role'] = input(
            f"   {'Role [A]->(Admin), [K]->(Kasir)':<9} : ").upper()
        back_to_menu(tmp_user['role'])

    if not tmp_user['role'].isalpha() or (tmp_user['role'] != 'A' and tmp_user['role'] != 'K'):
        print()
        view.text_in_line('Inputkan huruf A atau K', color='red')
        input()
        add_user(True)
    else:
        if tmp_user['role'] == 'A':
            tmp_user['role'] = 'admin'
        else:
            tmp_user['role'] = 'kasir'

        data = data_users()
        data.append(tmp_user)
        result = services.post(db_user, data)

        print()
        view.text_in_line(
            f"User '{result['username']}' berhasil ditambahkan sebagai '{result['role']}", color='green')
        print()
        input('Enter untuk kembali ke Menu')
        data_users()
        admin.main()


def input_update_user(data, isRecall=False, user={}):
    tmp_user = data
    admin.header('Update User', 'Menu')
    list_user([data], False, True)
    print()

    if isRecall and user.__len__() > 0:
        print(f'   Username baru : {user["username"]}')
    else:
        username = input('   Username baru : ')
        if username.__len__() < 3:
            print()
            view.text_in_line('Username minimal 3 Karakter', color='red')
            print()
            input('Enter untuk lanjut')
            input_update_user(data)
        else:
            user['username'] = username

    if isRecall and user.__len__() > 1:
        print(f"   Password baru : {user['password']}")
    else:
        password = input('   Password baru : ')
        if password.__len__() < 3:
            print()
            view.text_in_line('Password minimal 3 karakter', color='red')
            print()
            input('Enter untuk lanjut')
            input_update_user(data, True, user)
        else:
            user['password'] = password

    role = input('   Role [A -> Admin, K -> Kasir] : ').upper()
    if not role.isalpha() and role.__len__ != 1 and (role != 'A' or role != 'B'):
        print()
        view.text_in_line('Inputkan A atau K')
        print()
        input('Enter untuk lanjut')
        input_update_user(data, True, user)
    else:
        if role == 'A':
            role = 'admin'
        else:
            role = 'kasir'
        user['role'] = role

    get_data_users = data_users()

    for index, item in enumerate(get_data_users):
        if item['username'] == data['username'] and item['password'] == data['password']:
            get_data_users[index] = user

    result = services.post(db_user, get_data_users)

    print()
    view.text_in_line(
        f'User {tmp_user["username"]} berhasil diubah', color='green')
    print()
    input('Enter untuk lanjut')
    admin.main()


# UPDATE USER
def update_user(data=data_users(), isRecall=False):
    ratio = 80
    user_selected = []
    key = ''

    admin.header('Update User', 'Menu')
    list_user(data)

    if isRecall:
        key = input('   Pilih User [No] : ')
        back_to_menu(key)

        if not key.isnumeric():
            print()
            view.text_in_line(
                f'Input hanya dari No 1 sampai {data.__len__()}', color='red')
            print()
            input('Enter untuk lanjut')
    else:
        key = input('   Pilih User [No/Username] : ').lower()
        back_to_menu(key)

    if key.__len__() == 0:
        update_user()
    elif key.isnumeric():
        key = int(key) - 1
        if key > data.__len__():
            print()
            view.text_in_line(
                f'Input No hanya dari 1 sampai {data.__len__()}', color='red')
            print()
            input('Enter untuk lanjut')
            update_user()
        else:
            user_selected.append(data[key])
    else:
        for user in data:
            if fuzz.partial_ratio(key, user['username']) >= ratio:
                user_selected.append(user)

    if user_selected.__len__() < 1:
        print()
        view.text_in_line(f'Username tidak ditemukan', color='red')
        print()
        input('Enter untuk lanjut')
        update_user()
    elif user_selected.__len__() == 1:
        tmp_user = user_selected[0]
    else:
        update_user(user_selected, True)

    print()
    input_update_user(tmp_user)


# DELETE USER
def delete_user(data=data_users(), isRecall=False):
    user_selected = []
    ratio = 80
    index = 0
    key = ''

    admin.header('Delete User', 'Menu')

    list_user(data)

    if isRecall:
        key = input('   Pilih User [No] : ')
        if not key.isnumeric():
            print()
            view.text_in_line(
                f'Pilih hanya No 1 sampai {data.__len__()}', color='red')
            print()
            input('Enter untuk lanjut')
            delete_user(data)
    else:
        key = input('   Pilih User [No/Username] : ')
    back_to_menu(key)

    if key.__len__() == 0:
        delete_user()
    elif key.isnumeric() and key.__len__() < 3:
        deleting_user(data[int(key)-1])
    else:
        for i, user in enumerate(data):
            if fuzz.partial_ratio(key, user['username']) >= ratio:
                index = i
                user_selected.append(user)

        if user_selected.__len__() == 0:
            print()
            view.text_in_line('User tidak ditemukan', color='red')
            print()
            input('Enter untuk lanjut')
            delete_user()
        elif user_selected.__len__() > 1:
            print()
            view.text_in_line('Ditemukan lebih dari 1 user', color='green')
            print()
            input('Enter untuk lanjut')
            delete_user(user_selected, True)
        else:
            deleting_user(user_selected[0])


def deleting_user(data):
    tmp_user = data
    get_data_users = data_users()

    admin.header('Delete User', 'Menu')
    list_user([data], False, True)
    konfirm = input('   Anda yakin? [Y/N] : ').upper()

    if konfirm != 'Y' and konfirm != 'N':
        print()
        view.text_in_line('Inputkan Y atau N')
        print()
        input('Enter untuk lanjut')

    if konfirm == 'Y':
        for index, user in enumerate(get_data_users):
            if data == user:
                del get_data_users[index]
        services.post(db_user, get_data_users)
        print()
        view.text_in_line(
            f"User '{tmp_user['username']}' berhasil dihapus", color='green')
        print()
        input('Enter untuk lanjut')
        delete_user()

    if konfirm == 'N':
        delete_user()
