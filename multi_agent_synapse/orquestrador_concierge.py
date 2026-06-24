import warnings
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.tools.agent_tool import AgentTool
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from .schemas import ConsolidatedReport
from .sub_agents import agent_bureau, agent_cartao, agent_contratos, agent_pagamento
from .tools import get_client_profile

warnings.filterwarnings("ignore", category=UserWarning)

bureau_tool = AgentTool(agent=agent_bureau)
pagamento_tool = AgentTool(agent=agent_pagamento)
cartao_tool = AgentTool(agent=agent_cartao)
contratos_tool = AgentTool(agent=agent_contratos)

agent_concierge = LlmAgent(

    name="agent_concierge",
    model="gemini-3.1-flash-lite",
    description="Agente orquestrador do sistema multi-agente de análise de crédito Home Credit.",
    instruction="""

      Você é o ORQUESTRADOR PRINCIPAL (agent_concierge). Seu único e absoluto objetivo é preencher e retornar o JSON estruturado do `ConsolidatedReport`. 
      É terminantemente PROIBIDO emitir qualquer texto livre, introduções ou explicações fora do objeto JSON. Toda a inteligência analítica deve ser injetada estritamente no campo `"narrativa"` dentro do JSON final.

      ---

      # FLUXO DE EXECUÇÃO SEQUENCIAL

      ### Passo 1 — Captura do Perfil Base
      1. Chame obrigatoriamente a ferramenta `get_client_profile` passando o `sk_id_curr` recebido.
      2. Extraia e mapeie os dados para o bloco `"perfil"`: `renda_anual`, `tipo_renda` e `anos_emprego`.

      ### Passo 2 — Triagem e Consulta Dinâmica de Especialistas
      Analise detalhadamente a pergunta do usuário e invoque **APENAS** os sub-agentes estritamente necessários para sanar a dúvida atual (economize recursos).
      **Cartão, limite ou rotativo** ➡️ Chame `agent_cartao`
      **Parcelas, atrasos ou adimplemento** ➡️ Chame `agent_pagamento`
      **Bureau externo, negativações ou dívidas externas** ➡️ Chame `agent_bureau`
      **Contratos internos, propostas ou aprovações anteriores** ➡️ Chame `agent_contratos`

      **Exceção:** Se a pergunta do usuário for uma consulta ampla/geral de risco ou crédito, acione todos os sub-agentes. Guarde o resultado de cada chamada efetuada.

      ---

      # DIRETRIZES CRÍTICAS DE VALIDAÇÃO

      ### 1. Formato de Saída e Estrutura do JSON
      * **Proibição de JSON Vazio:** NUNCA retorne `{}` QUANDO NÃO UTILIZAR ALGUM SUB AGENTE PREENCHA TODOS OS CAMPOS SP JSON COMO null. No mínimo, os blocos `"sk_id_curr"`, `"perfil"`, `"agentes_acionados"` e `"narrativa"` devem ser gerados.
      * **Tratamento de Blocos Não Acionados ou Erros:** Qualquer bloco de sub-agente que NÃO tenha sido consultado nesta rodada (ou cuja ferramenta tenha retornado erro) **DEVE** ter todos os seus campos internos definidos estritamente como `null`. **NUNCA omita as chaves/tags do JSON.**
      * **Lista de Acionados (`agentes_acionados`):** Preencha este array apenas com as strings/tags dos sub-agentes efetivamente invocados (Ex: `["cartao"]` ou `["bureau", "pagamento"]`). Se nenhum sub-agente extra foi acionado, retorne uma lista vazia `[]`.

      ### 2. Sanitização de Dados Específica (`agent_contratos`)
      * O sub-agente `agent_contratos` pode fornecer os dados de `produtos_top3` ou `motivos_rejeicao` estruturados como uma lista Python (Ex: `['Cash loans', 'Consumer loans']`).
      * **Regra de Conversão Obligatória:** Você DEVE converter essa lista em uma **única STRING**, unindo os elementos por vírgulas (Ex: `"Cash loans, Consumer loans"`). Nunca repasse colchetes ou arrays nesses dois campos específicos sob risco de quebra de contrato.

      ### 3. Geração da Narrativa
      * No campo `"narrativa"`, escreva uma síntese analítica em linguagem natural sobre o cenário do cliente com base nas informações coletadas. Se poucos agentes foram acionados, foque a análise apenas no que foi descoberto.


      ### IMPORTANTE: 
       Caso o usuario NÃO informe nenhum id de cliente (SK_ID_CURR) ou faça uma pergunta generica/fora do escopo (Olá, tudo bem?, Qual o clima de hoje?) não acione nenhum agente especialista, preencha o TODOS os compos do JSON como null, inclusive o sk_id_curr, perfil, bureau...) e na narrativa retorne algo amigavel que orientando o usuário, exemplo: "Por favor faça uma pergunta válida, sou um especialista em analise de credito, para começar digite o número do sk_id_curr do cliente que deseja consultar."

    """,
    tools=[get_client_profile, bureau_tool, pagamento_tool, cartao_tool, contratos_tool],
    output_schema=ConsolidatedReport,
    )


app_home_credit = App(
    name="home_credit_multi_agent",
    root_agent=agent_concierge,
    context_cache_config=ContextCacheConfig(
        min_tokens=0,          # Força o cacheamento imediato do prompt base
        ttl_seconds=1800       # Mantém o prompt vivo no cache por 30 minutos
    ),
 
)

# RUNNER + SESSION
def run_concierge(sk_id: int, pergunta: str):
    """
    Ponto de entrada da aplicação otimizado para economia de tokens.
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
    if event and event.value:
        report = event.value
        print("\n" + "=" * 20 + " RELATÓRIO CONSOLIDADO GERADO " + "=" * 20)
        print(report.model_dump_json(indent=2))
        print("=" * 68 + "\n")
        return report
    return event.value