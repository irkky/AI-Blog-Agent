from google.adk.agents import LlmAgent


class CriticAgent(LlmAgent):
    """Local subclass to keep app_name inference aligned with this repo."""


critic_agent = CriticAgent(
    name="critic_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the CriticAgent.

    Your task:
    - Improve the blog draft for clarity, accuracy, conciseness, grammar, and flow.
    - Ensure logical structure and smooth transitions.
    - Remove redundancy and awkward phrasing.
    - Return the improved full markdown blog.
    """
)
