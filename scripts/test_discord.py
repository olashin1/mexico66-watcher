import httpx

from main import DISCORD_WEBHOOK_URL, send_notification


if not DISCORD_WEBHOOK_URL:
    raise SystemExit("FAIL | DISCORD_WEBHOOK_URL is not configured.")

try:
    with httpx.Client(timeout=httpx.Timeout(20, connect=10)) as client:
        send_notification(client)
except Exception as error:
    print(f"FAIL | Discord notification was not sent: {error}")
    raise SystemExit(1)

print("PASS | Discord notification sent.")
