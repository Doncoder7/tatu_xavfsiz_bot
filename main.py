import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import database as db
from config import BOT_TOKEN
from handlers import student, staff

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def handle_ping(request):
    return web.Response(text="TATU Xavfsiz Bot is active and running! 🚀")

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/ping", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Keep-alive veb-server ishga tushdi: http://0.0.0.0:{port}")

async def main():
    if not BOT_TOKEN:
        print("\n" + "="*60)
        print("DIQQAT: BOT_TOKEN belgilanmagan!")
        print(".env fayliga yoki config.py fayliga bot tokenini joylashtiring.")
        print("="*60 + "\n")
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(staff.router)
    dp.include_router(student.router)

    # Render uchun veb-serverni ishga tushirish (Render port tekshiruvi uchun shart)
    await start_web_server()

    print("\n" + "="*60)
    print("✅ BOT ISHGA TUSHDI VA XABARLARNI KUTMOQDA!")
    print("Telegramdan botingizga /start buyrug'ini yuborib tekshirishingiz mumkin.")
    print("="*60 + "\n")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
