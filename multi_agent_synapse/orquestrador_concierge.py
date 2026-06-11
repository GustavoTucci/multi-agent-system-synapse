from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session

# Importar agents
from .sub_agents import agent_bureau, agent_payment, agent_card, agent_contracts
from .tools import get_client_profile
from .schemas import ConsolidatedReport


concierge_agent = LlmAgent(
    name="agent_concierge",
    model="gemini-2.5-flash",
    description="Agente orquestrador do sistema multi-agente de análise de crédito Home Credit.",
    instruction="""
    Você é o orquestrador principal do sistema multi-agente de análise de crédito Home Credit.

    SUA MISSÃO
    1. Receber uma pergunta + SK_ID_CURR do usuário
    2. Ler o perfil base do cliente com get_client_profile(sk_id)
    3. Decidir quais especialistas acionar BASEADO SEMÂNTICAMENTE na pergunta
    4. Consolidar todas as respostas em um JSON único (ConsolidatedReport)
    5. Gerar uma narrativa analítica sintetizando os dados

    QUANDO USAR CADA ESPECIALISTA

    - agent_bureau: Perguntas sobre "créditos externos", "bureau", "outras instituições"
    - agent_pagamentos: Perguntas sobre "atraso", "pagamento", "parcelas", "pontualidade"
    - agent_cartao: Perguntas sobre "cartão", "limite", "fatura", "utilização"
    - agent_contratos: Perguntas sobre "histórico de contratos", "aprovação", "rejeição"

    COMO CONSOLIDAR

    Retorne UM JSON com o schema ConsolidatedReport:
    {
    "sk_id_curr": <int>,
    "perfil": {...},
    "bureau": <JSON do bureau_agent> ou null,
    "pagamento": <JSON do payment_agent> ou null,
    "cartao": <JSON do card_agent> ou null,
    "contratos": <JSON do contracts_agent> ou null,
    "agentes_acionados": ["bureau", "pagamento", ...],
    "narrativa": "<sintese>"
    }

    ## REGRAS

    1. Não criar lógica de roteamento em Python (if/else)
    2. Roteamento SEMÂNTICO pela system_instruction + docstrings
    3. Sempre retornar JSON estruturado (output_schema)
    """,
    tools=[get_client_profile, ...], 
    output_schema=ConsolidatedReport,
)

# ======================
# RUNNER + SESSION
# ======================

def run_concierge(sk_id: int, pergunta: str):
    """
    Ponto de entrada da aplicação.
    """
    session_id = f"client_{sk_id}"
    session = Session(
        app_id="home_credit_multi_agent",
        session_id=session_id,
    )
    
    runner = Runner(
        agent=concierge_agent,
        app_id="home_credit_multi_agent",
        max_turns=10,
    )
    
    event = runner.run(
        session=session,
        user_message=f"SK_ID_CURR: {sk_id}\n\nPergunta: {pergunta}",
    )
    
    return event.value  # ConsolidatedReport (Pydantic)
