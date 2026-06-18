<<<<<<< HEAD
try:
    from .orquestrador_concierge import agent_concierge
except ImportError:
    agent_concierge = None  # orquestrador ainda não está pronto

=======
from .orquestrador_concierge import agent_concierge as root_agent
>>>>>>> 5309a87acea2a88288f9ee83913da0f57b19bb6c
