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
        if (not (re.match(padrao, matricula))):
            limpar_tela()
            print("Formato inválido! Tente novamente.")
            continue
        
        # Verificar se veículo já está estacionado
        cursor.execute("""
            SELECT 1 FROM viaturas_entrada 
            INNER JOIN vaga ON viaturas_entrada.lugar_id = vaga.id 
            WHERE matricula = ? AND ocupado = 1
        """, (matricula,))
        if cursor.fetchone():
            limpar_tela()
            print("Este veículo já está registrado como estacionado.")
            return Menu_Principal()

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
                print("\n Erro ao registrar o carro. Tente novamente.")
                return Menu_Principal()

#Registrar saída do veículo:

def registrar_Saida():
    limpar_tela()
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
        return Menu_Principal()
    else:
        print("Matrícula não encontrada.\n")
        return Menu_Principal()

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

#CONSULTAR VAGAS DISPONIVEIS
def Consultar_Vaga_Especifica():
    limpar_tela()
    cod_vaga = input("Digite o código da vaga que deseja consultar (ex: A1, B2): ").strip().upper()

    # Verifica se a vaga existe e está ocupada
    cursor.execute("SELECT id, ocupado FROM vaga WHERE codigo = ?", (cod_vaga,))
    resultado = cursor.fetchone()

    if not resultado:
        print("Vaga não encontrada.\n")
    else:
        vaga_id, ocupado = resultado
        if ocupado == 0:
            print(f"A vaga {cod_vaga} está livre.\n")
        else:
            cursor.execute("""
                SELECT matricula, entrada FROM viaturas_entrada
                WHERE lugar_id = ? ORDER BY entrada DESC LIMIT 1
            """, (vaga_id,))
            carro = cursor.fetchone()
            print(f"A vaga {cod_vaga} está ocupada pelo carro com matrícula: {carro[0]}")
            print(f"Horário de entrada: {carro[1]}\n")
    
    input("Pressione Enter para voltar ao menu...")
    return Menu_Principal()

# FUNÇÃO ADMINISTRADOR

def InserirVaga():
    user = input("Digite seu usuário: ")
    password = input("Digite sua senha: ")
    
    if (user == "Dario" and password == "1234"):
        print("Login como administrador bem-sucedido.\n")
        while True:
            vaga = input("Insira o código da nova vaga: ")
            try:
                cursor.execute("INSERT INTO vaga (codigo) VALUES (?)", (vaga,))
                conexao.commit()
                print("Vaga inserida com sucesso.\n")
            except sqlite3.IntegrityError:
                print("Código de vaga já existe! Tente outro.\n")

            if input("Deseja sair? (S/N): ").upper() == "S":
                limpar_tela()
                return Menu_Principal()
    else:
        limpar_tela()
        print("Usuário ou senha incorretos.\n")
        return InserirVaga()

#MENU PRINCIPAL DO SISTEMA

def Menu_Principal():
   while True: 
    print("\n\t SISTEMA DE GESTÃO DE PARQUE")
    print("\n============== MENU PRINCIPAL ==============")
    print("|    1 - Registrar entrada de veículo      |")
    print("|    2 - Registrar saída de veículo        |")
    print("|    3 - Consultar vagas disponíveis       |")
    print("|    4 - Mostrar viaturas estacionadas     |")
    print("|    5 - Consultar vaga por código        |")
    print("|    6 - Admin (Adicionar vagas)           |")
    print("|    7 - Sair do programa                  |")
    print("============================================")
    
    try:
        escolha = int(input("Escolha uma opção: "))
    except ValueError:
        limpar_tela()
        print("Opção inválida. Digite um número para Representar uma das opções!\n.")
        continue
    
    if escolha == 1:
        limpar_tela()
        Registrar_Veiculo()
    elif escolha == 2:
        limpar_tela()
        registrar_Saida()
    elif escolha == 3:
        limpar_tela()
        Listar_Vagas()
        return Menu_Principal()
    elif escolha == 4:
        limpar_tela()
        Mostrar_Viaturas_Estacionadas()
        return Menu_Principal()
    elif escolha == 5:
        limpar_tela()
        Consultar_Vaga_Especifica()
    elif escolha == 6:
        limpar_tela()
        InserirVaga()
    elif escolha == 7:
        limpar_tela()
        print("Obrigado por utilizar o sistema! Até logo.")
        conexao.close()
        break
    else:
        limpar_tela()
        print("Opção inválida. Tente novamente.")


# Criação das tabelas (apenas na primeira execução)
criar_tabelas_com_lugares()

# Iniciar o programa
Menu_Principal()
