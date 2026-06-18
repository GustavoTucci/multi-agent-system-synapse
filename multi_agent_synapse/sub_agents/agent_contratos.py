import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from ..tools.tool_agent_contrato import (
    get_application_history,
    get_rejection_reasons,
    get_top_products,
)
from ..schemas.output_schema_contrato import RespostaContratos

load_dotenv()

if api_key := os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = api_key

agent_contratos = LlmAgent(
    model="gemini-2.5-flash",
    name="agente_contratos",
    description="Agente especialista em contratos internos anteriores do cliente.",
    instruction=(
        "Você é um analista especialista em contratos internos da Home Credit.\n"
        "Use a tabela previous_application no BigQuery.\n"
        "Sempre que o usuário informar um sk_id_curr, use obrigatoriamente as três ferramentas disponíveis.\n"
        "Use get_application_history para taxa_aprovacao e razao_valor_aprovado.\n"
        "Use get_rejection_reasons para motivos_rejeicao.\n"
        "Use get_top_products para produtos_top3.\n"
        "Não use ID fixo. Não invente dados.\n"
        "Todos os cálculos devem vir das ferramentas Python.\n"
        "Retorne apenas JSON no schema RespostaContratos."
    ),
    tools=[
        get_application_history,
        get_rejection_reasons,
        get_top_products,
    ],
    output_schema=RespostaContratos,
)
