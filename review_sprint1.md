# Relatório de Desenvolvimento do Projeto — Sprint 1 (Semanas 1 e 2)

## Semana 1: Fundação e Infraestrutura

A primeira semana foi dedicada a construir a base sólida do projeto. O objetivo era garantir que toda a infraestrutura de dados e o ambiente de desenvolvimento do Google ADK estivessem rodando.

Configuramos o ambiente virtual, instalando a venv, as bibliotecas Google-adk, Pandas, Pandas gbq, validamos um agente minimalista com ferramentas funcionais e conectamos com o Big Query por meio da extensão Google Cloud Data Agent Kit.

Carregamos as 7 tabelas do dataset via Pandas, mapeamos a integridade dos dados e realizar joins relacionais manuais via SK_ID_CURR e fizemos o EDA básico.

**O Algoritmo compute, o LLM raciocina:** Provamos com sucesso que as funções Python conseguem extrair, limpar e agregar os dados relacionais do Home Credit, entregando para o modelo apenas o dado mastigado.

---

## Semana 2: Divisão de Tarefas e Especialização

Na segunda semana o objetivo central da segunda semana foi a divisão de tarefas para o desenvolvimento. Cada integrante da equipe assumiu o papel de "dono" de um ecossistema de dados, codificando as ferramentas em Python (tool) e configurando os respectivos sub-agentes especialistas (LlmAgent).

Aplicamos o tratamento de erros para dados ausentes, clientes com dados zerados ou nulos e forçar saídas estruturadas. Fizemos testes unitários isolados para validar a execução individual de cada agente com diferentes IDs de clientes contrastantes.

### 1. Agente de Bureau Externo (`LlmAgent`)

* **Tabelas Relacionadas:** `bureau.csv` e `bureau_balance.csv`
* **Implementação de Tools:** Desenvolveu e homologou com sucesso três ferramentas críticas:
  * `get_active_credits(sk_id)`: Filtra e lista créditos ativos em outras instituições.
  * `get_debt_summary(sk_id)`: Executa a soma da dívida ativa externa e captura o teto histórico de dias em atraso.
  * `get_status_trend(sk_id)`: Realiza o join relacional complexo de dois níveis com a `bureau_balance` e calcula a tendência mensal do cliente.
* **Resultado do Teste:** O agente conseguiu ler o comportamento externo do cliente e traduzir em texto se o perfil estava melhorando ou piorando financeiramente.

No agente Bureau, desenvolvi ferramentas para análise do histórico de crédito dos clientes utilizando dados do Home Credit, incluindo a consulta de créditos ativos, o cálculo da dívida total e dos atrasos históricos, além da identificação de tendências de comportamento financeiro a partir do histórico de pagamentos. As principais dificuldades foram entender a estrutura e o relacionamento entre as tabelas `bureau` e `bureau_balance`, interpretar corretamente os códigos de status de crédito, construir consultas SQL com agregações e regras de negócio, tratar os dados para retorno em JSON compatível com o ADK e resolver problemas de integração das novas tools ao agente, como importações, registro das ferramentas e validação dos dados disponíveis para cada cliente.

### 2. Agente de Pagamentos (`LlmAgent`)

* **Tabelas Relacionadas:** `installments_payments.csv` e `POS_CASH_balance.csv`
* **Implementação de Tools:** Garantiu a aplicação estrita da regra matemática do projeto através de quatro ferramentas:
  * `buscar_historico_parcelas(sk_id)`: Calcula a média de dias e a quantidade de parcelas atrasadas pelo cliente.
  * `buscar_saldo_cartao(sk_id)`: Avalia o uso limite de faturas pendentes de cartão de crédito.
  * `buscar_saldo_pos(sk_id)`: Verifica o status de atrasos de contratos financeiros.
   * `buscar_bureau(sk_id)`: Consultar orgãos externos para checar se o cliente possí dividas institucionais.


* **Resultado do Teste:** O agente processou milhões de linhas de parcelas puramente em Python, entregando métricas agregadas sem estressar o LLM com dados brutos.

