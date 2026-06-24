from .orquestrador_concierge import agent_concierge

root_agent = agent_concierge

__all__ = ["root_agent", "agent_concierge"]

import typing
# Força o módulo typing a expor o Union globalmente para o servidor do Google ADK
typing.Union = typing.Union