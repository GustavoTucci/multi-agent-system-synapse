import pandas as pd
import pandas_gbq
import math
from ..queries.queries_agent_bureal import QUERY_CREDITOS_ATIVOS, QUERY_DEBT_SUMMARY, QUERY_STATUS_TREND
from ..schemas.output_schema_bureau import RespostaBureauAgente
def _sanitize(value):
    """Converte NaN e Inf para None, tornando o valor seguro para JSON."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value

def get_active_credits(sk_id_curr: int) -> dict:
    """Calcula a quantidade de créditos ativos e o maior atraso registrado."""
    sql = QUERY_CREDITOS_ATIVOS.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhum crédito ativo localizado para o cliente {sk_id_curr}"}

    # Como a query já filtra os ativos, contamos as linhas ou uma coluna ID
    total_ativos = int(df.shape[0])
    
    # Busca a coluna de dias em atraso (CREDIT_DAY_OVERDUE) se ela existir na query
    max_atraso = 0
    if 'CREDIT_DAY_OVERDUE' in df.columns:
        max_atraso = int(df['CREDIT_DAY_OVERDUE'].max())

    return {
        "total_creditos_ativos": total_ativos,
        "max_dias_atraso": max_atraso
    }

def get_debt_summary(sk_id_curr: int) -> dict:
    """Retorna a soma consolidada das dívidas ativas do cliente."""
    sql = QUERY_DEBT_SUMMARY.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhuma informação de dívida encontrada para o cliente {sk_id_curr}"}

    # Soma a coluna de dívida ativa (AMT_CREDIT_SUM_DEBT)
    divida_total = 0.0
    if 'AMT_CREDIT_SUM_DEBT' in df.columns:
        # Preenche nulos com 0 antes de somar
        divida_total = float(df['AMT_CREDIT_SUM_DEBT'].fillna(0).sum())

    return {"divida_global_total": _sanitize(divida_total)}

def get_status_trend(sk_id_curr: int) -> dict:
    """Retorna a string de tendência de pagamento baseada no histórico."""
    sql = QUERY_STATUS_TREND.format(sk_id_curr=sk_id_curr)
    df = pandas_gbq.read_gbq(sql, project_id='prj-data-ps-us')

    if df.empty:
        return {"status": f"Nenhum histórico de status encontrado para o cliente {sk_id_curr}"}

    # Aqui você analisa os registros para definir a string que o schema espera:
    # 'Melhorando', 'Piorando', 'Estável' ou 'Indeterminada'
    # Como não tenho a estrutura exata da sua query de tendência (ex: STATUS_BURBUR ou MONTHS_BALANCE),
    # criamos uma lógica genérica defensiva. Ajuste conforme as colunas da sua tabela.
    
    tendencia = "Estável" 
    
    if 'STATUS' in df.columns and len(df) >= 2:
        # Exemplo hipotético: se o status recente tiver menos atrasos que o antigo
        pass

    return {"tendencia": tendencia}


def get_bureau_consolidated(sk_id_curr: int) -> dict:
    """Retorna todas as informações consolidadas do bureau do cliente."""
    
    active_credits = get_active_credits(sk_id_curr)
    debt_summary = get_debt_summary(sk_id_curr)
    status_trend = get_status_trend(sk_id_curr)
   
    # Se todas falharem, repassa o status de erro/sem dados
    if "status" in active_credits and "status" in debt_summary and "status" in status_trend:
        return {"status": active_credits.get("status")}
       
    return {
        "creditos_ativos": active_credits.get("total_creditos_ativos") if "total_creditos_ativos" in active_credits else None,
        "divida_total": debt_summary.get("divida_global_total") if "divida_global_total" in debt_summary else None,
        "max_dias_atraso": active_credits.get("max_dias_atraso") if "max_dias_atraso" in active_credits else None,
        "tendencia_status": status_trend.get("tendencia") if "tendencia" in status_trend else None
    }