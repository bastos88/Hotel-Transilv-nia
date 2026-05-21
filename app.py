from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "hotel.db"


def init_db():
    """Cria o banco de dados do zero"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Banco antigo removido")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📝 Criando tabelas...")

    # Criar tabelas
    cursor.execute("""CREATE TABLE hotel (sigla TEXT PRIMARY KEY, designacao TEXT)""")
    cursor.execute(
        """CREATE TABLE quarto (sigla TEXT, numero INTEGER, num_camas INTEGER, preco REAL, PRIMARY KEY (sigla, numero))"""
    )
    cursor.execute(
        """CREATE TABLE cliente (num_cliente INTEGER PRIMARY KEY, nome TEXT)"""
    )
    cursor.execute(
        """CREATE TABLE individual (num_cliente INTEGER PRIMARY KEY, NIF INTEGER)"""
    )
    cursor.execute(
        """CREATE TABLE organizacoes (num_cliente INTEGER PRIMARY KEY, contato TEXT, NIPC INTEGER)"""
    )
    cursor.execute(
        """CREATE TABLE reserva (num_reserva INTEGER PRIMARY KEY, num_cliente INTEGER, dia_entrada DATE, dia_saida DATE)"""
    )
    cursor.execute(
        """CREATE TABLE reserva_quarto (num_reserva INTEGER, sigla TEXT, numero INTEGER, camaextra INTEGER, num_pessoas INTEGER, PRIMARY KEY (num_reserva, sigla, numero))"""
    )
    cursor.execute(
        """CREATE TABLE fatura (num_fatura INTEGER PRIMARY KEY, num_reserva INTEGER, data DATE, valor REAL)"""
    )

    print("📝 Inserindo dados...")

    # Hotéis
    hoteis = [
        ("SH", "Sheraton"),
        ("AL", "Alfa"),
        ("MN", "Mundial"),
        ("RM", "Roma"),
        ("MJ", "Majestic"),
        ("LS", "Lisboa"),
    ]
    cursor.executemany("INSERT INTO hotel VALUES (?, ?)", hoteis)

    # Clientes
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

    # Reservas
    reservas = []
    for i in range(1, 30):
        if i <= 14:
            reservas.append((i, 4, None, None))
        elif i <= 17:
            reservas.append((i, 5, None, None))
        elif i <= 19:
            reservas.append((i, 8, None, None))
        elif i <= 21:
            reservas.append((i, 9, None, None))
        elif i <= 23:
            reservas.append((i, 10, None, None))
        elif i <= 26:
            reservas.append((i, 11, None, None))
        else:
            reservas.append((i, 12, None, None))
    cursor.executemany("INSERT INTO reserva VALUES (?, ?, ?, ?)", reservas)

    # Reserva Quarto
    reserva_quartos = [
        (1, "SH", 1, None, 1),
        (2, "AL", 4, None, 1),
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
    ]
    cursor.executemany(
        "INSERT INTO reserva_quarto VALUES (?, ?, ?, ?, ?)", reserva_quartos
    )

    # Faturas
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


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    conn = get_db()
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.num_cliente, c.nome, 
               CASE WHEN i.NIF IS NOT NULL THEN 'Individual' WHEN o.NIPC IS NOT NULL THEN 'Organização' ELSE 'Desconhecido' END as tipo,
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.designacao, COUNT(q.numero) as quartos_livres
        FROM hotel h
        LEFT JOIN quarto q ON h.sigla = q.sigla
        WHERE NOT EXISTS (SELECT 1 FROM reserva_quarto rq WHERE rq.sigla = h.sigla AND rq.numero = q.numero) OR q.numero IS NULL
        GROUP BY h.designacao
        ORDER BY quartos_livres DESC
    """)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)


