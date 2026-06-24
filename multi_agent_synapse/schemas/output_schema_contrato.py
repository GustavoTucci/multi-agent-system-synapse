from pydantic import BaseModel, Field

# 1. Defina o esquema que você quer usar para validar os contratos depois
class RespostaContratos(BaseModel):
    taxa_aprovacao: float | None = Field(
        default=None,
        description="Percentual de contratos aprovados."
    )
    motivos_rejeicao: list[str] | None = Field(
        default=None,
        description="Principais motivos de rejeição."
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

# O PONTO CHAVE: Avise o Pydantic para reconstruir o modelo usando o escopo correto
SetModelResponseParams.model_rebuild()