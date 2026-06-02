from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
)
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, date, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave_secreta_do_hotel_2026"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = "hotel.db"


# ============================================
# FUNÇÕES DE BANCO DE DADOS
# ============================================


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest" or request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized", "redirect": "/"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# ============================================
# FUNÇÃO PARA GARANTIR TABELAS EXISTEM
# ============================================


def garantir_tabelas():
    """Garante que todas as tabelas necessárias existem no banco de dados"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens_recuperacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE,
            expira_em TIMESTAMP,
            usado BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tentativas_login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            username TEXT,
            tentativas INTEGER DEFAULT 0,
            ultima_tentativa TIMESTAMP,
            bloqueado_ate TIMESTAMP
        )
    """)

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN email TEXT")
        print("✅ Coluna email adicionada à tabela usuarios")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("✅ Tabelas de segurança verificadas/criadas com sucesso!")


# ============================================
# NÍVEL 3 - BLOQUEIO APÓS 3 TENTATIVAS
# ============================================


def registrar_tentativa_falha(ip, username):
    conn = get_db()
    cursor = conn.cursor()
    agora = datetime.now()

    cursor.execute(
        "SELECT * FROM tentativas_login WHERE ip = ? AND username = ?", (ip, username)
    )
    tentativa = cursor.fetchone()

    if tentativa:
        novas_tentativas = tentativa["tentativas"] + 1
        bloqueado_ate = None
        if novas_tentativas >= 3:
            bloqueado_ate = agora + timedelta(minutes=5)

        cursor.execute(
            """
            UPDATE tentativas_login 
            SET tentativas = ?, ultima_tentativa = ?, bloqueado_ate = ?
            WHERE ip = ? AND username = ?
        """,
            (novas_tentativas, agora, bloqueado_ate, ip, username),
        )
    else:
        cursor.execute(
            """
            INSERT INTO tentativas_login (ip, username, tentativas, ultima_tentativa)
            VALUES (?, ?, ?, ?)
        """,
            (ip, username, 1, agora),
        )

    conn.commit()
    conn.close()


def verificar_bloqueio(ip, username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT bloqueado_ate FROM tentativas_login 
        WHERE ip = ? AND username = ? AND bloqueado_ate > datetime('now')
    """,
        (ip, username),
    )
    bloqueado = cursor.fetchone()
    conn.close()

    if bloqueado:
        return True, bloqueado["bloqueado_ate"]
    return False, None


def limpar_tentativas(ip, username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tentativas_login WHERE ip = ? AND username = ?", (ip, username)
    )
    conn.commit()
    conn.close()


# ============================================
# NÍVEL 4 - RECUPERAÇÃO DE PASSWORD
# ============================================


def gerar_token_recuperacao(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens_recuperacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE,
            expira_em TIMESTAMP,
            usado BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        )
    """)

    token = secrets.token_urlsafe(32)
    expira_em = datetime.now() + timedelta(hours=1)

    cursor.execute(
        "INSERT INTO tokens_recuperacao (user_id, token, expira_em) VALUES (?, ?, ?)",
        (user_id, token, expira_em),
    )
    conn.commit()
    conn.close()
    return token


