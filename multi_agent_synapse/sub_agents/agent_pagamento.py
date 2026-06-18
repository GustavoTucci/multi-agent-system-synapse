import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_agent_synapse.tools.tool_agent_pagamento import (
    get_avg_delay_days,
    get_underpayment_rate,
    get_pos_dpd_history,
    get_active_pos_contracts,
)
from multi_agent_synapse.schemas.output_schema_pagamento import (
    RespostaPagamentoAgente,
)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY or GEMINI_API_KEY == "COLE_SUA_CHAVE_AQUI":
    raise EnvironmentError(
        "\n" + "="*60 +
        "\n  GEMINI_API_KEY nao configurada!" +
        "\n  Gere sua chave em: https://aistudio.google.com/apikey" +
        "\n  Cole-a no arquivo .env: GEMINI_API_KEY=AIza..." +
        "\n" + "="*60
    )
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "prj-data-ps-us")
DATASET = f"{PROJECT}.home_credit_default_risk"

print(f"[CONFIG] Projeto GCP : {PROJECT}")
print(f"[CONFIG] Dataset BQ  : {DATASET}")
print(f"[CONFIG] API Key     : {GEMINI_API_KEY[:8]}...\n")


root_agent = LlmAgent(
    name="agente_pagamentos",
    model="gemini-2.5-flash",
    description=(
        "Especialista em pontualidade e cobertura de parcelas. "
        "Analisa installments_payments e POS_CASH_balance."
    ),
    instruction="""
        Voce e um sub-agente especialista em analise de pagamentos.
        Seu objetivo e chamar as ferramentas, coletar as metricas ja calculadas
        e preencher o JSON de saida (RespostaPagamentoAgente).

        FLUXO OBRIGATORIO:
        1. Receba o sk_id_curr do cliente.
        2. Chame SEMPRE as quatro ferramentas disponiveis:
           - get_avg_delay_days(sk_id_curr)
           - get_underpayment_rate(sk_id_curr)
           - get_pos_dpd_history(sk_id_curr)
           - get_active_pos_contracts(sk_id_curr)

        COMO PREENCHER O JSON DE SAIDA:
        3. Mapeie cada retorno para o campo correto do schema:
           - get_avg_delay_days       -> campo "media_dias_atraso"
           - get_underpayment_rate    -> campo "pct_subpago"
           - get_pos_dpd_history     -> campo "pct_meses_dpd"
           - get_active_pos_contracts -> campo "contratos_ativos_pos"

        4. Se uma ferramenta retornar um campo "status" em vez de metrica,
           significa que nao ha dados. Preencha o campo correspondente como null
           e preencha o campo "status" do schema com a mensagem recebida.

        REGRAS:
        - Nao faca calculos. As ferramentas ja retornam metricas prontas.
        - Preencha o sk_id_curr com o ID do cliente consultado.
        - Nao adicione saudacoes ou conversas informais.
    """,
    tools=[
        FunctionTool(get_avg_delay_days),
        FunctionTool(get_underpayment_rate),
        FunctionTool(get_pos_dpd_history),
        FunctionTool(get_active_pos_contracts),
    ],
    output_schema=RespostaPagamentoAgente,
)


async def analisar_cliente(sk_id_curr: int) -> None:

    USER    = "analista"
    SESSION = f"sessao-{sk_id_curr}"

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="agente_pagamentos",
        user_id=USER,
        session_id=SESSION,
    )

    runner = Runner(
        agent=root_agent,
        app_name="agente_pagamentos",
        session_service=session_service,
    )

    pergunta = (
        f"Analise o perfil completo de pagamentos do cliente com ID {sk_id_curr}."
    )
    print(f"{'='*60}")
    print(f"  Analisando cliente SK_ID_CURR = {sk_id_curr}")
    print(f"{'='*60}\n")

    mensagem = types.Content(
        role="user",
        parts=[types.Part(text=pergunta)],
    )

    async for evento in runner.run_async(
        user_id=USER,
        session_id=SESSION,
        new_message=mensagem,
    ):
        if evento.content and evento.content.parts:
            for part in evento.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    print(f"  [TOOL] Ferramenta: {fc.name}(sk_id_curr={dict(fc.args).get('sk_id_curr', '?')})")
                elif hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    print(f"  [OK] Retorno de '{fr.name}': recebido")

        if evento.is_final_response():
            print("\n=== RELATORIO DO AGENTE ===\n")
            if evento.content and evento.content.parts:
                for part in evento.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text)
            else:
                print("[Agente finalizou sem texto de resposta]")


async def main():
    await analisar_cliente(sk_id_curr=100002)


if __name__ == "__main__":
    asyncio.run(main())