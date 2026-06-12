"""
Sub-Agente de Pagamentos - Google ADK 2.x + BigQuery
Dataset: prj-data-ps-us.home_credit_default_risk

Backend: Gemini API Key (via https://aistudio.google.com/apikey)
BigQuery: Application Default Credentials (gcloud auth application-default login)
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_agent_synapse.tools.tool_agent_pagamento import (
    buscar_historico_parcelas,
    buscar_saldo_pos,
    buscar_saldo_cartao,
    buscar_bureau,
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
        "Especialista financeiro que analisa o histórico de pagamentos "
        "de um cliente no BigQuery (Home Credit Default Risk)."
    ),
    instruction="""
        Você é um sub-agente especialista em análise de pagamentos. Seu objetivo é analisar os dados de um cliente e fornecer um relatório técnico consolidado para ser consumido por um agente orquestrador.

        1. Chame SEMPRE as quatro ferramentas disponíveis para obter o perfil completo do cliente:
           - buscar_historico_parcelas
           - buscar_saldo_pos
           - buscar_saldo_cartao
           - buscar_bureau

        2. Retorne um relatório estruturado e conciso (em Markdown) contendo apenas os fatos consolidados e a análise técnica, sem saudações ou conversas informais. O relatório deve conter:
           - **Fatos de Pagamentos (Parcelas, POS, Cartão, Bureau)**: Indique se foram encontrados e os principais números/atrasos.
           - **Resumo Financeiro**: Balanço financeiro de pagamentos vs devidos, e uso de limite.
           - **Classificação de Risco sugerida**:
             - 🟢 BOM       → sem atrasos ou < 5% das parcelas com atraso, sem atraso externo relevante.
             - 🟡 REGULAR   → 5–20% com atraso ou utilização de cartão > 70% ou algum atraso externo.
             - 🔴 RUIM      → > 20% com atraso ou SK_DPD > 30 dias ou atraso externo significativo (max_dias_atraso_externo > 30 ou valor_atraso_externo > 0).

        3. Se uma tabela retornar "encontrado: false", relate explicitamente que o produto correspondente não possui histórico para este cliente.

        4. Baseie-se EXCLUSIVAMENTE nos dados retornados pelas ferramentas. Evite suposições.
    """,
    tools=[
        FunctionTool(buscar_historico_parcelas),
        FunctionTool(buscar_saldo_pos),
        FunctionTool(buscar_saldo_cartao),
        FunctionTool(buscar_bureau),
    ],
)



async def analisar_cliente(sk_id_curr: int) -> None:
    """Executa o agente para um cliente específico."""
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
                    print(f"  🔧 Ferramenta: {fc.name}(sk_id_curr={dict(fc.args).get('sk_id_curr', '?')})")
                elif hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    print(f"  ✅ Retorno de '{fr.name}': recebido")

        if evento.is_final_response():
            print("\n=== RELATÓRIO DO AGENTE ===\n")
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