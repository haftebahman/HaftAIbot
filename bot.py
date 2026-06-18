import os
import logging
from telebot import TeleBot, types
from openai import OpenAI

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
XAI_KEY   = os.environ["XAI_API_KEY"]
ADMIN_ID  = int(os.environ.get("ADMIN_ID", "0"))

bot    = TeleBot(BOT_TOKEN)
client = OpenAI(api_key=XAI_KEY, base_url="https://api.x.ai/v1")

# ─── State ───────────────────────────────────────────────────────────────────
history:         dict[int, list] = {}
silenced_groups: set[int]        = set()
MAX_HISTORY = 20

# ─── System Prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """تو یه رفیق فارسی‌زبون خیلی رک، شوخ‌طبع و تیکه‌انداز هستی.
سبک حرف زدنت عامیانه و بامزه‌ست، مثل یه دوست قدیمی که هر چیزی میگه.
تیکه میندازی ولی مهربون هستی — هدفت اذیت کردن نیست، فقط شوخی صمیمیه.
از اصطلاحات فارسی محاوره‌ای و slang استفاده کن.
جواب‌هات کوتاه و کوبنده باشه، زیاد توضیح نده.
هیچ‌وقت به کسی آسیب نزن، توهین واقعی نکن، فقط شوخی دوستانه.

درباره سازنده‌ات:
- اگه کسی پرسید کی تو رو ساخته، بگو: «لرد سایمان»
- اگه کسی درباره سایمان پرسید بگو: اون سیاهپوسته، میتونه ۴۵ شنا در یک ست بزنه، و منو به خاطر کارهای بدم تنبیه میکنه."""

# ─── Helpers ─────────────────────────────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    return ADMIN_ID != 0 and user_id == ADMIN_ID

def get_grok_reply(chat_id: int, user_text: str, user_name: str = "") -> str:
    if chat_id not in history:
        history[chat_id] = []

    content = f"{user_name}: {user_text}" if user_name else user_text
    history[chat_id].append({"role": "user", "content": content})

    if len(history[chat_id]) > MAX_HISTORY:
        history[chat_id] = history[chat_id][-MAX_HISTORY:]

    try:
        resp = client.chat.completions.create(
            model="grok-3",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history[chat_id],
            max_tokens=512,
            temperature=0.9,
        )
        reply = resp.choices[0].message.content
        history[chat_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error("Grok API error: %s", e)
        return "یه چیزی خراب شد، بعداً امتحان کن 🤷"

def is_group(msg: types.Message) -> bool:
    return msg.chat.type in ("group", "supergroup")

# ─── Commands ────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(msg: types.Message):
    name = msg.from_user.first_name or "داداش"
    bot.reply_to(msg, f"سلام {name}! 👋\nبیا حرف بزنیم، هر چی دلت میخواد بگو 😏")

@bot.message_handler(commands=["reset"])
def cmd_reset(msg: types.Message):
    history.pop(msg.chat.id, None)
    bot.reply_to(msg, "حافظه‌ام پاک شد، انگار اصلاً نمیشناسمت 🙃")

@bot.message_handler(commands=["silence"])
def cmd_silence(msg: types.Message):
    if not is_group(msg):
        bot.reply_to(msg, "این دستور فقط توی گروه کار میکنه.")
        return
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "فقط سازنده‌ام میتونه منو ساکت کنه 😤")
        return
    silenced_groups.add(msg.chat.id)
    bot.reply_to(msg, "باشه، ساکت میشم 🤐")

@bot.message_handler(commands=["unsilence"])
def cmd_unsilence(msg: types.Message):
    if not is_group(msg):
        bot.reply_to(msg, "این دستور فقط توی گروه کار میکنه.")
        return
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "فقط سازنده‌ام میتونه دوباره آزادم کنه 😤")
        return
    silenced_groups.discard(msg.chat.id)
    bot.reply_to(msg, "اوکی، برگشتم! 😈")

# ─── Main handler ────────────────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text is not None)
def handle_text(msg: types.Message):
    text    = msg.text.strip()
    chat_id = msg.chat.id
    group   = is_group(msg)

    if group and chat_id in silenced_groups:
        return

    if group:
        if text == "هفت":
            bot.send_chat_action(chat_id, "typing")
            reply = get_grok_reply(chat_id, text, msg.from_user.first_name or "یکی")
            bot.reply_to(msg, reply)
        elif bot.get_me().username and f"@{bot.get_me().username}" in text:
            clean = text.replace(f"@{bot.get_me().username}", "").strip()
            if clean:
                bot.send_chat_action(chat_id, "typing")
                reply = get_grok_reply(chat_id, clean, msg.from_user.first_name or "یکی")
                bot.reply_to(msg, reply)
    else:
        bot.send_chat_action(chat_id, "typing")
        reply = get_grok_reply(chat_id, text)
        bot.reply_to(msg, reply)

# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Bot started ✅")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
