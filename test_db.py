from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "hotel.db"


def init_db():
    """Cria o banco de dados do zero"""
    # Deletar banco antigo se existir
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Banco antigo removido")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📝 Criando tabelas...")

    # Criar tabelas
    cursor.execute("""
        CREATE TABLE hotel (
            sigla TEXT PRIMARY KEY,
            designacao TEXT
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
            nome TEXT
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
            num_reserva INTEGER PRIMARY KEY,
            sigla TEXT,
            numero INTEGER,
            camaextra INTEGER,
            num_pessoas INTEGER
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

    print("📝 Inserindo dados...")

    # Inserir hotéis
    hoteis = [
        ("SH", "Sheraton"),
        ("AL", "Alfa"),
        ("MN", "Mundial"),
        ("RM", "Roma"),
        ("MJ", "Majestic"),
        ("LS", "Lisboa"),
    ]
    cursor.executemany("INSERT INTO hotel VALUES (?, ?)", hoteis)

    # Inserir clientes
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

    # Inserir organizações
    organizacoes = [
        (2, None, 1020),
        (4, "Evaristo", 2040),
        (6, None, 1030),
        (8, "Joao", 1120),
        (10, None, 1060),
    ]
    cursor.executemany("INSERT INTO organizacoes VALUES (?, ?, ?)", organizacoes)

    # Inserir individuais
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

    # Inserir quartos
    quartos = [
        ("SH", 1, 2, 10),
        ("SH", 2, 2, 20),
        ("SH", 3, 4, 20),
        ("SH", 4, 1, 10),
        ("SH", 5, 2, None),
        ("SH", 6, 3, 15),
        ("SH", 7, 2, 15),
        ("SH", 8, 4, None),
        ("SH", 9, 1, 10),
        ("SH", 10, 1, 5),
        ("AL", 1, 2, 10),
        ("AL", 2, 4, None),
        ("AL", 3, 4, 20),
        ("AL", 4, 2, 10),
        ("AL", 5, 2, None),
        ("AL", 6, 4, 15),
        ("AL", 7, 2, 15),
        ("AL", 8, 4, None),
        ("MN", 1, 2, 10),
        ("MN", 2, 2, 20),
        ("MN", 3, 4, 26),
        ("MN", 4, 1, 10),
        ("MN", 5, 3, None),
        ("MN", 6, 4, 15),
        ("MN", 7, 2, 15),
        ("MN", 8, 4, None),
        ("MN", 9, 1, 10),
        ("MN", 10, 2, 8),
        ("RM", 1, 2, 10),
        ("RM", 2, 3, 25),
        ("RM", 3, 4, 20),
        ("RM", 4, 1, 10),
        ("RM", 5, 2, None),
        ("RM", 6, 2, 20),
        ("RM", 7, 2, 15),
        ("RM", 8, 4, None),
        ("RM", 9, 1, 10),
        ("RM", 10, 4, 13),
        ("MJ", 1, 2, 10),
        ("MJ", 2, 3, 15),
        ("MJ", 3, 4, 22),
        ("MJ", 4, 1, 10),
        ("LS", 1, 2, 12),
        ("LS", 2, 2, 20),
        ("LS", 3, 3, 16),
        ("LS", 4, 1, 14),
        ("LS", 5, 1, 20),
        ("LS", 6, 4, 20),
    ]
    cursor.executemany("INSERT INTO quarto VALUES (?, ?, ?, ?)", quartos)

    # Inserir reservas
    reservas = [(i, 4, None, None) for i in range(1, 15)]
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

    # Inserir reserva_quarto
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

    # Inserir faturas
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


# Inicializar banco
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM hotel")
    hoteis = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM quarto")
    quartos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM cliente")
    clientes = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(valor), 0) as total FROM fatura")
    faturacao = cursor.fetchone()["total"]

    conn.close()

    return jsonify(
        {
            "hoteis": hoteis,
            "quartos": quartos,
            "clientes": clientes,
            "faturacao": faturacao,
        }
    )


@app.route("/api/clientes")
def clientes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.num_cliente, c.nome, 
               CASE 
                   WHEN i.NIF IS NOT NULL THEN 'Individual'
                   WHEN o.NIPC IS NOT NULL THEN 'Organização'
                   ELSE 'Desconhecido'
               END as tipo,
               COALESCE(i.NIF, o.NIPC, '-') as documento
        FROM cliente c
        LEFT JOIN individual i ON c.num_cliente = i.num_cliente
        LEFT JOIN organizacoes o ON c.num_cliente = o.num_cliente
        ORDER BY c.num_cliente
    """)

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(resultados)


@app.route("/api/hoteis-quartos-livres")
def quartos_livres():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.designacao, COUNT(q.numero) as quartos_livres
        FROM hotel h
        LEFT JOIN quarto q ON h.sigla = q.sigla
        WHERE NOT EXISTS (
            SELECT 1 FROM reserva_quarto rq
            WHERE rq.sigla = h.sigla AND rq.numero = q.numero
        ) OR q.numero IS NULL
        GROUP BY h.designacao
        ORDER BY quartos_livres DESC
    """)

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(resultados)


@app.route("/api/hoteis-quartos")
def hoteis_quartos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.designacao, COUNT(q.numero) as numero_quartos
        FROM hotel h
        LEFT JOIN quarto q ON h.sigla = q.sigla
        GROUP BY h.designacao
    """)

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(resultados)


@app.route("/api/faturacao-hoteis")
def faturacao_hoteis():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.designacao, COALESCE(SUM(f.valor), 0) as faturacao_total
        FROM hotel h
        LEFT JOIN reserva_quarto rq ON h.sigla = rq.sigla
        LEFT JOIN fatura f ON rq.num_reserva = f.num_reserva
        GROUP BY h.designacao
        ORDER BY faturacao_total DESC
    """)

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(resultados)


@app.route("/api/clientes-reservas")
def clientes_reservas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT i.num_cliente) as total
        FROM individual i
        INNER JOIN reserva r ON i.num_cliente = r.num_cliente
    """)

    total = cursor.fetchone()["total"]
    conn.close()

    return jsonify({"total": total})


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Servidor Hotel Transilvânia (SQLite)")
    print("=" * 50)
    print(f"📍 Acesse: http://localhost:5000")
    print(f"📁 Banco de dados: {DB_PATH}")
    print("=" * 50)
    app.run(debug=True, host="localhost", port=5000)
