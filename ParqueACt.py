import sqlite3  # Biblioteca para manipular banco de dados SQLite
import re       # Biblioteca para validação de strings via expressões regulares
import os       # Biblioteca para interagir com o sistema operacional (limpeza de terminal)


# Conexão com o banco de dados SQLite (será criado se não existir)
conexao = sqlite3.connect("parque.db")
cursor = conexao.cursor()


#FUNÇÃO PARA LIMPAR TERMINAL

def limpar_tela():

    os.system('cls' if os.name == 'nt' else 'clear')
    
#Cria as tabelas principais do banco de dados.
def criar_tabelas_com_lugares():
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaga (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                ocupado INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viaturas_entrada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lugar_id INTEGER,
                FOREIGN KEY (lugar_id) REFERENCES vaga(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viaturas_saida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                saida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conexao.commit()
    except Exception as e:
        print("Erro ao criar tabelas:", e)

# FUNÇÕES AUXILIARES PARA VAGAS E REGISTROS

#Buscar ID da vaga com base no código:
def Buscar_Id_Vaga(codVaga):
    cursor.execute("SELECT id FROM vaga WHERE codigo = ?", (codVaga,))
    carro = cursor.fetchone()
    if carro:
        return carro[0]
    else:
        limpar_tela()
        print("\n Código do espaço incorreto! Verifique novamente.")
        return False
    
#Inserir dados da viatura ao entrar:
def Inserir_Dados_Bd(matricula, fk):
    cursor.execute("INSERT INTO viaturas_entrada (matricula, lugar_Id) VALUES (?, ?)", (matricula, fk))
    try:
        conexao.commit()
        cursor.execute("UPDATE vaga SET ocupado = 1 WHERE id = ?", (fk,))
        conexao.commit()
        return True
    except:
        return False
    
    
#Inserir registro de saída:
def Inserir_Dados_Bd_Saida(matricula):
    cursor.execute("INSERT INTO viaturas_saida (matricula) VALUES (?)", (matricula,))
    try:
        conexao.commit()
        return True
    except:
        return False

#FUNÇÕES PRINCIPAIS DO SISTEMA

#Registrar entrada do veículo:
def Registrar_Veiculo():
    padrao = r'^[A-Z]{2}-\d{2}-\d{2}-[A-Z]{2}$'
    
    while True:
        matricula = input("Insira a matrícula do carro (ex: LD-12-34-FZ):\n").upper()
        if not re.match(padrao, matricula):
            limpar_tela()
            print("Formato inválido! Tente novamente.")
            continue

        if Listar_Vagas() == 0:
            limpar_tela()
            print("Não há vagas disponíveis.")
            return Menu_Principal()

        cod_Vagas = input("\nDigite o código da vaga desejada: ")
        vaga_id = Buscar_Id_Vaga(cod_Vagas)

        if vaga_id:
            if Inserir_Dados_Bd(matricula, vaga_id):
                limpar_tela()
                print("Carro registrado com sucesso!")
                return Menu_Principal()
            else:
                limpar_tela()
                print("\nErro ao registrar o carro. Tente novamente.")

#Registrar saída do veículo:

def registrar_Saida():
    matricula = input("Informe a matrícula do carro para registrar a saída:\n")
    
    cursor.execute("""
        SELECT vaga.id FROM viaturas_entrada 
        INNER JOIN vaga ON viaturas_entrada.lugar_id = vaga.id 
        WHERE matricula = ? LIMIT 1
    """, (matricula,))
    
    carros = cursor.fetchone()
    
    if carros:
        id_vaga = carros[0]
        cursor.execute("UPDATE vaga SET ocupado = 0 WHERE id = ?", (id_vaga,))
        conexao.commit()
        Inserir_Dados_Bd_Saida(matricula)
        print("Saída registrada com sucesso!\n")
    else:
        print("Matrícula não encontrada.\n")
        Menu_Principal()

#Mostrar viaturas estacionadas:

def Mostrar_Viaturas_Estacionadas():
    cursor.execute("""
        SELECT matricula, entrada, codigo 
        FROM viaturas_entrada 
        INNER JOIN vaga ON viaturas_entrada.lugar_id = vaga.id 
        WHERE ocupado = 1
    """)
    
    carros = cursor.fetchall()
    
    if carros:
        print("Carros estacionados:\n")
        for carro in carros:
            print(f" - Matrícula: {carro[0]} | Entrada: {carro[1]} | Espaço: {carro[2]}")
    else:
        print("Nenhum carro estacionado.")

#Listar vagas disponíveis:
def Listar_Vagas():
    cursor.execute("SELECT codigo FROM vaga WHERE ocupado = 0")
    vagas = cursor.fetchall()
    
    if vagas:
        print("Vagas disponíveis:")
        for vaga in vagas:
            print(f" - {vaga[0]}")
        return 1
    else:
        print("Nenhuma vaga disponível.")
        return 0

# FUNÇÃO ADMINISTRADOR

def InserirVaga():
    user = input("Digite seu usuário: ")
    password = input("Digite sua senha: ")
    
    if user == "Dario" and password == "1234":
        print("Login como administrador bem-sucedido.\n")
        while True:
            vaga = input("Insira o código da nova vaga: ")
            cursor.execute("INSERT INTO vaga (codigo) VALUES (?)", (vaga,))
            conexao.commit()
            print("Vaga inserida com sucesso.\n")

            if input("Deseja sair? (S/N): ").upper() == "S":
                limpar_tela()
                return Menu_Principal()
    else:
        limpar_tela()
        print("Usuário ou senha incorretos.\n")
        InserirVaga()

#MENU PRINCIPAL DO SISTEMA

def Menu_Principal():
    print("\n\t SISTEMA DE GESTÃO DE PARQUE")
    print("\n============== MENU PRINCIPAL ==============")
    print("|    1 - Registrar entrada de veículo      |")
    print("|    2 - Registrar saída de veículo        |")
    print("|    3 - Consultar vagas disponíveis       |")
    print("|    4 - Mostrar viaturas estacionadas     |")
    print("|    5 - Admin (Adicionar vagas)           |")
    print("|    6 - Sair do programa                  |")
    print("============================================")
    
    try:
        escolha = int(input("Escolha uma opção: "))
    except ValueError:
        limpar_tela()
        print("Opção inválida. Digite um número.")
        return Menu_Principal()
    
    if escolha == 1:
        Registrar_Veiculo()
    elif escolha == 2:
        registrar_Saida()
    elif escolha == 3:
        Listar_Vagas()
        return Menu_Principal()
    elif escolha == 4:
        Mostrar_Viaturas_Estacionadas()
        return Menu_Principal()
    elif escolha == 5:
        InserirVaga()
    elif escolha == 6:
        print("Obrigado por utilizar o sistema! Até logo.")
        conexao.close()
    else:
        print("Opção inválida. Tente novamente.")
        Menu_Principal()

# Criação das tabelas (apenas na primeira execução)
criar_tabelas_com_lugares()

# Iniciar o programa
Menu_Principal()


conexao.close()