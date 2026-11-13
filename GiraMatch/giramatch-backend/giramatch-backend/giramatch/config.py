"""Parâmetros do GiraMatch.

Os pesos e as taxas de economia são PARÂMETROS ILUSTRATIVOS para o protótipo.
Devem ser calibrados com dados históricos de contratações compartilhadas antes
de qualquer uso real.
"""
import os

# Banco: DATABASE_URL (PostgreSQL, usado na hospedagem) ou arquivo SQLite local.
DB_PATH = os.environ.get("DATABASE_URL") or os.environ.get("GIRAMATCH_DB", "giramatch.db")
# Na hospedagem a plataforma define PORT e a API precisa escutar em 0.0.0.0.
HOST = os.environ.get("GIRAMATCH_HOST") or ("0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
PORT = int(os.environ.get("PORT") or os.environ.get("GIRAMATCH_PORT", "8000"))

# Carrega os dados fictícios de demonstração se o banco estiver vazio (1 = sim).
# Útil na hospedagem, onde não há terminal. Desligue quando for usar dados reais.
DEMO_SE_VAZIO = os.environ.get("GIRAMATCH_DEMO_SE_VAZIO", "0") == "1"

# Origem permitida para o front-end (CORS). "*" libera tudo — só para o protótipo.
CORS_ORIGEM = os.environ.get("GIRAMATCH_CORS", "*")

# Validade do token de acesso
TOKEN_HORAS = 12

# Protecao contra tentativas de login em sequencia (F-003). Contadores em memoria do processo.
LOGIN_MAX_FALHAS = int(os.environ.get("GIRAMATCH_LOGIN_MAX_FALHAS", "8"))        # por IP + e-mail
LOGIN_MAX_FALHAS_IP = int(os.environ.get("GIRAMATCH_LOGIN_MAX_FALHAS_IP", "30"))  # por IP
LOGIN_JANELA_S = int(os.environ.get("GIRAMATCH_LOGIN_JANELA_S", "300"))           # janela e bloqueio, em segundos

# Usuários criados/atualizados a cada subida da API: "ORGAO|Nome|email|senha;ORGAO|Nome|email|senha"
USUARIOS_ENV = os.environ.get("GIRAMATCH_USUARIOS", "")

# --- Motor de match -------------------------------------------------------
LIMIAR_SCORE = 60            # abaixo disso, o par não vira sugestão
SIMILARIDADE_MINIMA = 0.40   # descrições menos parecidas que isso são descartadas

PESOS = {
    "similaridade": 0.45,    # é o mesmo objeto?
    "tempo": 0.25,           # os meses previstos no PCA estão próximos?
    "territorio": 0.15,      # mesmo município/estado?
    "sustentabilidade": 0.15,  # critérios sustentáveis em comum?
}
JANELA_MESES = 6             # diferença de meses a partir da qual a nota de tempo é zero
BONUS_CONTRATOS_ALINHADOS = 5  # serviços cujos contratos atuais terminam juntos (até 90 dias)

# Economia de escala estimada: base + fator * log2(volume_total / maior_quantidade)
ECONOMIA_BASE = 0.06
ECONOMIA_FATOR = 0.08
ECONOMIA_MAX = 0.20

# Valor até o qual a LC 123/2006 (art. 48, I) prevê licitação exclusiva para ME/EPP
LIMITE_ME_EPP = 80_000.00