# ============================================
# ROTAS DE AUTENTICAÇÃO
# ============================================


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ip = request.remote_addr

        bloqueado, bloqueado_ate = verificar_bloqueio(ip, username)
        if bloqueado:
            tempo_restante = (
                datetime.fromisoformat(bloqueado_ate) - datetime.now()
            ).seconds // 60
            flash(
                f"🔒 Demasiadas tentativas. Tente novamente em {tempo_restante + 1} minutos.",
                "error",
            )
            return render_template("login.html")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, nome FROM usuarios WHERE username = ?",
            (username,),
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nome"] = user["nome"]
            limpar_tentativas(ip, username)
            flash(f"✅ Bem-vindo(a) {user['nome']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            registrar_tentativa_falha(ip, username)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tentativas FROM tentativas_login WHERE ip = ? AND username = ?",
                (ip, username),
            )
            tentativa = cursor.fetchone()
            conn.close()

            tentativas_restantes = 3 - (tentativa["tentativas"] if tentativa else 1)
            if tentativas_restantes > 0:
                flash(
                    f"❌ Username ou senha inválidos. Tem {tentativas_restantes} tentativa(s) restante(s).",
                    "error",
                )
            else:
                flash("🔒 Conta temporariamente bloqueada. Aguarde 5 minutos.", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        ip = request.remote_addr

        bloqueado, _ = verificar_bloqueio(ip, username)
        if bloqueado:
            return (
                jsonify(
                    {"success": False, "error": "Conta temporariamente bloqueada."}
                ),
                401,
            )

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, nome FROM usuarios WHERE username = ?",
            (username,),
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nome"] = user["nome"]
            limpar_tentativas(ip, username)
            return jsonify({"success": True, "redirect": "/dashboard"})
        else:
            registrar_tentativa_falha(ip, username)
            return (
                jsonify({"success": False, "error": "Usuário ou senha inválidos"}),
                401,
            )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/registar", methods=["GET", "POST"])
def registar():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmar = request.form.get("confirmar")
        nome_completo = request.form.get("nome_completo")
        email = request.form.get("email")

        if not username or len(username) < 3:
            flash("❌ Username deve ter pelo menos 3 caracteres.", "error")
            return render_template("registar.html")
        if not password or len(password) < 6:
            flash("❌ Password deve ter pelo menos 6 caracteres.", "error")
            return render_template("registar.html")
        if password != confirmar:
            flash("❌ As passwords não coincidem.", "error")
            return render_template("registar.html")
        if not nome_completo:
            flash("❌ Nome completo é obrigatório.", "error")
            return render_template("registar.html")
        if not email or "@" not in email:
            flash("❌ Email inválido.", "error")
            return render_template("registar.html")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("❌ Username já existe.", "error")
            conn.close()
            return render_template("registar.html")

        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            flash("❌ Email já registado.", "error")
            conn.close()
            return render_template("registar.html")

        senha_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (username, password, nome, email) VALUES (?, ?, ?, ?)",
            (username, senha_hash, nome_completo, email),
        )
        conn.commit()
        conn.close()

        flash(f"✅ Registo efetuado com sucesso! Faça login com {username}.", "success")
        return redirect(url_for("login"))

    return render_template("registar.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html", username=session.get("username"), nome=session.get("nome")
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("🔓 Sessão terminada com sucesso.", "info")
    return redirect(url_for("login"))


@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    return render_template("admin.html", username=session.get("username", "Admin"))


@app.route("/site")
def index_public():
    return render_template("index.html")


# ============================================
# NÍVEL 4 - RECUPERAÇÃO DE PASSWORD (ROTAS)
# ============================================


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, nome FROM usuarios WHERE email = ?", (email,)
        )
        user = cursor.fetchone()

        if user:
            token = gerar_token_recuperacao(user["id"])
            link_recuperacao = f"http://localhost:5000/redefinir/{token}"
            flash(f"📧 Link de teste: {link_recuperacao}", "warning")
            flash(f"📧 Um link de recuperação foi gerado para {email}.", "info")
        else:
            flash("❌ Email não encontrado.", "error")

        conn.close()
        return redirect(url_for("login"))

    return render_template("recuperar.html")


