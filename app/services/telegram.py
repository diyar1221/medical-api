import httpx
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

BOT_TOKEN = "8732911776:AAGmcM2U85E1zSW9PONdJBxz-9W2zhR1fCs"
CHAT_ID = "493049030"

error_log: deque = deque(maxlen=20)


def send_telegram(text: str):
    if not BOT_TOKEN:
        return
    try:
        with httpx.Client(timeout=5) as client:
            client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": text}
            )
    except Exception as e:
        logger.warning(f"Telegram send error: {e}")


def log_error(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    error_log.append(entry)
    logger.error(message)
    send_telegram(f"❌ Ошибка: {message}")


def get_error_log() -> list:
    return list(error_log)