O objetivo principal do agente é consolidar o histórico financeiro e o comportamento de crédito do cliente para prever o risco de inadimplência. Para isso, foram integradas ferramentas que consultam o BigQuery em busca de dados de parcelas pagas, saldos de contratos POS, utilização de limite de cartão de crédito e registros de burocras externos (Bureau). Durante a construção, surgiram alguns pontos de atenção, como problemas de importação e, principalmente, limitações de tokens e da chave de API do Gemini. Apesar desses desafios, foi possível concluir o agente com sucesso.

### 3. Agente de Cartão de Crédito (`LlmAgent`)

* **Tabela Relacionada:** `credit_card_balance.csv`
* **Ferramentas Desenvolvidas:**
  * `get_limit_utilization`: calcula o percentual médio de uso do limite do cartão.
  * `get_min_payment_rate`: Meses em que o cliente ficou inadimplente/atrasou o cartão.
  * `get_balance_trend`: Evolução do saldo devedor nos últimos 6 meses cadastrados
* **Tratamento de Dados Ausentes:** Implementou uma lógica de tratamento de exceções. Caso o `SK_ID_CURR` consultado não possua registros de cartão de crédito no banco de dados, a tool intercepta o erro e retorna um dicionário estruturado: `{"sem_dados": true}`. E caso o `SK_ID_CURR` for inexistente irá retornar que o "Cliente não está cadastrado". E caso o cliente possua dados e histórico no Big Query, será retornado um JSON com a média do uso do limite do cartão, se o cliente ficou inadimplente/atrasou o cartão e também buscará a evolução do saldo devedor nos últimos 6 meses.

### 4. Agente de Contratos Internos (`LlmAgent`)

* **Tabela Relacionada:** `previous_application.csv`

Dessa forma, a análise é feita apenas com os registros do cliente informado.

#### Tools do Agente de Contratos:
* `carregar_tabela()`: Essa tool é responsável por carregar a tabela `previous_application.csv`. Ela permite que os dados da base sejam lidos e utilizados pelas demais tools.
* `filtrar_cliente(sk_id_curr)`: Essa tool filtra os dados da tabela usando o `SK_ID_CURR` informado pelo usuário. Ela garante que a análise seja feita somente com os contratos do cliente consultado.
* `get_application_history(sk_id_curr)`: Essa tool analisa o histórico geral de contratos anteriores do cliente. Ela calcula: total de pedidos; total de contratos aprovados; total de contratos recusados; taxa de aprovação. A taxa de aprovação é calculada pela relação entre contratos aprovados e total de pedidos.
* `get_rejection_reasons(sk_id_curr)`: Essa tool identifica os principais motivos de rejeição dos contratos recusados.
* `get_top_products(sk_id_curr)`: Essa tool identifica os tipos de contrato mais frequentes do cliente.
* `get_approved_amount_ratio(sk_id_curr)`: Essa tool calcula a razão entre o valor aprovado e o valor solicitado. A regra utilizada é: `soma do valor aprovado nos contratos aprovados / soma do valor solicitado em todos os contratos anteriores`.
* `analisar_contratos(sk_id_curr)`: Essa é a tool principal do agente. Ela chama as outras tools, junta os resultados e monta a resposta final. Sua função principal é consolidar toda a análise dos contratos anteriores do cliente, reunindo: taxa de aprovação; motivos de rejeição; produtos mais frequentes; razão entre valor aprovado e solicitado.

#### Resposta Final do Agente:
No final, o agente retorna uma resposta estruturada em JSON com os principais resultados da análise. O formato esperado é:

```json
{
  "taxa_aprovacao": 0.6,
  "motivos_rejeicao": ["LIMIT"],
  "produtos_top3": [
    "Consumer loans",
    "Cash loans",
    "Revolving loans"
  ],
  "razao_valor_aprovado": 0.6786
} 
```

---

## Status Atual
Toda a matemática do risco de crédito rodou de forma determinística no Python.

Isso nos dá a segurança necessária para iniciar a Semana 3 hoje, onde o foco do projeto passa a ser a **Orquestração desses sub-agentes pelo Agente Concierge utilizando AgentTool**, em paralelo a isso configuraremos o **Runner** e as **memórias através da Session**.