@app.route("/redefinir/<token>", methods=["GET", "POST"])
def redefinir_password(token):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM tokens_recuperacao 
        WHERE token = ? AND usado = 0 AND expira_em > datetime('now')
    """,
        (token,),
    )
    token_rec = cursor.fetchone()

    if not token_rec:
        conn.close()
        flash("❌ Link de recuperação inválido ou expirado.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        nova_password = request.form.get("nova_password", "")
        confirmar = request.form.get("confirmar", "")

        if not nova_password or len(nova_password) < 6:
            flash("❌ Password deve ter pelo menos 6 caracteres.", "error")
        elif nova_password != confirmar:
            flash("❌ As passwords não coincidem.", "error")
        else:
            nova_hash = generate_password_hash(nova_password)
            cursor.execute(
                "UPDATE usuarios SET password = ? WHERE id = ?",
                (nova_hash, token_rec["user_id"]),
            )
            cursor.execute(
                "UPDATE tokens_recuperacao SET usado = 1 WHERE id = ?",
                (token_rec["id"],),
            )
            conn.commit()
            conn.close()
            flash(
                "✅ Password redefinida com sucesso! Faça login com a nova password.",
                "success",
            )
            return redirect(url_for("login"))

    conn.close()
    return render_template("redefinir.html", token=token)


# ============================================
# API - RESERVAS DO SITE PÚBLICO
# ============================================


@app.route("/api/site/reserva", methods=["POST"])
def site_reserva():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        tipo_quarto = request.form.get("tipo_quarto")
        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        hospedes = request.form.get("hospedes")
        mensagem = request.form.get("mensagem")

        if not all([nome, email, telefone, checkin, checkout, hospedes]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Todos os campos obrigatórios devem ser preenchidos",
                    }
                ),
                400,
            )

        if not tipo_quarto or tipo_quarto not in ["standard", "luxo", "suite"]:
            return (
                jsonify(
                    {"success": False, "error": "Selecione um tipo de suíte válido"}
                ),
                400,
            )

        checkin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
        checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()

        quarto_map = {
            "standard": {
                "sigla": "SH",
                "numero": 1,
                "preco": 120,
                "nome": "Forest Chamber",
            },
            "luxo": {
                "sigla": "SH",
                "numero": 2,
                "preco": 220,
                "nome": "Mountain Grand",
            },
            "suite": {
                "sigla": "SH",
                "numero": 3,
                "preco": 450,
                "nome": "Sovereign Suite",
            },
        }
        quarto = quarto_map.get(tipo_quarto, quarto_map["standard"])

        conn = get_db()
        cursor = conn.cursor()

        # VERIFICAR DISPONIBILIDADE
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM reserva_quarto rq
            JOIN reserva r ON rq.num_reserva = r.num_reserva
            WHERE rq.sigla = ? AND rq.numero = ?
            AND (
                (r.dia_entrada <= ? AND r.dia_saida >= ?) OR
                (r.dia_entrada <= ? AND r.dia_saida >= ?) OR
                (r.dia_entrada >= ? AND r.dia_entrada < ?)
            )
        """,
            (
                quarto["sigla"],
                quarto["numero"],
                checkin_date,
                checkin_date,
                checkout_date,
                checkout_date,
                checkin_date,
                checkout_date,
            ),
        )

        if cursor.fetchone()["total"] > 0:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"O quarto {quarto['nome']} está ocupado neste período. Por favor, escolha outro quarto ou datas.",
                        "ocupado": True,
                    }
                ),
                409,
            )

        # Verificar se cliente já existe
        cursor.execute("SELECT num_cliente FROM cliente WHERE nome = ?", (nome,))
        cliente = cursor.fetchone()

        if not cliente:
            cursor.execute("SELECT MAX(num_cliente) as max_id FROM cliente")
            max_id = cursor.fetchone()["max_id"] or 0
            next_id = max_id + 1
            cursor.execute(
                "INSERT INTO cliente (num_cliente, nome) VALUES (?, ?)", (next_id, nome)
            )
            cliente_id = next_id
            cursor.execute(
                "INSERT INTO individual (num_cliente, NIF) VALUES (?, ?)",
                (next_id, None),
            )
        else:
            cliente_id = cliente["num_cliente"]

        cursor.execute("SELECT MAX(num_reserva) as max_id FROM reserva")
        max_reserva = cursor.fetchone()["max_id"] or 0
        num_reserva = max_reserva + 1

        cursor.execute(
            "INSERT INTO reserva (num_reserva, num_cliente, dia_entrada, dia_saida) VALUES (?, ?, ?, ?)",
            (num_reserva, cliente_id, checkin_date, checkout_date),
        )

        cursor.execute(
            "INSERT INTO reserva_quarto (num_reserva, sigla, numero, num_pessoas) VALUES (?, ?, ?, ?)",
            (num_reserva, quarto["sigla"], quarto["numero"], int(hospedes)),
        )

        num_dias = (checkout_date - checkin_date).days
        valor_total = quarto["preco"] * num_dias

        cursor.execute("SELECT MAX(num_fatura) as max_id FROM fatura")
        max_fatura = cursor.fetchone()["max_id"] or 0
        num_fatura = max_fatura + 1

        cursor.execute(
            "INSERT INTO fatura (num_fatura, num_reserva, data, valor) VALUES (?, ?, ?, ?)",
            (num_fatura, num_reserva, date.today(), valor_total),
        )

        conn.commit()
        conn.close()

        return jsonify(
            {
                "success": True,
                "message": f"✨ Reserva #{num_reserva} confirmada! Suíte: {quarto['nome']}, Valor: €{valor_total}.",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# API - ESTATÍSTICAS E RELATÓRIOS
# ============================================


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
    cursor.execute("SELECT COUNT(*) as total FROM reserva")
    reservas = cursor.fetchone()["total"]
    cursor.execute("SELECT COALESCE(SUM(valor), 0) as total FROM fatura")
    faturacao = cursor.fetchone()["total"]
    conn.close()
    return jsonify(
        {
            "hoteis": hoteis,
            "quartos": quartos,
            "clientes": clientes,
            "reservas": reservas,
            "faturacao": faturacao,
        }
    )


@app.route("/api/clientes")
def api_clientes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.num_cliente, c.nome, 
               CASE WHEN i.NIF IS NOT NULL THEN 'Individual' ELSE 'Organização' END as tipo,
               COALESCE(i.NIF, o.NIPC, '-') as documento
        FROM cliente c
        LEFT JOIN individual i ON c.num_cliente = i.num_cliente
        LEFT JOIN organizacoes o ON c.num_cliente = o.num_cliente
        ORDER BY c.num_cliente
    """)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)


@app.route("/api/reservas")
def api_reservas():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.num_reserva, c.nome as cliente_nome, r.dia_entrada, r.dia_saida,
               julianday(r.dia_saida) - julianday(r.dia_entrada) as num_dias,
               COALESCE(f.valor, 0) as valor_total
        FROM reserva r
        JOIN cliente c ON r.num_cliente = c.num_cliente
        LEFT JOIN fatura f ON r.num_reserva = f.num_reserva
        ORDER BY r.num_reserva DESC LIMIT 50
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
        FROM hotel h LEFT JOIN quarto q ON h.sigla = q.sigla GROUP BY h.sigla
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
        GROUP BY h.sigla ORDER BY faturacao_total DESC
    """)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)


