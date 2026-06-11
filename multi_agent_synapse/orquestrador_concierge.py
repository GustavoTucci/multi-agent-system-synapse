from google.adk.agents.llm_agent import Agent

agent_concierge = Agent(
    model='gemini-2.5-flash',
    name='agent_concierge',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
