import json
import warnings
import re
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.tools import transfer_to_agent

from .schemas import ConsolidatedReport
from .sub_agents import agent_bureau, agent_cartao, agent_contratos
from .tools import get_client_profile

# Oculta os logs amarelos do Pydantic/ADK no terminal
warnings.filterwarnings("ignore", category=UserWarning)

agent_concierge = LlmAgent(
    name="agent_concierge",
    model="gemini-2.5-flash",
    description="Agente orquestrador do sistema multi-agente de análise de crédito Home Credit.",
    instruction="""
    Você é o orquestrador principal do sistema multi-agente de análise de crédito Home Credit.

    SUA MISSÃO
    1. Receber uma pergunta e o SK_ID_CURR do usuário.
    2. Chamar OBRIGATORIAMENTE a ferramenta `get_client_profile` utilizando o ID fornecido para obter os dados do "perfil" base do cliente.
    3. Analisar semanticamente a pergunta do usuário para decidir qual ou quais sub-agentes especialistas devem ser consultados.
    4. Consolidar os dados coletados de todos os sub-agentes consultados no formato estruturado (ConsolidatedReport).
    5. Gerar uma narrativa analítica correlacionando os dados coletados e traçando o perfil de risco do cliente.
6. Caso o SK_ID_CURR fornecido não seja encontrado, retornar uma mensagem de erro "Cliente não encontrado, digite outro ID".
    
    QUANDO ACIONAR CADA ESPECIALISTA (Usando transfer_to_agent)
    - agent_bureau: Perguntas sobre "créditos externos", "bureau", "outras instituições".
    - agent_cartao: Perguntas sobre "cartão", "limite", "fatura", "utilização".
    - agent_contratos: Perguntas sobre "histórico de contratos", "aprovação", "rejeição".
    
    *Nota: Se o usuário perguntar algo sobre "atraso", "pagamento" ou "parcelas" (antigo agent_pagamentos), lembre-se que este sub-agente está indisponível. Reporte os dados como null para esse bloco.*

    REGRAS CRÍTICAS DE RETORNO em JSON
    1. Você DEVE preencher o schema 'ConsolidatedReport' por completo.
    2. Para qualquer bloco de sub-agente especialista que NÃO FOI acionado na sessão, você deve definir o valor daquela chave inteira estritamente como `null`.
    3. O bloco 'perfil' sempre deve vir preenchido com o retorno da ferramenta básica `get_client_profile`.
    4. No campo 'agentes_acionados', liste estritamente as tags textuais dos agentes que você chamou (ex: ['bureau', 'cartao']).
    5. Não use lógica de controle if/else em Python para roteamento. Deixe que sua inteligência semântica gerencie as transferências de estado.
    """,
    tools=[get_client_profile, transfer_to_agent],
    output_schema=ConsolidatedReport
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
        agent=agent_concierge,
        app_id="home_credit_multi_agent",
        max_turns=10,
    )

    event = runner.run(
        session=session,
        user_message=f"SK_ID_CURR: {sk_id}\n\nPergunta: {pergunta}",
    )

    # Captura o retorno do Gemini, formata como JSON e joga na tela
    if event and event.value:
        report = event.value
        print("\n" + "=" * 20 + " RELATÓRIO CONSOLIDADO GERADO " + "=" * 20)
        print(report.model_dump_json(indent=2))
        print("=" * 68 + "\n")
        return report

    return event.value


# ==============================================================================
# INTERFACE DEPROMPT DINÂMICO (Para quando rodar via script Python direto)
# ==============================================================================
if __name__ == "__main__":
    print("Modo Interativo Local Iniciado.")
    print("Digite 'sair' para encerrar.\n")
    
    while True:
        entrada = input("[user]: ")
        if entrada.lower() == "sair":
            break
            
        # Tenta extrair qualquer sequência de 6 dígitos (o ID do cliente) da sua pergunta
        match = re.search(r'\b\d{6}\b', entrada)
        if not match:
            print("[Sistema]: Por favor, informe o ID do cliente com 6 dígitos na pergunta (Ex: 217517).\n")
            continue
            
        id_extraido = int(match.group())
        run_concierge(sk_id=id_extraido, pergunta=entrada)