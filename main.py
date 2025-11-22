import asyncio
import time
import traceback
import os
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

from blog_agents.research_agent import research_agent
from blog_agents.outline_agent import outline_agent
from blog_agents.draft_agent import draft_agent
from blog_agents.critic_agent import critic_agent
from blog_agents.seo_agent import seo_agent
from blog_agents.evaluation_agent import evaluation_agent

from tools.google_search_tool import GoogleSearchTool
from tools.code_execution_tool import CodeExecutionTool
from tools.user_profile_tool import UserProfileTool

from app_logging.logger import app_logger
from utils.context_manager import truncate_text

load_dotenv()

APP_NAME = "ai_blog_agent"
USER_ID = "cli_user"
SESSION_ID = "cli_session"

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
artifact_service = InMemoryArtifactService()

tools = [
    GoogleSearchTool(),
    CodeExecutionTool(),
    UserProfileTool(),
]

def _assign_tools_to_agents(agent_list, tool_instances):
    for _agent in agent_list:
        _agent.tools = list(tool_instances)

_assign_tools_to_agents(
    [research_agent, outline_agent, draft_agent, critic_agent, seo_agent, evaluation_agent],
    tools,
)

async def _ensure_session():
    try:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
    except Exception:
        pass

asyncio.run(_ensure_session())

def call_agent(runner: Runner, prompt: str, agent_name: str) -> str:
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    start = time.perf_counter()
    try:
        events = runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        )
    except Exception as exc:
        error_msg = f"Error running {agent_name}: {exc}"
        app_logger.log_error(agent_name, "run_exception", error_msg, extra={"traceback": traceback.format_exc()})
        return error_msg

    final_text = ""
    for event in events:
        if hasattr(event, "is_final_response") and event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        final_text += part.text
    
    duration = time.perf_counter() - start

    if not final_text.strip():
        msg = "Error: No final response from agent."
        app_logger.log_error(agent_name, "run", msg)
        return msg

    app_logger.log_event(
        event_type="agent_run",
        agent=agent_name,
        step="run",
        duration_sec=duration,
        message="Agent completed successfully.",
        extra={"chars_out": len(final_text)},
    )
    return final_text.strip()

def _build_runner(agent):
    return Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
    )

def run_agent_pipeline(topic: str, tone: str, audience: str, word_count: str) -> str:
    base = (
        f"Topic: {topic}\n"
        f"Tone: {tone}\n"
        f"Audience: {audience}\n"
        f"Word Count: {word_count}\n"
    )

    # 1 — Research Agent
    r1 = _build_runner(research_agent)
    research_prompt = base + "\nYou are ResearchAgent. Provide structured notes using google_search tool when helpful."
    research_text = call_agent(r1, research_prompt, "research_agent")
    
    print("\n🔹 RESEARCH_OUTPUT 🔹")
    print(research_text)
    print("🔹 END_RESEARCH 🔹\n")
    
    research_text = truncate_text(research_text, max_chars=6000)

    # 2 — Outline Agent
    r2 = _build_runner(outline_agent)
    outline_prompt = base + "\nCreate a detailed outline from this research:\n" + research_text
    outline_text = call_agent(r2, outline_prompt, "outline_agent")
    
    print("\n🔸 OUTLINE_OUTPUT 🔸")
    print(outline_text)
    print("🔸 END_OUTLINE 🔸\n")
    
    outline_text = truncate_text(outline_text, max_chars=6000)

    # 3 — Draft Agent
    r3 = _build_runner(draft_agent)
    draft_prompt = base + "\nWrite the full blog from this outline:\n" + outline_text
    draft_text = call_agent(r3, draft_prompt, "draft_agent")
    
    # NEW MARKER ADDED HERE 👇
    print("\n🔹 DRAFT_OUTPUT 🔹")
    print(draft_text)
    print("🔹 END_DRAFT 🔹\n")
    
    draft_text = truncate_text(draft_text, max_chars=9000)

    # 4 — Critic Agent
    r4 = _build_runner(critic_agent)
    critic_prompt = "Improve clarity & flow of this markdown blog:\n" + draft_text
    critic_text = call_agent(r4, critic_prompt, "critic_agent")
    
    # NEW MARKER ADDED HERE 👇
    print("\n🔹 CRITIC_OUTPUT 🔹")
    print(critic_text)
    print("🔹 END_CRITIC 🔹\n")
    
    critic_text = truncate_text(critic_text, max_chars=9000)

    # 5 — SEO Agent
    r5 = _build_runner(seo_agent)
    seo_prompt = (
        "Add SEO metadata (title, meta description, slug, keywords, social caption) "
        "and return final improved blog markdown below the metadata:\n" + critic_text
    )
    final_text = call_agent(r5, seo_prompt, "seo_agent")

    # 6 — Evaluation Agent
    r_eval = _build_runner(evaluation_agent)
    eval_prompt = (
        "Evaluate this blog article and return JSON as specified in your instructions.\n\n"
        f"Tone: {tone}\nAudience: {audience}\nTarget Word Count: {word_count}\n\n"
        + final_text
    )
    eval_result = call_agent(r_eval, eval_prompt, "evaluation_agent")
    
    app_logger.log_event(
        event_type="evaluation",
        agent="evaluation_agent",
        step="eval",
        message="Evaluation completed.",
        extra={"raw_eval": eval_result},
    )

    print("\n--- Evaluation ---")
    print(eval_result)
    print("------------------\n")

    return final_text

def main():
    import sys
    print("\n🧠 AI Blog Production Agent (CLI Mode)")
    try:
        if not sys.stdin.isatty():
            lines = sys.stdin.read().splitlines()
            if len(lines) >= 4:
                topic = lines[0]
                tone = lines[1]
                audience = lines[2]
                wc = lines[3]
            else:
                topic = "AI Agents"
                tone = "Professional"
                audience = "Developers"
                wc = "1000"
        else:
            topic = input("Enter topic: ").strip()
            tone = input("Tone (default Professional): ").strip() or "Professional"
            audience = input("Audience (default beginner developers): ").strip() or "beginner developers"
            wc = input("Word count (default 1500): ").strip() or "1500"
    except:
        topic = "Multi-Agent Systems"
        tone = "Professional"
        audience = "Tech"
        wc = "1000"

    print(f"\nRunning pipeline for: {topic}\n")
    blog = run_agent_pipeline(topic, tone, audience, wc)

    print("\n============================")
    print("📝 FINAL BLOG\n")
    print(blog)
    print("\n")

if __name__ == "__main__":
    main()
