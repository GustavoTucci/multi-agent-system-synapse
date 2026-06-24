import pandas_gbq

PROJECT_ID = "prj-data-ps-us"
DATASET_ID = "home_credit_default_risk"
TABLE_ID = "previous_application"


def get_application_history(sk_id_curr):
    """
    Pedidos anteriores com status Approved/Refused/Canceled.
    Calcula taxa_aprovacao e razao_valor_aprovado.
    """

    sql = f"""
        SELECT
            NAME_CONTRACT_STATUS,
            AMT_APPLICATION,
            AMT_CREDIT
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
          AND NAME_CONTRACT_STATUS IN ('Approved', 'Refused', 'Canceled')
    """

    df = pandas_gbq.read_gbq(sql, project_id=PROJECT_ID)

    if df.empty:
        return {
            "taxa_aprovacao": 0.0,
            "razao_valor_aprovado": 0.0
        }

    total_pedidos = len(df)
    aprovados_df = df[df["NAME_CONTRACT_STATUS"] == "Approved"]

    taxa_aprovacao = len(aprovados_df) / total_pedidos

    valor_solicitado = df["AMT_APPLICATION"].fillna(0).sum()
    valor_aprovado = aprovados_df["AMT_CREDIT"].fillna(0).sum()

    razao_valor_aprovado = (
        valor_aprovado / valor_solicitado
        if valor_solicitado > 0
        else 0.0
    )

    return {
        "taxa_aprovacao": round(float(taxa_aprovacao), 4),
        "razao_valor_aprovado": round(float(razao_valor_aprovado), 4)
    }


def get_rejection_reasons(sk_id_curr):
    """
    Contagem de CODE_REJECT_REASON nos contratos recusados.
    """

    sql = f"""
        SELECT
            CODE_REJECT_REASON
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
          AND NAME_CONTRACT_STATUS = 'Refused'
    """

    df = pandas_gbq.read_gbq(sql, project_id=PROJECT_ID)

    if df.empty:
        return {"motivos_rejeicao": []}

    motivos_rejeicao = (
        df["CODE_REJECT_REASON"]
        .dropna()
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    return {"motivos_rejeicao": motivos_rejeicao}


def get_top_products(sk_id_curr):
    """
    Tipos de produto mais contratados pelo cliente.
    """

    sql = f"""
        SELECT
            NAME_CONTRACT_TYPE
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE SK_ID_CURR = {int(sk_id_curr)}
    """

    df = pandas_gbq.read_gbq(sql, project_id=PROJECT_ID)

    if df.empty:
        return {"produtos_top3": []}

    produtos_top3 = (
        df["NAME_CONTRACT_TYPE"]
        .dropna()
        .value_counts()
        .head(3)
        .index
        .tolist()
    )

    return {"produtos_top3": produtos_top3}

def get_contrato_consolidated(sk_id_curr):
    """
    Retorna todas as informações consolidadas de contratos anteriores do cliente.
    Combina taxa de aprovação, motivos de rejeição e produtos mais procurados.
    """
    historico = get_application_history(sk_id_curr)
    rejeicoes = get_rejection_reasons(sk_id_curr)
    produtos = get_top_products(sk_id_curr)
   
    return {
        "taxa_aprovacao": historico.get("taxa_aprovacao", 0.0),
        "razao_valor_aprovado": historico.get("razao_valor_aprovado", 0.0),
        "motivos_rejeicao": rejeicoes.get("motivos_rejeicao", []),
        "produtos_top3": produtos.get("produtos_top3", [])
    }