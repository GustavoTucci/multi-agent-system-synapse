
from google.adk.agents import LlmAgent

from multi_agent_synapse.tools.tool_agent_contrato import analisar_contratos


root_agent = LlmAgent(
    name="agente_contratos",
    model="gemini-2.5-flash",
    description="Agente especialista em contratos internos anteriores do cliente.",
    instruction="""
Você é um agente especialista em contratos internos.

Sua função é analisar contratos anteriores de clientes usando a tabela previous_application.csv.

Quando o usuário informar um SK_ID_CURR, use obrigatoriamente a ferramenta analisar_contratos.

Regras:
- Sempre use o SK_ID_CURR informado pelo usuário.
- Não use ID fixo.
- Não invente dados.
- Todos os cálculos devem vir da ferramenta Python analisar_contratos.
- Se o cliente não existir na tabela, retorne sem_dados como true.
- Responda em JSON simples.
""",
    tools=[analisar_contratos],
)