# ربات تلگرام Grok — هاست روی Render

## فایل‌های پروژه
```
telegram-bot/
├── bot.py            ← کد اصلی
├── requirements.txt  ← کتابخانه‌ها
├── render.yaml       ← تنظیمات Render
└── README.md
```

---

## مرحله ۱ — ساخت ربات تلگرام
1. برو به @BotFather در تلگرام
2. بنویس /newbot و مراحل رو طی کن
3. Token رو کپی کن

## مرحله ۲ — Grok API Key
1. برو به console.x.ai
2. لاگین کن و از API Keys یه کلید بساز

## مرحله ۳ — گرفتن ADMIN_ID
1. برو به @userinfobot در تلگرام
2. /start بزن — عدد Id رو کپی کن

## مرحله ۴ — آپلود به GitHub
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

## مرحله ۵ — هاست روی Render
1. برو به render.com و ثبت‌نام کن
2. روی New + کلیک کن → Background Worker
3. ریپوی GitHub رو وصل کن
4. از بخش Environment این سه متغیر رو اضافه کن:
   - BOT_TOKEN
   - XAI_API_KEY
   - ADMIN_ID
5. روی Deploy کلیک کن ✅

---

## دستورات
| دستور | کار |
|-------|-----|
| /start | شروع |
| /reset | پاک کردن حافظه |
| /silence | خاموش کردن در گروه (فقط ادمین) |
| /unsilence | فعال کردن دوباره (فقط ادمین) |
