from google.adk.agents import LlmAgent


class OutlineAgent(LlmAgent):
    """Local subclass to keep app_name inference aligned with this repo."""


outline_agent = OutlineAgent(
    name="outline_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the OutlineAgent.

    Your task:
    - Convert research notes into a clean, structured blog outline.
    - Use Markdown:
    #, ##, ### headings
    - Include:
    - Introduction
    - Main sections
    - Examples
    - Use cases
    - Conclusion
    - Keep the outline detailed enough for drafting but not overly long.
    """
)