@app.route("/api/hoteis-quartos")
def hoteis_quartos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.designacao, COUNT(q.numero) as numero_quartos
        FROM hotel h LEFT JOIN quarto q ON h.sigla = q.sigla GROUP BY h.designacao
    """)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)


@app.route("/api/faturacao-hoteis")
def faturacao_hoteis():
    conn = get_db()
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(DISTINCT i.num_cliente) as total FROM individual i INNER JOIN reserva r ON i.num_cliente = r.num_cliente"
    )
    total = cursor.fetchone()["total"]
    conn.close()
    return jsonify({"total": total})


@app.route("/add-quarto", methods=["POST"])
def add_quarto():
    print("🔵 Rota /add-quarto chamada")
    sigla = request.form.get("sigla")
    numero = request.form.get("num_quartos")
    num_camas = request.form.get("num_camas")
    preco = request.form.get("preco")

    if not all([sigla, numero, num_camas, preco]):
        return (
            jsonify({"success": False, "error": "Todos os campos são obrigatórios"}),
            400,
        )

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM quarto WHERE sigla = ? AND numero = ?", (sigla, numero)
        )
        if cursor.fetchone():
            return (
                jsonify({"success": False, "error": "Quarto já existe neste hotel"}),
                409,
            )

        cursor.execute(
            "INSERT INTO quarto (sigla, numero, num_camas, preco) VALUES (?, ?, ?, ?)",
            (sigla, numero, num_camas, preco),
        )
        conn.commit()
        print(f"✅ Quarto {numero} inserido com sucesso!")
        return jsonify(
            {"success": True, "message": f"Quarto {numero} cadastrado com sucesso!"}
        )
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao inserir quarto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/add-reserva", methods=["POST"])
def add_reserva():
    print("🔵 Rota /add-reserva chamada")

    nome_cliente = request.form.get("nome_cliente")
    sigla_hotel = request.form.get("sigla_hotel")
    numero_quarto = request.form.get("numero_quarto")
    checkin = request.form.get("checkin")
    checkout = request.form.get("checkout")
    num_pessoas = request.form.get("num_pessoas")

    if not all(
        [nome_cliente, sigla_hotel, numero_quarto, checkin, checkout, num_pessoas]
    ):
        return (
            jsonify({"success": False, "error": "Todos os campos são obrigatórios"}),
            400,
        )

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT num_cliente FROM cliente WHERE nome = ?", (nome_cliente,)
        )
        cliente = cursor.fetchone()
        if not cliente:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Cliente "{nome_cliente}" não encontrado',
                    }
                ),
                404,
            )

        cursor.execute(
            "SELECT * FROM quarto WHERE sigla = ? AND numero = ?",
            (sigla_hotel, numero_quarto),
        )
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Quarto não encontrado"}), 404

        cursor.execute(
            "SELECT COALESCE(MAX(num_reserva), 0) + 1 as next_id FROM reserva"
        )
        next_id = cursor.fetchone()["next_id"]

        cursor.execute(
            "INSERT INTO reserva (num_reserva, num_cliente, dia_entrada, dia_saida) VALUES (?, ?, ?, ?)",
            (next_id, cliente["num_cliente"], checkin, checkout),
        )
        cursor.execute(
            "INSERT INTO reserva_quarto (num_reserva, sigla, numero, num_pessoas, camaextra) VALUES (?, ?, ?, ?, ?)",
            (next_id, sigla_hotel, numero_quarto, num_pessoas, None),
        )

        conn.commit()
        print(f"✅ Reserva #{next_id} criada com sucesso!")
        return jsonify(
            {"success": True, "message": f"Reserva #{next_id} criada com sucesso!"}
        )
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar reserva: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


# ============================================
# ROTA PARA ADICIONAR CLIENTE
# ============================================
@app.route("/add-cliente", methods=["POST"])
def add_cliente():
    print("🔵 Rota /add-cliente chamada")

    nome = request.form.get("nome")
    tipo = request.form.get("tipo")
    documento = request.form.get("documento")

    print(f"📝 Dados recebidos: nome={nome}, tipo={tipo}, documento={documento}")

    if not nome:
        return jsonify({"success": False, "error": "Nome é obrigatório"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Verificar se o cliente já existe
        cursor.execute("SELECT * FROM cliente WHERE nome = ?", (nome,))
        if cursor.fetchone():
            return (
                jsonify({"success": False, "error": f'Cliente "{nome}" já existe'}),
                409,
            )

        # Buscar próximo ID
        cursor.execute(
            "SELECT COALESCE(MAX(num_cliente), 0) + 1 as next_id FROM cliente"
        )
        next_id = cursor.fetchone()["next_id"]

        # Inserir cliente
        cursor.execute(
            "INSERT INTO cliente (num_cliente, nome) VALUES (?, ?)", (next_id, nome)
        )

        # Inserir tipo específico
        if tipo == "individual":
            cursor.execute(
                "INSERT INTO individual (num_cliente, NIF) VALUES (?, ?)",
                (next_id, documento if documento else None),
            )
            print(
                f"✅ Cliente individual {nome} (ID: {next_id}) adicionado com sucesso!"
            )
        elif tipo == "organizacao":
            cursor.execute(
                "INSERT INTO organizacoes (num_cliente, NIPC, contato) VALUES (?, ?, ?)",
                (next_id, documento if documento else None, None),
            )
            print(
                f"✅ Cliente organização {nome} (ID: {next_id}) adicionado com sucesso!"
            )

        conn.commit()
        return jsonify(
            {
                "success": True,
                "message": f"Cliente {nome} adicionado com sucesso!",
                "id": next_id,
            }
        )
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao adicionar cliente: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Servidor Hotel Transilvânia (SQLite)")
    print("=" * 50)
    print(f"📍 Acesse: http://localhost:5000")
    print(f"📁 Banco de dados: {DB_PATH}")
    print("=" * 50)
    print("\n📌 Rotas disponíveis:")
    print("   GET  /")
    print("   GET  /api/stats")
    print("   GET  /api/clientes")
    print("   GET  /api/hoteis-quartos-livres")
    print("   GET  /api/hoteis-quartos")
    print("   GET  /api/faturacao-hoteis")
    print("   GET  /api/clientes-reservas")
    print("   POST /add-quarto")
    print("   POST /add-reserva")
    print("   POST /add-cliente")  # NOVA ROTA
    print("=" * 50)

    app.run(debug=True, host="localhost", port=5000)
