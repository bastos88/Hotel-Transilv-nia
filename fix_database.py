# fix_database.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = "hotel.db"

# Apagar banco antigo
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Banco antigo removido")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("📝 Criando tabelas atualizadas...")

# Tabelas com estrutura completa
cursor.execute("""
    CREATE TABLE hotel (
        sigla TEXT PRIMARY KEY, 
        designacao TEXT, 
        cidade TEXT
    )
""")

cursor.execute("""
    CREATE TABLE quarto (
        sigla TEXT, 
        numero INTEGER, 
        num_camas INTEGER, 
        preco REAL, 
        PRIMARY KEY (sigla, numero)
    )
""")

cursor.execute("""
    CREATE TABLE cliente (
        num_cliente INTEGER PRIMARY KEY, 
        nome TEXT, 
        email TEXT, 
        telefone TEXT
    )
""")

cursor.execute("""
    CREATE TABLE individual (
        num_cliente INTEGER PRIMARY KEY, 
        NIF INTEGER
    )
""")

cursor.execute("""
    CREATE TABLE organizacoes (
        num_cliente INTEGER PRIMARY KEY, 
        contato TEXT, 
        NIPC INTEGER
    )
""")

cursor.execute("""
    CREATE TABLE reserva (
        num_reserva INTEGER PRIMARY KEY, 
        num_cliente INTEGER, 
        dia_entrada DATE, 
        dia_saida DATE
    )
""")

cursor.execute("""
    CREATE TABLE reserva_quarto (
        num_reserva INTEGER, 
        sigla TEXT, 
        numero INTEGER, 
        camaextra INTEGER, 
        num_pessoas INTEGER,
        PRIMARY KEY (num_reserva, sigla, numero)
    )
""")

cursor.execute("""
    CREATE TABLE fatura (
        num_fatura INTEGER PRIMARY KEY, 
        num_reserva INTEGER, 
        data DATE, 
        valor REAL
    )
""")

cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nome TEXT,
        email TEXT,
        is_admin INTEGER DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE tentativas_login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        username TEXT,
        tentativas INTEGER DEFAULT 0,
        ultima_tentativa TIMESTAMP,
        bloqueado_ate TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE tokens_recuperacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        token TEXT UNIQUE,
        expira_em TIMESTAMP,
        usado BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    )
