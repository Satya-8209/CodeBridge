"""
Slack Bolt bot for the Incident Memory Agent.

Slash command: /incident <service> | <error description>
Example: /incident payment-service | OOMKilled pod restarted 3 times

Requires:
  SLACK_BOT_TOKEN  — xoxb-...
  SLACK_APP_TOKEN  — xapp-... (Socket Mode)
"""
import sys
import os

# Add project root to path so backend imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from backend.config import settings

app = App(token=settings.slack_bot_token)

BACKEND_URL = "http://localhost:8000"


def call_alert(service: str, title: str, error_log: str) -> dict:
    """Call the FastAPI backend /alert endpoint."""
    resp = httpx.post(
        f"{BACKEND_URL}/alert",
        json={"title": title, "service": service, "severity": "high", "error_log": error_log},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


@app.command("/incident")
def incident_command(ack, body, respond):
    """
    /incident <service> | <error description>
    """
    ack()
    text = body.get("text", "").strip()
    if not text:
        respond("❌ Usage: `/incident <service> | <error description>`\nExample: `/incident payment-service | OOMKilled pod`")
        return

    # Parse: "payment-service | OOMKilled: container memory limit exceeded"
    if "|" in text:
        parts = text.split("|", 1)
        service = parts[0].strip()
        error = parts[1].strip()
    else:
        service = "unknown-service"
        error = text

    respond(f"🔍 Querying Hindsight memory for incidents similar to:\n*{error[:120]}*\n\n_Please wait..._")

    try:
        data = call_alert(service=service, title=error[:100], error_log=error)
    except Exception as e:
        respond(f"❌ Agent error: {e}")
        return

    count = len(data.get("similar_incidents", []))
    memory_icon = "🧠" if data.get("memory_hit") else "🆕"
    memory_label = (
        f"{memory_icon} *Memory: Found {count} similar past incident(s)*"
        if data.get("memory_hit")
        else "🆕 *Memory: No similar past incidents found — this may be new.*"
    )

    suggestion = data.get("suggestion", "No suggestion available.")

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"🚨 Incident Analysis — {service}", "emoji": True},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": memory_label},
        },
    ]

    # Show matched past incidents
    if count > 0:
        for i, inc in enumerate(data["similar_incidents"][:3], 1):
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Past Incident {i}:*\n```{inc['text'][:300]}```"},
            })

    blocks.append({"type": "divider"})
    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*💡 AI Suggestion:*\n{suggestion[:2900]}"},
    })
    blocks.append({
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": f"Alert ID: `{data['alert_id']}` · Powered by Hindsight + xAI Grok"}],
    })

    respond(blocks=blocks)


@app.event("app_mention")
def handle_mention(event, say):
    say("👋 Use `/incident <service> | <error log>` to get memory-powered incident analysis!")


if __name__ == "__main__":
    if not settings.slack_bot_token or not settings.slack_app_token:
        print("❌ Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env first")
        sys.exit(1)
    print("🤖 Starting Slack bot in Socket Mode...")
    handler = SocketModeHandler(app, settings.slack_app_token)
    handler.start()
