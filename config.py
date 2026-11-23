import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Mas'ul xodimlarni ro'yxatdan o'tkazish uchun maxfiy kalit (xodimlar botda o'zlarini tasdiqlashlari uchun)
STAFF_SECRET_KEY = os.getenv("STAFF_SECRET_KEY", "staff2026")

CATEGORIES = {
    "xotin_qizlar": "👩‍💼 Xotin-qizlar maslahatchisi (Sultanova X.)",
    "inspektor_1": "🛡 Inspektor (Bekmuhammedov Donyor)",
    "inspektor_2": "🛡 Inspektor (Xudayberdiyev Behruz)"
}

CONTACTS_INFO = (
    "📞 <b>Universitet mas'ul xodimlarining to'g'ridan-to'g'ri kontaktlari:</b>\n\n"
    "👩‍💼 <b>Xotin-qizlar masalalari maslahatchisi:</b>\n"
    "• <b>F.I.Sh:</b> Sultanova Xilola Jamoliddinovna\n"
    "• <b>Telefon:</b> +998998127599\n"
    "• <b>Telegram:</b> @sultanova75\n\n"
    "🛡 <b>Profilaktika inspektori:</b>\n"
    "• <b>F.I.Sh:</b> Bekmuhammedov Donyor\n"
    "• <b>Telefon:</b> +998946221112\n\n"
    "🛡 <b>Profilaktika inspektori:</b>\n"
    "• <b>F.I.Sh:</b> Xudayberdiyev Behruz\n"
    "• <b>Telefon:</b> +998931750400\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⚙️ <b>Bot Admini (Texnik yordam va takliflar):</b>\n"
    "• <b>F.I.Sh:</b> Tursunov Muhammadmirzo\n"
    "• <b>Telefon:</b> +998939416282\n"
    "• <b>Telegram:</b> @DoN_CoDeR\n"
    "<i>(Botda texnik muammo bo'lsa yoki yaxshilash bo'yicha takliflaringiz bo'lsa murojaat qilishingiz mumkin)</i>\n\n"
    "🔒 <i>Eslatma: Agar shaxsingiz sir qolishini va to'liq maxfiy muloqot qilishni istasangiz, bot orqali xabar yo'llashingiz mumkin.</i>"
)

DB_NAME = str(BASE_DIR / "database.sqlite3")