""")

print("📝 Inserindo dados...")

# Hotéis com cidades
hoteis = [
    ("SH", "Sheraton", "São Paulo"),
    ("AL", "Alfa", "Lisboa"),
    ("MN", "Mundial", "Porto"),
    ("RM", "Roma", "Rio de Janeiro"),
    ("MJ", "Majestic", "Barcelona"),
    ("LS", "Lisboa Plaza", "Lisboa"),
]
cursor.executemany("INSERT INTO hotel VALUES (?, ?, ?)", hoteis)

# Clientes com email e telefone
clientes = [
    (1, "Ana Silva", "ana@email.com", "912345678"),
    (2, "ISCTE", "iscte@email.com", "923456789"),
    (3, "Pedro Santos", "pedro@email.com", "934567890"),
    (4, "ONU", "onu@email.com", "945678901"),
    (5, "Luis Costa", "luis@email.com", "956789012"),
    (6, "NASA", "nasa@email.com", "967890123"),
    (7, "Carlos Mendes", "carlos@email.com", "978901234"),
    (8, "CE", "ce@email.com", "989012345"),
    (9, "Sofia Ferreira", "sofia@email.com", "990123456"),
    (10, "TAP", "tap@email.com", "901234567"),
    (11, "Luisa Rocha", "luisa@email.com", "912345678"),
    (12, "Antonio Neves", "antonio@email.com", "923456789"),
]
cursor.executemany("INSERT INTO cliente VALUES (?, ?, ?, ?)", clientes)

# Organizações
organizacoes = [
    (2, None, 1020),
    (4, "Evaristo", 2040),
    (6, None, 1030),
    (8, "Joao", 1120),
    (10, None, 1060),
]
cursor.executemany("INSERT INTO organizacoes VALUES (?, ?, ?)", organizacoes)

# Individuais
individuais = [
    (1, 589595),
    (3, 585985),
    (5, 375895),
    (7, 836137),
    (9, 767676),
    (11, None),
    (12, None),
]
cursor.executemany("INSERT INTO individual VALUES (?, ?)", individuais)

# Quartos
quartos = [
    ("SH", 1, 2, 120),
    ("SH", 2, 2, 220),
    ("SH", 3, 4, 450),
    ("SH", 4, 1, 80),
    ("SH", 5, 2, 150),
    ("AL", 1, 2, 100),
    ("AL", 2, 3, 180),
    ("AL", 3, 4, 250),
    ("AL", 4, 2, 110),
    ("AL", 5, 2, 130),
    ("MN", 1, 2, 95),
    ("MN", 2, 2, 160),
    ("MN", 3, 4, 280),
    ("MN", 4, 1, 75),
    ("MN", 5, 3, 140),
    ("RM", 1, 2, 110),
    ("RM", 2, 3, 190),
    ("RM", 3, 4, 280),
    ("RM", 4, 1, 85),
    ("RM", 5, 2, 140),
    ("MJ", 1, 2, 140),
    ("MJ", 2, 3, 210),
    ("MJ", 3, 4, 320),
    ("MJ", 4, 1, 95),
    ("MJ", 5, 2, 155),
    ("LS", 1, 2, 125),
    ("LS", 2, 2, 195),
    ("LS", 3, 3, 300),
    ("LS", 4, 1, 85),
    ("LS", 5, 2, 145),
]
cursor.executemany("INSERT INTO quarto VALUES (?, ?, ?, ?)", quartos)

# Reservas
reservas = [
    (1, 4, "2024-01-10", "2024-01-15"),
    (2, 4, "2024-01-10", "2024-01-15"),
    (3, 5, "2024-01-10", "2024-01-12"),
    (4, 5, "2024-01-15", "2024-01-18"),
    (5, 8, "2024-01-20", "2024-01-25"),
    (6, 9, "2024-01-22", "2024-01-28"),
    (7, 10, "2024-01-25", "2024-01-30"),
    (8, 11, "2024-02-01", "2024-02-05"),
    (9, 12, "2024-02-10", "2024-02-15"),
    (10, 4, "2024-02-20", "2024-02-25"),
]
cursor.executemany("INSERT INTO reserva VALUES (?, ?, ?, ?)", reservas)

# Reserva quartos
reserva_quartos = [
    (1, "SH", 1, None, 2),
    (2, "SH", 3, None, 2),
    (3, "AL", 1, None, 1),
    (4, "AL", 2, None, 2),
    (5, "MN", 1, None, 2),
    (6, "RM", 2, None, 2),
    (7, "MJ", 1, None, 1),
    (8, "LS", 2, None, 2),
    (9, "SH", 4, None, 1),
    (10, "AL", 3, None, 3),
]
cursor.executemany("INSERT INTO reserva_quarto VALUES (?, ?, ?, ?, ?)", reserva_quartos)

# Faturas
faturas = [
    (1, 1, "2024-01-16", 600),
    (2, 2, "2024-01-16", 900),
    (3, 3, "2024-01-13", 200),
    (4, 4, "2024-01-19", 360),
    (5, 5, "2024-01-26", 475),
    (6, 6, "2024-01-29", 560),
    (7, 7, "2024-01-31", 700),
    (8, 8, "2024-02-06", 400),
    (9, 9, "2024-02-16", 600),
    (10, 10, "2024-02-26", 500),
]
cursor.executemany("INSERT INTO fatura VALUES (?, ?, ?, ?)", faturas)

# Usuário admin
senha_hash = generate_password_hash("admin123")
cursor.execute(
    """
    INSERT INTO usuarios (username, password, nome, email, is_admin) 
    VALUES (?, ?, ?, ?, ?)
""",
    ("admin", senha_hash, "Administrador", "admin@hotel.com", 1),
)

conn.commit()
conn.close()

print("✅ Banco de dados recriado com sucesso!")
print("\n📍 Hotéis disponíveis:")
for sigla, nome, cidade in hoteis:
    print(f"   - {nome} ({cidade})")
print("\n🔑 Credenciais admin: admin / admin123")
