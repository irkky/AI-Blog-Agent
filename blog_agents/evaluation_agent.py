from google.adk.agents import LlmAgent


class EvaluationAgent(LlmAgent):
    """Agent that scores the final blog on clarity, SEO, structure, and usefulness."""


evaluation_agent = EvaluationAgent(
    name="evaluation_agent",
    model="gemini-2.5-flash",
    instruction="""
You are EvaluationAgent.

You will receive:
- A blog article in markdown.
- Optional metadata (tone, audience, word count).

Your job:
1. Evaluate the article on:
   - clarity (1-10)
   - structure (1-10)
   - SEO strength (1-10)
   - usefulness for the target audience (1-10)
   - overall score (1-10)

2. Return a short JSON object ONLY, with this shape:
{
  "clarity": 0-10,
  "structure": 0-10,
  "seo": 0-10,
  "usefulness": 0-10,
  "overall": 0-10,
  "comments": "one or two sentences of feedback"
}

Do NOT include any extra text outside the JSON.
""",
)
