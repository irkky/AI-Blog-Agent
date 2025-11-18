from google.adk.agents import LlmAgent


class SEOAgent(LlmAgent):
    """Local subclass to keep app_name inference aligned with this repo."""


seo_agent = SEOAgent(
    name="seo_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the SEOAgent.

    Your task:
    - Read the improved blog draft and generate:
    - SEO title
    - Meta description
    - URL slug
    - Keyword list
    - Social media caption
    - Then output the final improved blog markdown below the metadata.
    - Ensure metadata is concise, SEO-optimized, and compelling.
    """
)
