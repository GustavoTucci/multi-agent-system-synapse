from pydantic import BaseModel, Field

class RespostaContratos(BaseModel):
    taxa_aprovacao: float | None = Field(
        default=None,
        description="Percentual de contratos aprovados."
    )
    motivos_rejeicao: list[str] | None = Field(
        default=None,
        description="Principais motivos de rejeição. OBRIGATÓRIO ser uma lista de strings, ex: ['LIMIT']."
    )
    produtos_top3: list[str] | None = Field(
        default=None,
        description="Os três tipos de contrato mais frequentes."
    )
    razao_valor_aprovado: float | None = Field(
        default=None,
        description="Relação entre valor aprovado e valor solicitado."
    )

# 2. SE VOCÊ TIVER ESTA CLASSE ABAIXO NO SEU ARQUIVO, MUDE EXATAMENTE PARA ISSO:
class SetModelResponseParams(BaseModel):
    dados: RespostaContratos | str | None = Field(default=None)

# Avise o Pydantic para reconstruir o modelo usando o escopo correto
SetModelResponseParams.model_rebuild()