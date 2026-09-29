"""
Core agent logic.
1. recall() — find semantically similar past incidents from Hindsight memory
2. Build a prompt with that memory context
3. Call xAI (Grok) via OpenAI-compatible API
4. Return structured suggestion
"""
import logging
from groq import Groq
from openai import OpenAI
from backend import hindsight_client as memory
from backend.config import settings
from backend.schemas import AgentResponse, MemoryMatch

logger = logging.getLogger(__name__)

def _get_llm_client():
    """Return the active LLM client based on config."""
    if settings.llm_provider == "groq" and settings.groq_api_key:
        return ("groq", Groq(api_key=settings.groq_api_key), settings.groq_model)
    elif settings.xai_api_key:
        return ("xai", OpenAI(api_key=settings.xai_api_key, base_url="https://api.x.ai/v1"), settings.xai_model)
    else:
        raise RuntimeError("No LLM API key configured. Set GROQ_API_KEY or XAI_API_KEY in .env")

SYSTEM_PROMPT = """You are an expert on-call DevOps assistant with access to a
memory bank of past production incidents your team has resolved.

When given a new alert, your job is to:
1. Analyze the current error and service context
2. Review similar past incidents retrieved from memory (if any)
3. State the MOST LIKELY root cause (be specific)
4. Give CONCRETE, numbered fix steps an engineer can execute right now

Rules:
- Be concise. Engineers are under time pressure.
- If memory has a directly matching past incident, lead with it.
- If no memory match, give your best technical analysis.
- Never say "I don't know" — always give a best hypothesis.
- Format your response in clear sections: Root Cause | Fix Steps | Watch For"""


def _build_prompt(title: str, service: str, error_log: str, similar: list[dict]) -> str:
    memory_section = ""
    if similar:
        memory_section = "\n\n### 🧠 Memory: Similar Past Incidents\n"
        for i, inc in enumerate(similar, 1):
            score_str = f" (similarity: {inc['score']:.2f})" if inc.get("score") else ""
            memory_section += f"\n**Past Incident {i}{score_str}:**\n{inc['text']}\n"
    else:
        memory_section = "\n\n### 🧠 Memory: No similar past incidents found yet.\n"

    return f"""## 🚨 New Alert

**Service:** {service}
**Alert:** {title}

**Error Log:**
```
{error_log[:1000]}
```
{memory_section}

Based on the above context, provide your root cause analysis and recommended fix steps."""


def handle_alert(title: str, service: str, error_log: str, alert_id: str) -> AgentResponse:
    """Main agent entry point — synchronous, safe for FastAPI with run_in_threadpool."""
    query = f"{title} {service} {error_log[:400]}"
    similar = memory.recall(query, top_k=5)

    prompt = _build_prompt(title, service, error_log, similar)

    try:
        provider, client, model = _get_llm_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        suggestion = response.choices[0].message.content or "No suggestion generated."
        logger.info("LLM response from %s using %s", provider, model)
    except Exception as e:
        logger.error("LLM API call failed: %s", e)
        suggestion = f"⚠️ LLM unavailable ({e}).\n\n**Memory context retrieved:**\n" + "\n\n".join(
            f"- {s['text'][:300]}" for s in similar
        )

    return AgentResponse(
        alert_id=alert_id,
        similar_incidents=[MemoryMatch(text=s["text"], score=s.get("score")) for s in similar],
        suggestion=suggestion,
        memory_hit=len(similar) > 0,
    )
