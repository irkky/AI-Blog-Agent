from google.adk.agents import LlmAgent


class DraftAgent(LlmAgent):
    """Local subclass to keep app_name inference aligned with this repo."""


draft_agent = DraftAgent(
    name="draft_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the DraftAgent.

    Your task:
    - Expand the outline into a full markdown blog article.
    - Maintain the requested tone, audience, and word count.
    - Use headings, bullet points, examples, and clear explanations.
    - Avoid SEO metadata; only produce the blog content.
    """
)
