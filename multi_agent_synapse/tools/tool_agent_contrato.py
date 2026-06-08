from pathlib import Path
import pandas as pd


CSV_PATH = Path(__file__).resolve().parent.parent / "previous_application.csv"


def carregar_tabela() -> pd.DataFrame:
    """
    Carrega a tabela previous_application.csv.
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo previous_application.csv não encontrado em: {CSV_PATH}"
        )

    return pd.read_csv(CSV_PATH)


def analisar_contratos(sk_id_curr: int) -> dict:
    """
    Analisa os contratos anteriores de um cliente usando o SK_ID_CURR.

    Use esta ferramenta quando o usuário pedir informações sobre contratos,
    propostas anteriores, aprovações, recusas, produtos contratados ou histórico
    interno do cliente na Home Credit.
    """

    df = carregar_tabela()

    cliente_df = df[df["SK_ID_CURR"] == sk_id_curr]

    if cliente_df.empty:
        return {
            "sk_id_curr": int(sk_id_curr),
            "sem_dados": True,
            "total_pedidos": 0,
            "taxa_aprovacao": 0.0,
            "motivos_rejeicao": [],
            "produtos_top3": [],
            "razao_valor_aprovado": 0.0,
        }

    total_pedidos = len(cliente_df)

    aprovados_df = cliente_df[
        cliente_df["NAME_CONTRACT_STATUS"] == "Approved"
    ]

    recusados_df = cliente_df[
        cliente_df["NAME_CONTRACT_STATUS"] == "Refused"
    ]

    taxa_aprovacao = len(aprovados_df) / total_pedidos

    motivos_rejeicao = (
        recusados_df["CODE_REJECT_REASON"]
        .dropna()
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    produtos_top3 = (
        cliente_df["NAME_CONTRACT_TYPE"]
        .dropna()
        .value_counts()
        .head(3)
        .index
        .tolist()
    )

    valor_solicitado = cliente_df["AMT_APPLICATION"].fillna(0).sum()
    valor_aprovado = aprovados_df["AMT_CREDIT"].fillna(0).sum()

    if valor_solicitado > 0:
        razao_valor_aprovado = valor_aprovado / valor_solicitado
    else:
        razao_valor_aprovado = 0.0

    return {
        "sk_id_curr": int(sk_id_curr),
        "sem_dados": False,
        "total_pedidos": int(total_pedidos),
        "taxa_aprovacao": round(float(taxa_aprovacao), 4),
        "motivos_rejeicao": motivos_rejeicao,
        "produtos_top3": produtos_top3,
        "razao_valor_aprovado": round(float(razao_valor_aprovado), 4),
    }
