import asyncio
import time
import traceback
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

from config import config
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

# Load env
load_dotenv()

APP_NAME = config.APP_NAME
USER_ID = "streamlit_user"
SESSION_ID = "streamlit_session"

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
    [
        research_agent,
        outline_agent,
        draft_agent,
        critic_agent,
        seo_agent,
        evaluation_agent,
    ],
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

def _run_agent(agent, prompt: str, agent_name: str) -> str:
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
    )

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
        app_logger.log_error(
            agent_name,
            "run_exception",
            error_msg,
            extra={"traceback": traceback.format_exc()},
        )
        return error_msg

    # REMOVED: duration = time.perf_counter() - start  <-- deleted from here

    final_text = ""
    # The agent actually "thinks" and generates text inside this loop
    for event in events:
        if hasattr(event, "is_final_response") and event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        final_text += part.text

    # MOVED HERE: Stop the timer after the work is done
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


# ------------------------------------------------------------
# TYPEWRITER ANIMATION EFFECT
# ------------------------------------------------------------
import time as _time


def typewriter(text: str, container, delay: float = 0.005):
    output = ""
    for char in text:
        output += char
        container.markdown(output)
        _time.sleep(delay)

# ------------------------------------------------------------
# REAL-TIME CONSOLE LOGGER
# ------------------------------------------------------------
class ConsoleLogger:
    def __init__(self, st_container):
        self.box = st_container.empty()
        self.logs = []

    def log(self, text: str):
        self.logs.append(f"> {text}")
        console_output = "```text\n" + "\n".join(self.logs[-80:]) + "\n```"
        self.box.markdown(console_output)
        _time.sleep(0.08)

    def separator(self):
        self.log("--------------------------------------------------")


