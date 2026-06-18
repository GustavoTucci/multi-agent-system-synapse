import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from ..tools.tool_agent_bureal import get_active_credits, get_debt_summary, get_status_trend
from ..schemas.output_schema_bureal import RespostaBureauAgente

load_dotenv()
if api_key := os.getenv('GOOGLE_API_KEY'):
    os.environ['GOOGLE_API_KEY'] = api_key

agent_bureau = LlmAgent(
    model='gemini-2.5-flash',
    name='agent_bureau',
    description='Agente especialista em consultar o histórico de crédito e bureau do cliente.',
    instruction=(
        'Você é um analista especialista em histórico de crédito externo (Bureau).\n'
        'Sua função é analisar os dados consolidados do cliente fornecidos pelas ferramentas.\n'
        'Sempre que o usuário passar um sk_id_curr, use as ferramentas disponíveis para coletar informações.\n'
        'Retorne os resultados no formato JSON do output_schema.'
    ),
    tools=[get_active_credits, get_debt_summary, get_status_trend],
    output_schema=RespostaBureauAgente
)