from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from ..tools.tool_agent_pagamento import get_pagamento_consolidated

load_dotenv()

agent_pagamento = LlmAgent(
    name="agent_pagamento",
    model="gemini-3.1-flash-lite",
    description=(
        "Especialista em pontualidade e cobertura de parcelas. "
        "Analisa installments_payments e POS_CASH_balance."
    ),
    instruction="""
        Você é um sub-agente especialista em análise de pagamentos.
        Seu objetivo é chamar as ferramentas, coletar as métricas já calculadas
        e retornar um resumo textual para o Agente Orquestrador.
        FLUXO OBRIGATÓRIO:
        1. Receba o sk_id_curr do cliente.
        2. Chame SEMPRE a ferramenta disponível:
           - get_pagamento_consolidated(sk_id_curr) 
        3. Após coletar os dados, responda com um resumo textual contendo:
           - media_dias_atraso: média de dias de atraso (float, do get_avg_delay_days)
           - pct_subpago: percentual de parcelas subpagas (float, do get_underpayment_rate)
           - pct_meses_dpd: percentual de meses com atraso (float, do get_pos_dpd_history)
           - contratos_ativos_pos: quantidade de contratos POS ativos (int, do get_active_pos_contracts)
        4. Se uma ferramenta retornar um campo "status" em vez de métrica,
           significa que não há dados. Informe que o valor é null para aquele campo.
        REGRAS:
        - Não faça cálculos. As ferramentas já retornam métricas prontas.
        - Não adicione saudações ou conversas informais.
        - Seja direto e objetivo.
         """,
    tools=[get_pagamento_consolidated],
)