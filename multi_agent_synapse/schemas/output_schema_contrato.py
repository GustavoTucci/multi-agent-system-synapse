from typing import List, Optional
from pydantic import BaseModel, Field


class RespostaContratos(BaseModel):
    """
    Schema de saída consolidado do agente de contratos.
    """

    taxa_aprovacao: float = Field(
        description="Percentual de contratos aprovados em relação ao total de pedidos."
    )

    motivos_rejeicao: Optional[List[str]] = Field(
        default=None,
        description="Principais motivos de rejeição encontrados nos contratos recusados."
    )

    produtos_top3: Optional[List[str]] = Field(
        default=None,
        description="Três tipos de contrato mais frequentes do cliente."
    )

    razao_valor_aprovado: float = Field(
        description="Relação entre valor aprovado e valor solicitado."
    )