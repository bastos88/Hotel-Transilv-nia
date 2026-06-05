import sqlite3
import os

DB_PATH = "hotel.db"


def init_db():
    if os.path.exists(DB_PATH):
        print("🗑️ Removendo banco antigo...")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📝 Criando tabelas...")

    # Tabela hotel com cidade adicionada
    cursor.execute(
        "CREATE TABLE hotel (sigla TEXT PRIMARY KEY, designacao TEXT, cidade TEXT)"
    )
    cursor.execute(
        "CREATE TABLE quarto (sigla TEXT, numero INTEGER, num_camas INTEGER, preco REAL, PRIMARY KEY (sigla, numero))"
    )
    cursor.execute("CREATE TABLE cliente (num_cliente INTEGER PRIMARY KEY, nome TEXT)")
    cursor.execute(
        "CREATE TABLE individual (num_cliente INTEGER PRIMARY KEY, NIF INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE organizacoes (num_cliente INTEGER PRIMARY KEY, contato TEXT, NIPC INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE reserva (num_reserva INTEGER PRIMARY KEY, num_cliente INTEGER, dia_entrada DATE, dia_saida DATE)"
    )
    cursor.execute(
        "CREATE TABLE reserva_quarto (num_reserva INTEGER PRIMARY KEY, sigla TEXT, numero INTEGER, camaextra INTEGER, num_pessoas INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE fatura (num_fatura INTEGER PRIMARY KEY, num_reserva INTEGER, data DATE, valor REAL)"
    )

    print("📝 Inserindo dados...")

    # HOTÉIS COM CIDADES
    hoteis = [
        ("SH", "Sheraton", "São Paulo"),
        ("AL", "Alfa", "Lisboa"),
        ("MN", "Mundial", "Porto"),
        ("RM", "Roma", "Rio de Janeiro"),
        ("MJ", "Majestic", "Barcelona"),
        ("LS", "Lisboa Plaza", "Lisboa"),
    ]
    cursor.executemany("INSERT INTO hotel VALUES (?, ?, ?)", hoteis)

    clientes = [
        (1, "Ana"),
        (2, "ISCTE"),
        (3, "Pedro"),
        (4, "ONU"),
        (5, "Luis"),
        (6, "NASA"),
        (7, "Carlos"),
        (8, "CE"),
        (9, "Sofia"),
        (10, "TAP"),
        (11, "Luisa"),
        (12, "Antonio"),
    ]
    cursor.executemany("INSERT INTO cliente VALUES (?, ?)", clientes)

    organizacoes = [
        (2, None, 1020),
        (4, "Evaristo", 2040),
        (6, None, 1030),
        (8, "Joao", 1120),
        (10, None, 1060),
    ]
    cursor.executemany("INSERT INTO organizacoes VALUES (?, ?, ?)", organizacoes)

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

    # Preços atualizados por cidade
    quartos = [
        # Sheraton - São Paulo (preços mais altos)
        ("SH", 1, 2, 120),
        ("SH", 2, 2, 220),
        ("SH", 3, 4, 450),
        ("SH", 4, 1, 80),
        ("SH", 5, 2, 150),
        ("SH", 6, 3, 180),
        ("SH", 7, 2, 160),
        ("SH", 8, 4, 200),
        ("SH", 9, 1, 90),
        ("SH", 10, 1, 70),
        # Alfa - Lisboa
        ("AL", 1, 2, 100),
        ("AL", 2, 4, 180),
        ("AL", 3, 4, 250),
        ("AL", 4, 2, 110),
        ("AL", 5, 2, 130),
        ("AL", 6, 4, 200),
        ("AL", 7, 2, 140),
        ("AL", 8, 4, 220),
        # Mundial - Porto
        ("MN", 1, 2, 95),
        ("MN", 2, 2, 160),
        ("MN", 3, 4, 280),
        ("MN", 4, 1, 75),
        ("MN", 5, 3, 140),
        ("MN", 6, 4, 190),
        ("MN", 7, 2, 130),
        ("MN", 8, 4, 210),
        ("MN", 9, 1, 80),
        ("MN", 10, 2, 110),
        # Roma - Rio de Janeiro
        ("RM", 1, 2, 110),
        ("RM", 2, 3, 190),
        ("RM", 3, 4, 280),
        ("RM", 4, 1, 85),
        ("RM", 5, 2, 140),
        ("RM", 6, 2, 160),
        ("RM", 7, 2, 135),
        ("RM", 8, 4, 230),
        ("RM", 9, 1, 80),
        ("RM", 10, 4, 200),
        # Majestic - Barcelona
        ("MJ", 1, 2, 140),
        ("MJ", 2, 3, 210),
        ("MJ", 3, 4, 320),
        ("MJ", 4, 1, 95),
        ("MJ", 5, 2, 155),
        ("MJ", 6, 3, 200),
        # Lisboa Plaza - Lisboa
        ("LS", 1, 2, 125),
        ("LS", 2, 2, 195),
        ("LS", 3, 3, 300),
        ("LS", 4, 1, 85),
        ("LS", 5, 1, 145),
        ("LS", 6, 4, 280),
    ]
    cursor.executemany("INSERT INTO quarto VALUES (?, ?, ?, ?)", quartos)

    # Resto dos dados permanece igual
    reservas = []
    for i in range(1, 15):
        reservas.append((i, 4, None, None))
    reservas += [(15, 5, None, None), (16, 5, None, None), (17, 5, None, None)]
    reservas += [
        (18, 8, None, None),
        (19, 8, None, None),
        (20, 9, None, None),
        (21, 9, None, None),
    ]
    reservas += [
        (22, 10, None, None),
        (23, 10, None, None),
        (24, 11, None, None),
        (25, 11, None, None),
    ]
    reservas += [
        (26, 11, None, None),
        (27, 12, None, None),
        (28, 12, None, None),
        (29, 12, None, None),
    ]
    cursor.executemany("INSERT INTO reserva VALUES (?, ?, ?, ?)", reservas)

    reserva_quartos = [
        (1, "SH", 1, None, 1),
        (1, "SH", 3, None, 1),
        (2, "AL", 4, None, 1),
        (2, "AL", 6, None, 2),
        (3, "AL", 1, None, 1),
        (4, "AL", 2, None, 2),
        (5, "AL", 7, None, 1),
        (6, "AL", 8, None, 1),
        (7, "MN", 1, None, 1),
        (8, "MN", 2, None, 1),
        (9, "MN", 7, None, 1),
        (10, "LS", 6, None, 2),
        (11, "MN", 3, None, 1),
        (12, "RM", 1, None, 1),
        (13, "MJ", 2, None, 2),
        (14, "RM", 3, None, 1),
        (15, "RM", 4, None, 1),
        (16, "RM", 5, None, 2),
        (17, "RM", 7, None, 1),
        (18, "RM", 8, None, 3),
        (19, "RM", 9, None, 1),
        (20, "RM", 10, None, 1),
        (21, "MJ", 1, None, 1),
        (22, "MJ", 2, None, 1),
        (23, "MJ", 3, None, 2),
        (24, "MJ", 4, None, 1),
        (25, "LS", 1, None, 1),
        (26, "LS", 2, None, 1),
        (27, "LS", 3, None, 3),
        (28, "LS", 4, None, 2),
        (29, "LS", 5, None, 1),
        (29, "LS", 6, None, 1),
    ]
    cursor.executemany(
        "INSERT INTO reserva_quarto VALUES (?, ?, ?, ?, ?)", reserva_quartos
    )

    faturas = [
        (1, 1, None, 100),
        (2, 3, None, 120),
        (3, 5, None, 100),
        (4, 6, None, 120),
        (5, 8, None, 112),
        (6, 10, None, 70),
        (7, 12, None, 80),
        (8, 13, None, 90),
        (9, 14, None, 112),
        (10, 16, None, 124),
        (11, 17, None, 102),
        (12, 20, None, 70),
        (13, 21, None, 12),
        (14, 25, None, 120),
        (15, 27, None, 100),
        (16, 29, None, 80),
    ]
    cursor.executemany("INSERT INTO fatura VALUES (?, ?, ?, ?)", faturas)

    conn.commit()
    conn.close()

    print("✅ Banco de dados criado com sucesso!")
    print("\n📍 Hotéis com cidades:")
    for sigla, nome, cidade in hoteis:
        print(f"   - {nome} ({cidade})")


if __name__ == "__main__":
    init_db()
