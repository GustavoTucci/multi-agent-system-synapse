import pandas as pd
import pandas_gbq
from ..schemas.output_schema_cartao import LimitUtilizationResponse, MinPaymentRateResponse, BalanceTrendResponse, BalanceRecord, ToolResponse

PROJETO = "prj-data-ps-us"
DATASET = "home_credit_default_risk"
TABELA  = "credit_card_balance"

 
def get_limit_utilization(sk_id_curr: int) -> LimitUtilizationResponse:
    """Busca os dados do banco e calcula o percentual médio de uso do limite do cartão."""
    
    query = f"""
        SELECT AMT_BALANCE, AMT_CREDIT_LIMIT_ACTUAL 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
    """
    try:
        # Executa a query no BigQuery e armazena em um DataFrame 
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        # Se a conexão falhar, retorna o erro envelopado no contrato Pydantic
        return LimitUtilizationResponse(sem_dados=True, mensagem=f"Erro ao conectar ao banco: {str(e)}")

    if df.empty:
        return LimitUtilizationResponse(sem_dados=True, mensagem="Cliente sem histórico de cartão.")
    
    # Evita divisão por zero filtrando apenas limites válidos 
    limite_valido = df['AMT_CREDIT_LIMIT_ACTUAL'] > 0
    if not limite_valido.any():
        return LimitUtilizationResponse(utilizacao_media=0.0)
        
    # Divide o saldo devedor pelo limite do cartão de cada mês, df.loc[linhas, colunas] -> localização no data frame
    utilizacao = df.loc[limite_valido, 'AMT_BALANCE'] / df.loc[limite_valido, 'AMT_CREDIT_LIMIT_ACTUAL']
    
    # Extrai a média de uso (.mean()) e responde no formato Pydantic esperado pela IA
    return LimitUtilizationResponse(utilizacao_media=float(utilizacao.mean()))


def get_min_payment_rate(sk_id_curr: int) -> MinPaymentRateResponse:
    """Calcula a proporção de meses em que o cliente ficou inadimplente/atrasou o cartão."""
                
    query = f"""
        SELECT SK_DPD 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
    """
    try:
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        return MinPaymentRateResponse(sem_dados=True, mensagem=f"Erro ao conectar ao banco: {str(e)}")

    if df.empty:
        return MinPaymentRateResponse(sem_dados=True, mensagem="Cliente sem histórico de cartão.")
    
    # Conta em quantos registros/meses a coluna 'Dias em Atraso' (SK_DPD) foi maior que zero
    meses_com_atraso = df[df['SK_DPD'] > 0].shape[0]
    
    # Pega o total de linhas retornadas (total de meses que o cliente tem de histórico)
    total_meses = df.shape[0]
    
    # Divide a quantidade de meses ruins pelo total para gerar a taxa (ex: 2 meses de 10 = 0.2 ou 20%)
    taxa = meses_com_atraso / total_meses if total_meses > 0 else 0.0
    
    return MinPaymentRateResponse(taxa_pagamento_minimo=taxa)


def get_balance_trend(sk_id_curr: int) -> BalanceTrendResponse:
    """Busca a tendência de evolução do saldo devedor nos últimos 6 meses cadastrados."""
            
    # Traz os meses ordenados do mais antigo (ex: -6) para o mais recente (ex: -1)
    query = f"""
        SELECT MONTHS_BALANCE, AMT_BALANCE 
        FROM `{PROJETO}.{DATASET}.{TABELA}`
        WHERE SK_ID_CURR = {sk_id_curr}
        ORDER BY MONTHS_BALANCE ASC
    """
    try:
        df = pandas_gbq.read_gbq(query, project_id=PROJETO)
    except Exception as e:
        return BalanceTrendResponse(sem_dados=True, mensagem=f"Erro ao conectar ao banco: {str(e)}")

    if df.empty:
        return BalanceTrendResponse(sem_dados=True, mensagem="Cliente sem histórico de cartão.")
    
    # O método .tail(6) extrai as últimas 6 linhas do DataFrame (ou seja, os 6 meses mais recentes)
    ultimos_meses = df.tail(6)
    
    # Converte as linhas do Pandas para uma lista de objetos 'BalanceRecord' (Pydantic)
    registros = [
        BalanceRecord(MONTHS_BALANCE=int(row['MONTHS_BALANCE']), AMT_BALANCE=float(row['AMT_BALANCE']))
        for _, row in ultimos_meses.iterrows()
    ]
    
    return BalanceTrendResponse(tendencia_saldo=registros)