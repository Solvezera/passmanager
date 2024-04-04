import sqlite3
from cryptography.fernet import Fernet

# Chave para criptografia simétrica
key = b'nNjpIl9Ax2LRtm-p6ryCRZ8lRsL0DtuY0f9JeAe2wG0='  # Esta chave deve ser mantida em segredo

# Inicializar o objeto Fernet com a chave
fernet = Fernet(key)

# Conectar-se ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect('password_manager.db')
cursor = conn.cursor()

# Criar as tabelas 'admin' e 'passwords' se não existirem
cursor.executescript('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY,
        site TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        hint TEXT
    );
''')

# Função para verificar se a senha admin está cadastrada
def verificar_senha_admin():
    cursor.execute('SELECT COUNT(*) FROM admin')
    count = cursor.fetchone()[0]
    return count > 0

# Função para adicionar a senha admin
def adicionar_senha_admin(password):
    # Criptografar a senha admin
    hashed_password = fernet.encrypt(password.encode())
    cursor.execute('INSERT INTO admin (password) VALUES (?)', (hashed_password,))
    conn.commit()
    print('Senha admin adicionada com sucesso!')

# Função para verificar a senha admin
def verificar_admin(password):
    cursor.execute('SELECT password FROM admin')
    hashed_admin_password = cursor.fetchone()
    if hashed_admin_password:
        # Descriptografar a senha admin
        decrypted_password = fernet.decrypt(hashed_admin_password[0])
        return decrypted_password.decode() == password
    else:
        return False

# Função para adicionar uma nova senha
def adicionar_senha():
    site = input("Digite o nome do site: ")
    username = input("Digite o nome de usuário: ")
    password = input("Digite a senha: ")
    hint = input("Digite uma dica para a senha: ")
    # Criptografar a senha
    hashed_password = fernet.encrypt(password.encode())
    cursor.execute('INSERT INTO passwords (site, username, password, hint) VALUES (?, ?, ?, ?)', (site, username, hashed_password, hint))
    conn.commit()
    print('Senha adicionada com sucesso!')

# Função para recuperar uma senha
def recuperar_senha(password_admin):
    if verificar_admin(password_admin):
        site = input("Digite o nome do site: ")
        cursor.execute('SELECT username, password, hint FROM passwords WHERE site = ?', (site,))
        senha = cursor.fetchone()
        if senha:
            username, encrypted_password, hint = senha
            # Descriptografar a senha
            decrypted_password = fernet.decrypt(encrypted_password)
            password_hash = decrypted_password.decode()
            print("Senha Recuperada:")
            print("| {:<20} | {:<30} | {:<30} |".format("Nome de Usuário", "Senha Descriptografada", "Dica de Senha"))
            print("-" * 90)
            print("| {:<20} | {:<30} | {:<30} |".format(username, password_hash, hint))
        else:
            print("Senha não encontrada.")
    else:
        print("Senha admin incorreta.")
        
# Função para listar todas as senhas
def listar_senhas(password_admin):
    if verificar_admin(password_admin):
        cursor.execute('SELECT site, username, password, hint FROM passwords')
        senhas = cursor.fetchall()
        if senhas:
            print("Senhas Cadastradas:")
            print("| {:<30} | {:<20} | {:<30} | {:<30} |".format("Site", "Usuário", "Senha Descriptografada", "Dica"))
            print("-" * 123)
            for senha in senhas:
                site, username, encrypted_password, hint = senha
                # Descriptografar a senha
                decrypted_password = fernet.decrypt(encrypted_password)
                password = decrypted_password.decode()
                print("| {:<30} | {:<20} | {:<30} | {:<30} |".format(site, username, password, hint))
        else:
            print("Nenhuma senha cadastrada.")
    else:
        print("Senha admin incorreta.")


# Função para excluir uma senha
def excluir_senha(password_admin):
    if verificar_admin(password_admin):
        site = input("Digite o nome do site: ")
        cursor.execute('DELETE FROM passwords WHERE site = ?', (site,))
        conn.commit()
        print('Senha excluída com sucesso!')
    else:
        print("Senha admin incorreta.")

# Função principal
def main():
    # Verificar se a senha admin está cadastrada
    if not verificar_senha_admin():
        print("Senha admin não cadastrada. Por favor, faça o primeiro cadastro.")
        adicionar_senha_admin(input("Digite a senha admin: "))
    else:
        while True:
            password = input("Digite a senha admin: ")
            if verificar_admin(password):
                break
            else:
                print("Senha admin incorreta. Tente novamente.")

    print("Bem-vindo ao Password Manager!")
    while True:
        print("\nMenu:")
        print("1 - Adicionar nova senha")
        print("2 - Recuperar senha")
        print("3 - Excluir senha")
        print("4 - Listar Senhas")
        print("5 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_senha()
        elif opcao == '2':
            recuperar_senha(input("Digite a senha admin: "))
        elif opcao == '3':
            excluir_senha(input("Digite a senha admin: "))
        elif opcao == '4':
            listar_senhas(input("Digite a senha admin: "))
        elif opcao == '5':
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()

# Fechar conexão com o banco de dados ao final
conn.close()
