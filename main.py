import os, re, asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]

KEYWORDS = os.environ.get("KEYWORDS","дизайн|дизайнер|дизайнера|дизайнеру|дизайнеров|дизайнеры|дизайнерка|дизайнерки|карточка|карточки|карточек|инфографика|баннер|лого|логотип|логотипы|брендбук|фирменный стиль")
NEGATIVE = os.environ.get("NEGATIVE","")
ONLY_PUBLIC = os.environ.get("ONLY_PUBLIC","false").lower() == "true"

kw_re = re.compile(KEYWORDS, re.I) if KEYWORDS else None
neg_re = re.compile(NEGATIVE, re.I) if NEGATIVE else None

def fits(txt:str) -> bool:
    if not txt: return False
    if kw_re and not kw_re.search(txt): return False
    if neg_re and neg_re.search(txt): return False
    return True

async def run():
    async with TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH) as cli:
        since = datetime.now(timezone.utc) - timedelta(minutes=6)
        async for dialog in cli.iter_dialogs():
            ent = dialog.entity
            if ONLY_PUBLIC and not getattr(ent, "username", None):
                continue
            async for msg in cli.iter_messages(ent, limit=200, min_date=since):
                text = msg.message or ""
                if not fits(text):
                    continue
                chat_title = getattr(ent, "title", None) or getattr(ent, "username", None) or str(getattr(ent,"id",""))
                link = f"https://t.me/{ent.username}/{msg.id}" if getattr(ent,"username",None) else None
                out = (
                    "🛰 Найдено совпадение\n"
                    f"Чат: {chat_title}\n"
                    f"Дата (UTC): {msg.date.replace(tzinfo=timezone.utc).isoformat(timespec='seconds')}\n"
                    + (f"Ссылка: {link}\n" if link else "")
                    + "—\n" + text[:1000]
                )
                await cli.send_message("me", out)

if __name__ == "__main__":
    asyncio.run(run())