# ------------------------------------------------------------
# Custom CSS for Enhanced UI
# ------------------------------------------------------------
def apply_custom_css():
    st.markdown("""
        <style>
        /* Minimal styling - preserve Streamlit defaults */
        .stExpander {
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
        }
        
        /* Subtle button enhancement */
        .stButton>button {
            border-radius: 6px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px);
        }
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            border-radius: 6px;
            padding: 0.6rem;
        }
        
        /* Download button styling */
        .stDownloadButton>button {
            border-radius: 6px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            margin: 0.5rem 0;
        }
        
        /* Code blocks */
        .stCodeBlock {
            border-radius: 6px;
        }
        
        /* Expander headers */
        .streamlit-expanderHeader {
            border-radius: 6px;
            font-weight: 500;
            padding: 0.75rem 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Streamlit page config
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Blog Production Agent",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Hero Section
st.markdown("""
    <div style='text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🧠✍️ AI Blog Production Agent Suite</h1>
        <p style='font-size: 1rem;'>
            Generate research-backed, structured, SEO-optimized blog posts using a 5-step multi-agent workflow.
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar — settings with enhanced styling
with st.sidebar:
    st.markdown("### ⚙️ Generation Settings")
    
    st.markdown("<div style='padding: 1rem 0;'>", unsafe_allow_html=True)
    
    tone = st.selectbox(
        "📢 Tone",
        ["Professional", "Casual", "Technical", "Beginner-friendly"],
        index=0,
    )

    target_audience = st.text_input(
        "🎯 Target Audience",
        value="beginner developers",
        placeholder="e.g. indie hackers, students, marketers",
    )

    word_count = st.slider(
        "📝 Target Word Count",
        min_value=600,
        max_value=3000,
        value=1500,
        step=100,
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    extra_instructions = st.text_area(
        "💡 Extra Instructions (optional)",
        placeholder="e.g. include code examples, avoid heavy math, use short paragraphs...",
        height=100,
    )

    st.markdown("---")

    with st.expander("✨ Interactive Options", expanded=False):
        enable_typewriter = st.toggle("⌨️ Typewriter animation", value=True)
        show_prompts = st.toggle("🔍 Show agent prompts", value=False)
        auto_expand_steps = st.toggle("📖 Auto-expand all steps", value=False)

    st.markdown("---")
    st.caption("Built with Google ADK + Gemini")

# Main input section with enhanced styling
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "💭 Enter your blog topic",
        placeholder="e.g. How multi-agent AI systems improve developer productivity",
        key="topic_input",
        label_visibility="visible"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_clicked = st.button("🚀 Generate", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs with icons
tab_final, tab_downloads, tab_steps, tab_console, tab_history = st.tabs(
    ["📄 Final Blog", "📦 Downloads", "🧩 Agent Steps", "📟 Console Logs", "🗂 History"]
)

with tab_final:
    final_subheader = st.markdown("### 📄 Final SEO-Optimized Blog")
    animated_box = st.empty()

with tab_downloads:
    if not st.session_state.get("latest_outputs"):
        st.info("💡 Generate a blog first to enable downloads.")

with tab_steps:
    if not st.session_state.get("latest_outputs"):
        st.info("💡 Agent step outputs will appear here after generation.")

with tab_console:
    console_placeholder = st.empty()
    console = ConsoleLogger(console_placeholder)

with tab_history:
    st.caption("📚 Previous runs are stored locally in this session.")

st.session_state.setdefault("run_history", [])
st.session_state.setdefault("latest_outputs", None)


def _record_history(entry: dict):
    history = st.session_state["run_history"]
    history.insert(0, entry)
    st.session_state["run_history"] = history[:10]


with tab_history:
    if not st.session_state["run_history"]:
        st.info("💡 Generate at least one article to see history here.")
    else:
        clear_history = st.button("🧹 Clear history", use_container_width=True)
        if clear_history:
            st.session_state["run_history"] = []
            st.rerun()
        for idx, run in enumerate(st.session_state["run_history"]):
            label = f"📝 {run['topic']} — {run['timestamp']}"
            with st.expander(label, expanded=(idx == 0)):
                st.markdown(run["final_text"])
                st.caption(
                    f"Tone: {run['tone']} • Audience: {run['audience']} • Words: {run['word_count']}"
                )


def build_base_context() -> str:
    return (
        f"Topic: {topic}\n"
        f"Tone: {tone}\n"
        f"Target Audience: {target_audience}\n"
        f"Target Word Count (approx): {word_count}\n"
        f"Extra Instructions: {extra_instructions}\n"
    )


st.session_state.setdefault("animated_done", False)

if generate_clicked:
    if not topic.strip():
        st.warning("⚠️ Please enter a topic first.")
    else:
        st.session_state["animated_done"] = False

        progress = st.progress(0)
        console.log("🚀 Starting multi-agent blog pipeline...")
        console.log(f"Topic: {topic}")
        console.separator()

        base_context = build_base_context()

        with tab_steps:
            st.markdown("### 🧩 Agent Step-by-Step Outputs")
            step1 = st.expander("1️⃣ 🔬 ResearchAgent Output", expanded=True)
            step2 = st.expander("2️⃣ 📋 OutlineAgent Output", expanded=auto_expand_steps)
            step3 = st.expander("3️⃣ ✍️ DraftAgent Output", expanded=auto_expand_steps)
            step4 = st.expander("4️⃣ 🧐 CriticAgent Output", expanded=auto_expand_steps)
            step5 = st.expander("5️⃣ 🚀 SEOAgent Output (Final)", expanded=True)
            step6 = st.expander("6️⃣ 📊 EvaluationAgent Output", expanded=True)

        # STEP 1: ResearchAgent
        progress.progress(10)
        console.log("🔍 [Step 1] ResearchAgent: collecting research...")
        research_prompt = base_context + "\nProvide structured research notes for this topic.\n"

        research_text = _run_agent(research_agent, research_prompt, "research_agent")
        research_text = truncate_text(research_text, max_chars=6000)
        with step1:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(research_prompt, language="markdown")
            st.markdown(research_text)

        console.log("✅ ResearchAgent completed.")
        console.separator()
        progress.progress(25)

        # STEP 2: OutlineAgent
        console.log("🧩 [Step 2] OutlineAgent: generating outline...")
        outline_prompt = (
            base_context
            + "\n\nUsing the following research, produce a detailed markdown outline:\n\n"
            + research_text
        )

        outline_text = _run_agent(outline_agent, outline_prompt, "outline_agent")
        outline_text = truncate_text(outline_text, max_chars=6000)
        with step2:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(outline_prompt, language="markdown")
            st.markdown(outline_text)

        console.log("✅ OutlineAgent completed.")
        console.separator()
        progress.progress(45)

        # STEP 3: DraftAgent
        console.log("✏️ [Step 3] DraftAgent: writing full draft...")
        draft_prompt = (
            base_context
            + "\n\nUsing this outline, write the full markdown blog draft:\n\n"
            + outline_text
        )

        draft_text = _run_agent(draft_agent, draft_prompt, "draft_agent")
        draft_text = truncate_text(draft_text, max_chars=9000)
        with step3:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(draft_prompt, language="markdown")
            st.markdown(draft_text)

        console.log("✅ DraftAgent completed.")
        console.separator()
        progress.progress(65)

        # STEP 4: CriticAgent
        console.log("🧐 [Step 4] CriticAgent: improving draft...")
        critic_prompt = (
            "Improve this draft for clarity, flow, correctness, and conciseness.\n\n"
            + draft_text
        )

        critic_text = _run_agent(critic_agent, critic_prompt, "critic_agent")
        critic_text = truncate_text(critic_text, max_chars=9000)
        with step4:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(critic_prompt, language="markdown")
            st.markdown(critic_text)

        console.log("✅ CriticAgent completed.")
        console.separator()
        progress.progress(80)

        # STEP 5: SEOAgent
        console.log("🚀 [Step 5] SEOAgent: generating SEO metadata + final blog...")
        seo_prompt = (
            "Using the improved blog below, generate:\n"
            "- SEO title\n"
            "- Meta description\n"
            "- URL slug\n"
            "- Keywords\n"
            "- Social caption\n"
            "and return the final improved blog markdown.\n\n"
            + critic_text
        )

        final_output_text = _run_agent(seo_agent, seo_prompt, "seo_agent")
        with step5:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(seo_prompt, language="markdown")
            st.markdown(final_output_text)

        console.log("✅ SEOAgent completed.")
        console.log("📊 [Step 6] EvaluationAgent: scoring final blog...")

        # STEP 6: EvaluationAgent
        eval_prompt = (
            "Evaluate this blog article and return JSON as specified in your instructions.\n\n"
            f"Tone: {tone}\nAudience: {target_audience}\nTarget Word Count: {word_count}\n\n"
            + final_output_text
        )
        eval_text = _run_agent(evaluation_agent, eval_prompt, "evaluation_agent")
        with step6:
            if show_prompts:
                st.markdown("**📝 Prompt Sent**")
                st.code(eval_prompt, language="markdown")
            st.code(eval_text, language="json")

        console.log("✅ EvaluationAgent completed.")
        console.log("🎉 Pipeline finished successfully.")
        console.separator()
        progress.progress(100)
        st.toast("🎉 Blog generation complete!", icon="✅")

        _record_history(
            {
                "topic": topic.strip(),
                "tone": tone,
                "audience": target_audience,
                "word_count": word_count,
                "final_text": final_output_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )

        st.session_state["latest_outputs"] = {
            "topic": topic.strip(),
            "tone": tone,
            "audience": target_audience,
            "word_count": word_count,
            "final_text": final_output_text,
            "research_text": research_text,
            "outline_text": outline_text,
            "draft_text": draft_text,
            "critic_text": critic_text,
            "eval_text": eval_text,
        }

        # Final Blog Tab — with typewriter animation
        with tab_final:
            st.markdown("### 📄 Final SEO-Optimized Blog")
            animated_box = st.empty()

            if enable_typewriter and not st.session_state.get("animated_done", False):
                typewriter(final_output_text, animated_box, delay=0.003)
                st.session_state["animated_done"] = True
            else:
                animated_box.markdown(final_output_text)
                st.session_state["animated_done"] = True

        # Downloads Tab
        with tab_downloads:
            st.markdown("### 📦 Download Your Blog")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="⬇️ Download as Markdown (.md)",
                    data=final_output_text,
                    file_name="blog_article.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="⬇️ Download as Text (.txt)",
                    data=final_output_text,
                    file_name="blog_article.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        with tab_console:
            st.caption("📡 Live logs from the 6-step agent pipeline.")


latest_outputs = st.session_state.get("latest_outputs")
if not generate_clicked and latest_outputs:
    final_text = latest_outputs.get("final_text", "")

    with tab_final:
        if final_text:
            animated_box.markdown(final_text)
        else:
            animated_box.info("💡 Run the generator to view your blog content.")

    with tab_downloads:
        st.markdown("### 📦 Download Your Blog")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download as Markdown (.md)",
                data=final_text,
                file_name="blog_article.md",
                mime="text/markdown",
                disabled=not final_text,
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="⬇️ Download as Text (.txt)",
                data=final_text,
                file_name="blog_article.txt",
                mime="text/plain",
                disabled=not final_text,
                use_container_width=True
            )

    with tab_steps:
        st.markdown("### 🧩 Agent Step-by-Step Outputs")
        step1 = st.expander("1️⃣ 🔬 ResearchAgent Output", expanded=True)
        step1.markdown(latest_outputs.get("research_text", "_No research output._"))

        step2 = st.expander("2️⃣ 📋 OutlineAgent Output", expanded=auto_expand_steps)
        step2.markdown(latest_outputs.get("outline_text", "_No outline output._"))

        step3 = st.expander("3️⃣ ✍️ DraftAgent Output", expanded=auto_expand_steps)
        step3.markdown(latest_outputs.get("draft_text", "_No draft output._"))

        step4 = st.expander("4️⃣ 🧐 CriticAgent Output", expanded=auto_expand_steps)
        step4.markdown(latest_outputs.get("critic_text", "_No critic output._"))

        step5 = st.expander("5️⃣ 🚀 SEOAgent Output (Final)", expanded=True)
        step5.markdown(final_text or "_No SEO output._")

        step6 = st.expander("6️⃣ 📊 EvaluationAgent Output", expanded=True)
        with step6:
            eval_text = latest_outputs.get("eval_text", "")
            if eval_text:
                st.code(eval_text, language="json")
            else:
                st.info("No evaluation output available.")
