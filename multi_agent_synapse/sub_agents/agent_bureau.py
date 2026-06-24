from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from ..tools.tool_agent_bureau import get_bureau_consolidated

load_dotenv()

agent_bureau = LlmAgent(
    model='gemini-3.1-flash-lite',
    name='agent_bureau',
    description='Agente especialista em consultar o histórico de crédito e bureau do cliente.',
    instruction="""
        Você é um analista especialista em histórico de crédito externo (Bureau).

        Sua função é analisar os dados consolidados do cliente fornecidos pelas ferramentas.

        Sempre que receber um sk_id_curr, chame a ferramenta disponível:
        - get_bureau_consolidated(sk_id_curr) — para obter a quantidade de créditos ativos, a dívida total e máximo de dias em atraso e 
        para obter a tendência de status.

        Após coletar os dados, responda com um resumo textual contendo:
        - creditos_ativos: quantidade de créditos ativos (int)
        - divida_total: soma da dívida ativa (float)
        - max_dias_atraso: maior número de dias em atraso (int)
        - tendencia_status: tendência (Melhorando, Estável, Piorando ou Indeterminada)
        Se não houver dados, indique que o valor é null para cada campo sem dados.
        Não adicione saudações. Seja direto e objetivo.
    """,
    tools=[get_bureau_consolidated],
)