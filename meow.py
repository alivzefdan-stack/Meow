import asyncio
from telethon import TelegramClient, events

# اطلاعات اپلیکیشن شما
API_ID = 31787166
API_HASH = 'bed8cc6a8af3a44dfce7371b03c18747'

# ایجاد کلاینت تلگرام
client = TelegramClient('command_panel_session', API_ID, API_HASH)

# تنظیمات اولیه سلف‌بات
config = {
    "target_chat": "تنظیم نشده",  # گروه مقصد
    "interval": 5,                 # زمان به دقیقه
    "is_active": False             # وضعیت روشن/خاموش
}

# تابع بررسی اینکه پیام در Saved Messages (چت با خود شخص) فرستاده شده یا خیر
def is_saved_messages(event):
    return event.is_private and event.chat_id == client.loop.run_until_complete(client.get_me()).id

# ۱. دستور نمایش پنل متنی و وضعیت
@client.on(events.NewMessage(outgoing=True, pattern=r'^/panel$'))
async def show_panel(event):
    if event.is_private and event.chat_id == (await client.get_me()).id:
        status_text = "🟢 روشن (در حال ارسال)" if config["is_active"] else "🔴 خاموش"
        panel_message = (
            f"🎛 **پنل مدیریتی کامندی سلف‌بات میو**\n\n"
            f"📍 گروه مقصد: `{config['target_chat']}`\n"
            f"⏱️ فاصله زمانی: `{config['interval']} دقیقه`\n"
            f"⚙️ وضعیت: {status_text}\n\n"
            f"**دستورات کنترل:**\n"
            f"▫️ `/setchat [آیدی یا یوزرنیم گروه]`\n"
            f"▫️ `/settime [عدد به دقیقه]`\n"
            f"▫️ `/on` (روشن کردن)\n"
            f"▫️ `/off` (خاموش کردن)\n"
            f"▫️ `/panel` (نمایش این منو)"
        )
        await event.respond(panel_message)

# ۲. دستور تنظیم گروه مقصد
@client.on(events.NewMessage(outgoing=True, pattern=r'^/setchat\s+(.+)'))
async def set_chat(event):
    if event.is_private and event.chat_id == (await client.get_me()).id:
        new_chat = event.pattern_match.group(1).strip()
        config["target_chat"] = new_chat
        await event.respond(f"✅ گروه مقصد با موفقیت روی این آیدی تنظیم شد:\n`{new_chat}`")

# ۳. دستور تنظیم تایم (به دقیقه)
@client.on(events.NewMessage(outgoing=True, pattern=r'^/settime\s+(\d+)$'))
async def set_time(event):
    if event.is_private and event.chat_id == (await client.get_me()).id:
        new_time = int(event.pattern_match.group(1))
        config["interval"] = new_time
        await event.respond(f"⏱️ فاصله زمانی ارسال پیام به `{new_time} دقیقه` تغییر یافت.")

# ۴. دستور روشن کردن بات
@client.on(events.NewMessage(outgoing=True, pattern=r'^/on$'))
async def turn_on(event):
    if event.is_private and event.chat_id == (await client.get_me()).id:
        if config["target_chat"] == "تنظیم نشده":
            await event.respond("❌ ابتدا باید گروه مقصد را با دستور `/setchat` مشخص کنید!")
        else:
            config["is_active"] = True
            await event.respond("🟢 سلف‌بات با موفقیت **روشن** شد.")

# ۵. دستور خاموش کردن بات
@client.on(events.NewMessage(outgoing=True, pattern=r'^/off$'))
async def turn_off(event):
    if event.is_private and event.chat_id == (await client.get_me()).id:
        config["is_active"] = False
        await event.respond("🔴 سلف‌بات **خاموش** شد.")

# ۶. لوپ اصلی ارسال پیام «میو» در گروه مشخص شده
async def sender_loop():
    await client.start()
    print("سلف‌بات کامندی آماده به کار است...")
    
    while True:
        if config["is_active"] and config["target_chat"] != "تنظیم نشده":
            try:
                await client.send_message(config["target_chat"], 'میو')
                print(f"پیام 'میو' با موفقیت به {config['target_chat']} ارسال شد.")
            except Exception as e:
                print(f"خطا در ارسال پیام: {e}")
        
        # تبدیل دقیقه به ثانیه
        wait_seconds = config["interval"] * 60
        await asyncio.sleep(wait_seconds)

with client:
    client.loop.create_task(sender_loop())
    client.run_until_disconnected()
