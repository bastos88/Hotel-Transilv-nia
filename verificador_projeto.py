#!/usr/bin/env python3
"""
Script de Verificação do Projeto Hotel Transilvânia
Verifica se todas as condições do enunciado foram satisfeitas
"""

import os
import re
import sys
import sqlite3
from datetime import datetime


# Cores para output no terminal
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ️ {text}{Colors.RESET}")


class ProjetoVerificador:
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.results = {
            "requisitos_obrigatorios": [],
            "niveis_extra": [],
            "seguranca": [],
            "estrutura": [],
        }
        self.app_py_path = os.path.join(project_path, "app.py")
        self.templates_path = os.path.join(project_path, "templates")

    def verificar_arquivos_estrutura(self):
        """Verifica se a estrutura de ficheiros está correta"""
        print_header("1. VERIFICANDO ESTRUTURA DE FICHEIROS")

        arquivos_necessarios = [
            "app.py",
            "templates/login.html",
            "templates/registar.html",  # ou registo.html
            "templates/dashboard.html",
        ]

        for arquivo in arquivos_necessarios:
            caminho = os.path.join(self.project_path, arquivo)
            if os.path.exists(caminho):
                print_success(f"Arquivo encontrado: {arquivo}")
                self.results["estrutura"].append({"item": arquivo, "status": True})
            else:
                # Verificar alternativa para registo.html
                if arquivo == "templates/registar.html":
                    if os.path.exists(
                        os.path.join(self.project_path, "templates/registo.html")
                    ):
                        print_success(f"Arquivo encontrado: templates/registo.html")
                        self.results["estrutura"].append(
                            {"item": "templates/registo.html", "status": True}
                        )
                    else:
                        print_error(f"Arquivo não encontrado: {arquivo}")
                        self.results["estrutura"].append(
                            {"item": arquivo, "status": False}
                        )
                else:
                    print_error(f"Arquivo não encontrado: {arquivo}")
                    self.results["estrutura"].append({"item": arquivo, "status": False})

        # Verificar banco de dados
        if os.path.exists(
            os.path.join(self.project_path, "hotel.db")
        ) or os.path.exists(os.path.join(self.project_path, "utilizadores.db")):
            print_success("Banco de dados encontrado")
        else:
            print_warning("Banco de dados não encontrado (será criado ao executar)")

    def verificar_requisitos_obrigatorios(self):
        """Verifica os 4 requisitos obrigatórios"""
        print_header("2. VERIFICANDO REQUISITOS OBRIGATÓRIOS")

        if not os.path.exists(self.app_py_path):
            print_error("Arquivo app.py não encontrado!")
            return

        with open(self.app_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Registar utilizadores
        if re.search(r'@app\.route\([\'"]/regist(ar|o)[\'"]', content) or re.search(
            r"def regist(ar|o)", content
        ):
            print_success("1. Registar utilizadores - Implementado")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Registar utilizadores", "status": True}
            )
        else:
            print_error("1. Registar utilizadores - NÃO IMPLEMENTADO")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Registar utilizadores", "status": False}
            )

        # 2. Fazer login
        if (
            re.search(r'@app\.route\([\'"]/login[\'"]', content)
            and "def login" in content
        ):
            print_success("2. Fazer login - Implementado")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Fazer login", "status": True}
            )
        else:
            print_error("2. Fazer login - NÃO IMPLEMENTADO")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Fazer login", "status": False}
            )

        # 3. Aceder a página protegida
        if (
            re.search(r'@app\.route\([\'"]/dashboard[\'"]', content)
            and "login_required" in content
        ):
            print_success("3. Aceder a página protegida - Implementado")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Página protegida", "status": True}
            )
        else:
            print_error("3. Aceder a página protegida - NÃO IMPLEMENTADO")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Página protegida", "status": False}
            )

        # 4. Terminar sessão (logout)
        if re.search(r'@app\.route\([\'"]/logout[\'"]', content) and (
            "session.clear" in content or "session.pop" in content
        ):
            print_success("4. Terminar sessão (logout) - Implementado")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Logout", "status": True}
            )
        else:
            print_error("4. Terminar sessão (logout) - NÃO IMPLEMENTADO")
            self.results["requisitos_obrigatorios"].append(
                {"item": "Logout", "status": False}
            )

    def verificar_seguranca(self):
        """Verifica os requisitos de segurança"""
        print_header("3. VERIFICANDO REQUISITOS DE SEGURANÇA")

        if not os.path.exists(self.app_py_path):
            return

        with open(self.app_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Hash de passwords
        if "generate_password_hash" in content and "check_password_hash" in content:
            print_success("Hash de passwords - Implementado (werkzeug.security)")
            self.results["seguranca"].append(
                {"item": "Hash de passwords", "status": True}
            )
        else:
            print_error("Hash de passwords - NÃO IMPLEMENTADO")
            self.results["seguranca"].append(
                {"item": "Hash de passwords", "status": False}
            )

        # Utilização de sessões
        if "from flask import session" in content or "session[" in content:
            print_success("Utilização de sessões - Implementado")
            self.results["seguranca"].append({"item": "Sessões", "status": True})
        else:
            print_error("Utilização de sessões - NÃO IMPLEMENTADO")
            self.results["seguranca"].append({"item": "Sessões", "status": False})

        # Proteção de rotas
        if "login_required" in content or "@login_required" in content:
            print_success("Proteção de rotas - Implementado (decorator)")
            self.results["seguranca"].append(
                {"item": "Proteção de rotas", "status": True}
            )
        else:
            # Verificar proteção manual
            if re.search(r'if ["\']utilizador["\'] not in session', content):
                print_success("Proteção de rotas - Implementado (manual)")
                self.results["seguranca"].append(
                    {"item": "Proteção de rotas", "status": True}
                )
            else:
                print_error("Proteção de rotas - NÃO IMPLEMENTADO")
                self.results["seguranca"].append(
                    {"item": "Proteção de rotas", "status": False}
                )

    def verificar_niveis_extra(self):
        """Verifica os níveis extra"""
        print_header("4. VERIFICANDO NÍVEIS EXTRA")

        if not os.path.exists(self.app_py_path):
            return

        with open(self.app_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Nível 1: Nome completo e email
        if "nome_completo" in content or "nome" in content and "email" in content:
            # Verificar nos templates também
            template_registo = os.path.join(self.templates_path, "registar.html")
            if os.path.exists(template_registo):
                with open(template_registo, "r", encoding="utf-8") as tf:
                    template_content = tf.read()
                    if "nome" in template_content and "email" in template_content:
                        print_success("Nível 1 - Nome completo e email - Implementado")
                        self.results["niveis_extra"].append(
                            {"item": "Nível 1 (Nome/Email)", "status": True}
                        )
                    else:
                        print_warning("Nível 1 - Verificar templates")
                        self.results["niveis_extra"].append(
                            {"item": "Nível 1 (Nome/Email)", "status": True}
                        )
            else:
                print_success("Nível 1 - Nome completo e email - Implementado")
                self.results["niveis_extra"].append(
                    {"item": "Nível 1 (Nome/Email)", "status": True}
                )
        else:
            print_warning("Nível 1 - Nome completo e email - NÃO IMPLEMENTADO")
            self.results["niveis_extra"].append(
                {"item": "Nível 1 (Nome/Email)", "status": False}
            )

        # Nível 2: Confirmação de password
        if "confirmar" in content and "password != confirmar" in content:
            print_success("Nível 2 - Confirmação de password - Implementado")
            self.results["niveis_extra"].append(
                {"item": "Nível 2 (Confirmação password)", "status": True}
            )
        else:
            print_warning("Nível 2 - Confirmação de password - NÃO IMPLEMENTADO")
            self.results["niveis_extra"].append(
                {"item": "Nível 2 (Confirmação password)", "status": False}
            )

        # Nível 3: Bloqueio após 3 tentativas
        if "tentativas" in content and (
            "bloqueado" in content or "bloqueio" in content
        ):
            print_success("Nível 3 - Bloqueio após 3 tentativas - Implementado")
            self.results["niveis_extra"].append(
                {"item": "Nível 3 (Bloqueio tentativas)", "status": True}
            )
        else:
            print_warning("Nível 3 - Bloqueio após 3 tentativas - NÃO IMPLEMENTADO")
            self.results["niveis_extra"].append(
                {"item": "Nível 3 (Bloqueio tentativas)", "status": False}
            )

        # Nível 4: Recuperação de password
        if "recuperar" in content and ("token" in content or "redefinir" in content):
            print_success("Nível 4 - Recuperação de password - Implementado")
            self.results["niveis_extra"].append(
                {"item": "Nível 4 (Recuperação password)", "status": True}
            )
        else:
            print_warning("Nível 4 - Recuperação de password - NÃO IMPLEMENTADO")
            self.results["niveis_extra"].append(
                {"item": "Nível 4 (Recuperação password)", "status": False}
            )

    def verificar_banco_dados(self):
        """Verifica se a base de dados tem a estrutura correta"""
        print_header("5. VERIFICANDO BANCO DE DADOS")

        db_paths = ["hotel.db", "utilizadores.db"]
        db_encontrado = False

        for db_path in db_paths:
            caminho = os.path.join(self.project_path, db_path)
            if os.path.exists(caminho):
                db_encontrado = True
                try:
                    conn = sqlite3.connect(caminho)
                    cursor = conn.cursor()

                    # Verificar tabela de utilizadores
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'"
                    )
                    if cursor.fetchone():
                        print_success(f"Tabela 'usuarios' encontrada em {db_path}")

                        # Verificar colunas
                        cursor.execute("PRAGMA table_info(usuarios)")
                        colunas = [col[1] for col in cursor.fetchall()]

                        colunas_necessarias = ["id", "username", "password"]
                        for col in colunas_necessarias:
                            if col in colunas:
                                print_success(f"  - Coluna '{col}' encontrada")
                            else:
                                print_warning(f"  - Coluna '{col}' NÃO encontrada")

                        # Verificar se existe utilizador admin
                        cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
                        if cursor.fetchone():
                            print_success("  - Utilizador admin encontrado")
                        else:
                            print_warning("  - Utilizador admin NÃO encontrado")

                    conn.close()
                except Exception as e:
                    print_error(f"Erro ao ler banco de dados: {e}")
                break

        if not db_encontrado:
            print_warning(
                "Nenhum banco de dados encontrado (será criado na primeira execução)"
            )

    def verificar_templates(self):
        """Verifica o conteúdo dos templates HTML"""
        print_header("6. VERIFICANDO TEMPLATES HTML")

        templates = {
            "login.html": ["form", "username", "password", "submit"],
            "registar.html": [
                "form",
                "username",
                "password",
                "confirmar",
                "nome",
                "email",
            ],
            "dashboard.html": ["Bem-vindo", "logout", "session"],
        }

        for template, palavras_chave in templates.items():
            # Verificar possíveis nomes alternativos
            caminhos = [
                os.path.join(self.templates_path, template),
                os.path.join(
                    self.templates_path, template.replace("registar", "registo")
                ),
            ]

            encontrado = False
            for caminho in caminhos:
                if os.path.exists(caminho):
                    encontrado = True
                    with open(caminho, "r", encoding="utf-8") as f:
                        content = f.read()
                        print_success(f"{template} - Encontrado")

                        for palavra in palavras_chave:
                            if palavra.lower() in content.lower():
                                print_success(f"  - Palavra '{palavra}' encontrada")
                            else:
                                print_warning(f"  - Palavra '{palavra}' NÃO encontrada")
                    break

            if not encontrado:
                print_error(f"{template} - NÃO ENCONTRADO")

    def verificar_questoes_reflexao(self):
        """Verifica se as questões de reflexão foram respondidas"""
        print_header("7. QUESTÕES DE REFLEXÃO")

        questoes = [
            "Porque não devemos guardar passwords em texto simples?",
            "O que é uma função hash?",
            "Qual a diferença entre autenticação e autorização?",
            "O que acontece quando um utilizador termina sessão?",
            "Como proteger uma aplicação contra ataques de força bruta?",
        ]

        print_info("As seguintes questões devem ser respondidas na documentação:\n")
        for i, questao in enumerate(questoes, 1):
            print(f"   {i}. {questao}")

        print("\n" + "=" * 60)
        print("Respostas sugeridas:\n")

        respostas = [
            "Por razões de segurança. Se a base de dados for comprometida, as passwords dos utilizadores ficam expostas. O hash torna as passwords irreversíveis.",
            "É uma função matemática unidirecional que converte dados de qualquer tamanho em uma string de tamanho fixo. É determinística e não pode ser revertida.",
            "Autenticação verifica quem é o utilizador (login). Autorização verifica o que o utilizador pode fazer (permissões/acessos).",
            "Os dados da sessão são removidos do servidor, o cookie de sessão é invalidado, e o utilizador precisa autenticar-se novamente.",
            "Bloqueio após N tentativas, CAPTCHA, atraso progressivo, autenticação de dois fatores (2FA), rate limiting por IP.",
        ]

        for i, resposta in enumerate(respostas, 1):
            print(f"{i}. {resposta}\n")

    def gerar_relatorio_final(self):
        """Gera o relatório final com a pontuação"""
        print_header("📊 RELATÓRIO FINAL")

        total_items = 0
        items_ok = 0

        # Calcular requisitos obrigatórios
        for item in self.results["requisitos_obrigatorios"]:
            total_items += 1
            if item["status"]:
                items_ok += 1

        # Calcular segurança
        for item in self.results["seguranca"]:
            total_items += 1
            if item["status"]:
                items_ok += 1

        # Calcular níveis extra
        for item in self.results["niveis_extra"]:
            total_items += 1
            if item["status"]:
                items_ok += 1

        # Calcular estrutura
        for item in self.results["estrutura"]:
            total_items += 1
            if item["status"]:
                items_ok += 1

        percentual = (items_ok / total_items * 100) if total_items > 0 else 0

        print(f"{'Item':<40} {'Status':<10}")
        print("-" * 50)

        for item in self.results["requisitos_obrigatorios"]:
            status = "✅ OK" if item["status"] else "❌ FALTA"
            print(f"{item['item']:<40} {status:<10}")

        for item in self.results["seguranca"]:
            status = "✅ OK" if item["status"] else "❌ FALTA"
            print(f"{item['item']:<40} {status:<10}")

        for item in self.results["niveis_extra"]:
            status = "✅ OK" if item["status"] else "⚠️ NÃO"
            print(f"{item['item']:<40} {status:<10}")

        print("-" * 50)
        print(f"\n{'Total de itens verificados:':<40} {total_items}")
        print(f"{'Itens corretos:':<40} {items_ok}")
        print(f"{'Percentual de conformidade:':<40} {percentual:.1f}%")

        if percentual >= 90:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✅ PARABÉNS! O projeto atende à maioria dos requisitos!{Colors.RESET}"
            )
        elif percentual >= 70:
            print(
                f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ O projeto atende aos requisitos básicos, mas faltam alguns extras.{Colors.RESET}"
            )
        else:
            print(
                f"\n{Colors.RED}{Colors.BOLD}❌ O projeto precisa de ajustes para atender aos requisitos.{Colors.RESET}"
            )

        print(f"\n{Colors.BOLD}📝 Recomendações finais:{Colors.RESET}")
        if percentual < 100:
            print("   - Verifique os itens marcados como 'FALTA' ou 'NÃO'")
            print("   - Execute a aplicação para testar todas as funcionalidades")
            print("   - Certifique-se de que os templates estão completos")
        else:
            print("   - Todos os requisitos foram atendidos! Parabéns!")

        print("\n" + "=" * 60)

    def executar(self):
        """Executa todas as verificações"""
        print_header("🔍 VERIFICADOR DO PROJETO HOTEL TRANSILVÂNIA")
        print_info(f"Verificando projeto em: {os.path.abspath(self.project_path)}")

        self.verificar_arquivos_estrutura()
        self.verificar_requisitos_obrigatorios()
        self.verificar_seguranca()
        self.verificar_niveis_extra()
        self.verificar_banco_dados()
        self.verificar_templates()
        self.verificar_questoes_reflexao()
        self.gerar_relatorio_final()


def main():
    # Determinar o caminho do projeto
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.getcwd()

    verificador = ProjetoVerificador(project_path)
    verificador.executar()


if __name__ == "__main__":
    main()
