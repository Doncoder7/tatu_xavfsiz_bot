# Universitet Talaba Qizlari Qo'llab-quvvatlash Boti (UniSupportBot)

Ushbu bot universitetning talaba qizlari muammo va murojaatlarini qabul qilib, ularni tegishli mas'ul xodimlarga (inspektor, xotin-qizlar masalalari, psixolog, tyutor) yo'naltiruvchi va ikki tomonlama maxfiy muloqotni ta'minlovchi tizimdir.

## 🚀 Imkoniyatlar:
- **100% Maxfiylik:** Talaba va mas'ul shaxs bir-birlarining shaxsiy Telegram profilini ko'rmaydi.
- **Multimediya qo'llab-quvvatlash:** Matn, ovozli xabar (audio), fotosuratlar va hujjatlar orqali murojaat qilish.
- **Mas'ul xodimlarni tanlash:** Talaba o'z xohishi bilan qaysi sohaga (inspektor, psixolog, xotin-qizlar, tyutor) murojaat qilishini tanlaydi.
- **Relay-chat:** Mas'ul xodim Telegramda xabarga "Reply" qilib javob yozsa, javob bot orqali avtomatik talabaga yetkaziladi.
- **Murojaatni yakunlash:** Muammo hal bo'lgach, "Muloqotni yakunlash" tugmasi orqali ticket yopiladi.

## 🛠 O'rnatish va Ishga tushirish:
1. `.env` fayliga bot tokenini yozing:
   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   STAFF_SECRET_KEY=staff2026
   ```
2. Botni ishga tushiring:
   ```bash
   python main.py
   ```
