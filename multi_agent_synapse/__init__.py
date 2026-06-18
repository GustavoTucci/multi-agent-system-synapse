try:
    from .orquestrador_concierge import agent_concierge
except ImportError:
    agent_concierge = None  # orquestrador ainda não está pronto

