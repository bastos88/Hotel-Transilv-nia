import sqlite3


def adicionar_cliente(nome, nif=None, tipo="individual"):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    # Buscar próximo ID
    cursor.execute("SELECT COALESCE(MAX(num_cliente), 0) + 1 FROM cliente")
    next_id = cursor.fetchone()[0]

    # Inserir cliente
    cursor.execute(
        "INSERT INTO cliente (num_cliente, nome) VALUES (?, ?)", (next_id, nome)
    )

    if tipo == "individual":
        cursor.execute(
            "INSERT INTO individual (num_cliente, NIF) VALUES (?, ?)", (next_id, nif)
        )
    elif tipo == "organizacao":
        cursor.execute(
            "INSERT INTO organizacoes (num_cliente, NIPC) VALUES (?, ?)", (next_id, nif)
        )

    conn.commit()
    conn.close()
    print(f"✅ Cliente '{nome}' adicionado com ID {next_id}")


# Adicionar Leonardo
adicionar_cliente("Leonardo", 123456789, "individual")

# Listar todos os clientes para verificar
conn = sqlite3.connect("hotel.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM cliente")
print("\n📋 Todos os clientes:")
for cliente in cursor.fetchall():
    print(f"   ID: {cliente[0]}, Nome: {cliente[1]}")
conn.close()
