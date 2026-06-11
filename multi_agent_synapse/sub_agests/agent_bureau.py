# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
from google.adk.agents import LlmAgent
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Importando as ferramentas da sua pasta tools (que está na raiz)
# pyrefly: ignore [missing-import]
from multi_agent_synapse.tools.tool_agent_bureal import get_active_credits, get_debt_summary, get_status_trend


load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')


agent_bureau = LlmAgent(
    model='gemini-2.5-flash',
    name='agent_bureau',
    description='Agente especialista em consultar o histórico de crédito e bureau do cliente.',
    instruction=(
        'Você é um analista especialista em histórico de crédito externo (Bureau).\n'
        'Sua função é analisar os dados consolidados do cliente fornecidos pelas ferramentas.\n'
        'Sempre que o usuário passar um sk_id_curr, use as ferramentas disponíveis para coletar informações.\n'
        'Retorne os resultados em um formato JSON claro e estruturado contendo a análise do perfil de risco.'
    ),
    tools=[get_active_credits, get_debt_summary, get_status_trend]
)