@app.route("/api/ocupacao-hoteis")
def ocupacao_hoteis():
    conn = get_db()
    cursor = conn.cursor()
    hoje = date.today().isoformat()

    cursor.execute("SELECT sigla, designacao FROM hotel")
    hoteis = cursor.fetchall()

    resultados = []
    for hotel in hoteis:
        sigla = hotel["sigla"]
        designacao = hotel["designacao"]

        cursor.execute("SELECT COUNT(*) as total FROM quarto WHERE sigla = ?", (sigla,))
        total_quartos = cursor.fetchone()["total"] or 0

        cursor.execute(
            """
            SELECT COUNT(DISTINCT rq.numero) as ocupados
            FROM reserva_quarto rq
            JOIN reserva r ON rq.num_reserva = r.num_reserva
            WHERE rq.sigla = ? AND r.dia_entrada <= ? AND r.dia_saida >= ?
        """,
            (sigla, hoje, hoje),
        )
        ocupados = cursor.fetchone()["ocupados"] or 0

        taxa = round((ocupados / total_quartos * 100), 2) if total_quartos > 0 else 0

        resultados.append(
            {
                "designacao": designacao,
                "total_quartos": total_quartos,
                "quartos_ocupados": ocupados,
                "taxa_ocupacao": taxa,
            }
        )

    conn.close()
    return jsonify(resultados)


