#!/usr/bin/env python3
"""
Script para gerenciar usuários no banco de dados.
Uso:
python manage_users.py add <login> <senha> [email]
python manage_users.py list
python manage_users.py delete <login>
python manage_users.py update <login> <nova_senha>
"""

import sys
from auth import create_user, list_users, delete_user, update_user_password

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == 'add':
        if len(sys.argv) < 4:
            print("Uso: python add_user.py add <login> <senha> [email]")
            return
        login = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
        if create_user(login, password, email):
            print(f"Usuário {login} criado com sucesso.")
        else:
            print(f"Usuário {login} já existe.")

    elif command == 'list':
        users = list_users()
        print("Usuários:")
        for user in users:
            print(f"- {user['login']} (criado em {user['created_at']})")

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Uso: python add_user.py delete <login>")
            return
        login = sys.argv[2]
        delete_user(login)
        print(f"Usuário {login} deletado.")

    elif command == 'update':
        if len(sys.argv) < 4:
            print("Uso: python add_user.py update <login> <nova_senha>")
            return
        login = sys.argv[2]
        new_password = sys.argv[3]
        update_user_password(login, new_password)
        print(f"Senha de {login} atualizada.")

    else:
        print("Comando desconhecido.")
        print(__doc__)

if __name__ == '__main__':
    main()