@app.route("/api/clientes-top")
def clientes_top():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.nome, COUNT(DISTINCT r.num_reserva) as total_reservas,
               COALESCE(SUM(f.valor), 0) as total_gasto,
               CASE WHEN i.NIF IS NOT NULL THEN 'Individual' ELSE 'Organização' END as tipo
        FROM cliente c
        LEFT JOIN reserva r ON c.num_cliente = r.num_cliente
        LEFT JOIN fatura f ON r.num_reserva = f.num_reserva
        LEFT JOIN individual i ON c.num_cliente = i.num_cliente
        LEFT JOIN organizacoes o ON c.num_cliente = o.num_cliente
        GROUP BY c.num_cliente ORDER BY total_reservas DESC LIMIT 10
    """)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)


@app.route("/api/hoteis-completos")
def hoteis_completos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT sigla, designacao FROM hotel ORDER BY designacao")
    hoteis = cursor.fetchall()

    resultados = []
    for hotel in hoteis:
        sigla = hotel["sigla"]
        designacao = hotel["designacao"]

        cursor.execute("SELECT COUNT(*) as total FROM quarto WHERE sigla = ?", (sigla,))
        total_quartos = cursor.fetchone()["total"] or 0

        cursor.execute(
            """
            SELECT COUNT(DISTINCT r.num_reserva) as total 
            FROM reserva r JOIN reserva_quarto rq ON r.num_reserva = rq.num_reserva WHERE rq.sigla = ?
        """,
            (sigla,),
        )
        total_reservas = cursor.fetchone()["total"] or 0

        cursor.execute(
            """
            SELECT COALESCE(SUM(f.valor), 0) as total
            FROM fatura f JOIN reserva r ON f.num_reserva = r.num_reserva
            JOIN reserva_quarto rq ON r.num_reserva = rq.num_reserva WHERE rq.sigla = ?
        """,
            (sigla,),
        )
        faturacao = cursor.fetchone()["total"] or 0

        resultados.append(
            {
                "sigla": sigla,
                "designacao": designacao,
                "total_quartos": total_quartos,
                "total_reservas": total_reservas,
                "faturacao_total": faturacao,
            }
        )

    conn.close()
    return jsonify(resultados)


@app.route("/api/poo/relatorio-completo")
def poo_relatorio_completo():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.designacao, COALESCE(SUM(f.valor), 0) as faturacao
        FROM hotel h LEFT JOIN reserva_quarto rq ON h.sigla = rq.sigla
        LEFT JOIN fatura f ON rq.num_reserva = f.num_reserva GROUP BY h.sigla ORDER BY faturacao DESC LIMIT 1
    """)
    hotel_faturacao = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM hotel")
    total_hoteis = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT c.nome, COUNT(DISTINCT r.num_reserva) as total_reservas,
               COALESCE(SUM(f.valor), 0) as total_gasto
        FROM organizacoes o JOIN cliente c ON o.num_cliente = c.num_cliente
        LEFT JOIN reserva r ON o.num_cliente = r.num_cliente
        LEFT JOIN fatura f ON r.num_reserva = f.num_reserva
        GROUP BY o.num_cliente ORDER BY total_reservas DESC
    """)
    reservas_org = [dict(row) for row in cursor.fetchall()]

    organizacoes_todos = []
    if total_hoteis > 0:
        cursor.execute(
            """
            SELECT c.nome, COUNT(DISTINCT rq.sigla) as hoteis_visitados
            FROM organizacoes o JOIN cliente c ON o.num_cliente = c.num_cliente
            JOIN reserva r ON o.num_cliente = r.num_cliente
            JOIN reserva_quarto rq ON r.num_reserva = rq.num_reserva
            GROUP BY o.num_cliente HAVING COUNT(DISTINCT rq.sigla) = ?
        """,
            (total_hoteis,),
        )
        organizacoes_todos = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(
        {
            "hotel_maior_faturacao": {
                "nome": hotel_faturacao["designacao"] if hotel_faturacao else "Nenhum",
                "faturacao": hotel_faturacao["faturacao"] if hotel_faturacao else 0,
            },
            "reservas_por_organizacao": reservas_org,
            "total_hoteis": total_hoteis,
            "organizacoes_todos_hoteis": organizacoes_todos,
        }
    )


# ============================================
# ROTAS CRUD
# ============================================


@app.route("/api/admin/add-cliente", methods=["POST"])
@login_required
def admin_add_cliente():
    try:
        data = request.get_json()
        nome = data.get("nome")
        tipo = data.get("tipo")
        documento = data.get("documento")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(num_cliente) as max_id FROM cliente")
        max_id = cursor.fetchone()["max_id"] or 0
        next_id = max_id + 1

        cursor.execute(
            "INSERT INTO cliente (num_cliente, nome) VALUES (?, ?)", (next_id, nome)
        )

        if tipo == "individual":
            cursor.execute(
                "INSERT INTO individual (num_cliente, NIF) VALUES (?, ?)",
                (next_id, documento),
            )
        else:
            cursor.execute(
                "INSERT INTO organizacoes (num_cliente, NIPC) VALUES (?, ?)",
                (next_id, documento),
            )

        conn.commit()
        conn.close()
        return jsonify(
            {"success": True, "message": f"Cliente {nome} adicionado com sucesso!"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/delete-cliente/<int:cliente_id>", methods=["DELETE"])
@login_required
def admin_delete_cliente(cliente_id):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT nome FROM cliente WHERE num_cliente = ?", (cliente_id,))
        cliente = cursor.fetchone()
        if not cliente:
            return jsonify({"success": False, "error": "Cliente não encontrado"}), 404

        cursor.execute(
            "DELETE FROM fatura WHERE num_reserva IN (SELECT num_reserva FROM reserva WHERE num_cliente = ?)",
            (cliente_id,),
        )
        cursor.execute("DELETE FROM reserva WHERE num_cliente = ?", (cliente_id,))
        cursor.execute("DELETE FROM cliente WHERE num_cliente = ?", (cliente_id,))

        conn.commit()
        conn.close()
        return jsonify(
            {
                "success": True,
                "message": f"Cliente {cliente['nome']} removido com sucesso!",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/delete-reserva/<int:reserva_id>", methods=["DELETE"])
@login_required
def admin_delete_reserva(reserva_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fatura WHERE num_reserva = ?", (reserva_id,))
        cursor.execute(
            "DELETE FROM reserva_quarto WHERE num_reserva = ?", (reserva_id,)
        )
        cursor.execute("DELETE FROM reserva WHERE num_reserva = ?", (reserva_id,))
        conn.commit()
        conn.close()
        return jsonify(
            {"success": True, "message": f"Reserva #{reserva_id} removida com sucesso!"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/delete-all-reservas", methods=["DELETE"])
@login_required
def admin_delete_all_reservas():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fatura")
        cursor.execute("DELETE FROM reserva_quarto")
        cursor.execute("DELETE FROM reserva")
        conn.commit()
        conn.close()
        return jsonify(
            {"success": True, "message": "Todas as reservas foram removidas!"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/add-quarto", methods=["POST"])
@login_required
def admin_add_quarto():
    try:
        data = request.get_json()
        sigla = data.get("sigla")
        numero = data.get("numero")
        num_camas = data.get("num_camas")
        preco = data.get("preco")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quarto (sigla, numero, num_camas, preco) VALUES (?, ?, ?, ?)",
            (sigla, numero, num_camas, preco),
        )
        conn.commit()
        conn.close()
        return jsonify(
            {"success": True, "message": f"Quarto {numero} adicionado com sucesso!"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ============================================


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Banco antigo removido")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE hotel (sigla TEXT PRIMARY KEY, designacao TEXT)")
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
        "CREATE TABLE reserva_quarto (num_reserva INTEGER, sigla TEXT, numero INTEGER, camaextra INTEGER, num_pessoas INTEGER, PRIMARY KEY (num_reserva, sigla, numero))"
    )
    cursor.execute(
        "CREATE TABLE fatura (num_fatura INTEGER PRIMARY KEY, num_reserva INTEGER, data DATE, valor REAL)"
    )
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL, nome TEXT, email TEXT, is_admin INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE tentativas_login (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, username TEXT,
            tentativas INTEGER DEFAULT 0, ultima_tentativa TIMESTAMP, bloqueado_ate TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE tokens_recuperacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, token TEXT UNIQUE,
            expira_em TIMESTAMP, usado BOOLEAN DEFAULT 0, FOREIGN KEY (user_id) REFERENCES usuarios(id)
        )
    """)

    print("📝 Inserindo dados...")

    hoteis = [
        ("SH", "Sheraton"),
        ("AL", "Alfa"),
        ("MN", "Mundial"),
        ("RM", "Roma"),
        ("MJ", "Majestic"),
        ("LS", "Lisboa"),
    ]
    cursor.executemany("INSERT INTO hotel VALUES (?, ?)", hoteis)

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

    quartos = [
        ("SH", 1, 2, 120),
        ("SH", 2, 2, 220),
        ("SH", 3, 4, 450),
        ("AL", 1, 2, 100),
        ("AL", 2, 3, 180),
        ("AL", 3, 4, 250),
        ("MN", 1, 2, 130),
        ("MN", 2, 2, 200),
        ("MN", 3, 4, 350),
        ("RM", 1, 2, 110),
        ("RM", 2, 3, 190),
        ("RM", 3, 4, 280),
        ("MJ", 1, 2, 140),
        ("MJ", 2, 3, 210),
        ("MJ", 3, 4, 320),
        ("LS", 1, 2, 125),
        ("LS", 2, 3, 195),
        ("LS", 3, 4, 300),
    ]
    cursor.executemany("INSERT INTO quarto VALUES (?, ?, ?, ?)", quartos)

    senha_hash = generate_password_hash("admin123")
    cursor.execute(
        "INSERT INTO usuarios (username, password, nome, email) VALUES (?, ?, ?, ?)",
        ("admin", senha_hash, "Administrador", "admin@hotel.com"),
    )

    conn.commit()
    conn.close()
    print("✅ Banco de dados criado com sucesso!")
    print("📝 Utilizador admin: admin / admin123")


if not os.path.exists(DB_PATH):
    init_db()
else:
    garantir_tabelas()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 HOTEL TRANSILVÂNIA - Servidor Completo")
    print("=" * 50)
    print(f"📍 Site público: http://localhost:5000/site")
    print(f"📍 Login: http://localhost:5000/login")
    print(f"📍 Registo: http://localhost:5000/registar")
    print(f"📍 Recuperar password: http://localhost:5000/recuperar")
    print(f"📍 Admin: http://localhost:5000/admin-dashboard")
    print(f"🔑 Credenciais: admin / admin123")
    print("=" * 50)
    app.run(debug=True, host="localhost", port=5000)
