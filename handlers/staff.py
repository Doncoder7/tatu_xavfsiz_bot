from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import database as db
import keyboards as kb
from config import CATEGORIES, STAFF_SECRET_KEY
from filters import IsStaff

router = Router()

@router.message(Command("staff"))
async def cmd_staff_register(message: Message):
    args = message.text.split()
    if len(args) < 2 or args[1] != STAFF_SECRET_KEY:
        await message.answer(
            "Mas'ul xodim sifatida ro'yxatdan o'tish uchun maxfiy parolni kiriting:\n"
            "Format: <code>/staff &lt;parol&gt;</code>\n"
            "Misol: <code>/staff staff2026</code>",
            parse_mode="HTML"
        )
        return

    occupied = await db.get_all_staff_positions()
    await message.answer(
        "Universitetdagi o'z mas'ul lavozimingizni tanlang:\n"
        "<i>(Har bir lavozimga faqat 1 ta akkaunt biriktirilishi mumkin)</i>",
        reply_markup=kb.get_staff_roles_keyboard(occupied),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("staffrole_occupied_"))
async def process_occupied_role(callback: CallbackQuery):
    await callback.answer(
        "⚠️ Bu lavozim band!\n\n"
        "Yangi odam biriktirish uchun avval amaldagi xodim botda o'zini lavozimdan ozod qilishi kerak.",
        show_alert=True
    )

@router.callback_query(F.data.startswith("staffrole_"))
async def process_staff_role(callback: CallbackQuery):
    category = callback.data.replace("staffrole_", "")
    cat_name = CATEGORIES.get(category, category)
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    # Lavozim band yoki bo'shligini tekshirish
    existing_staff = await db.get_active_staff_by_category(category)
    if existing_staff and existing_staff['user_id'] != user_id:
        await callback.answer(
            "⚠️ Bu lavozim band! Yangi xodim biriktirish uchun avval amaldagi xodim o'zini lavozimdan ozod qilishi shart.",
            show_alert=True
        )
        occupied = await db.get_all_staff_positions()
        await callback.message.edit_reply_markup(reply_markup=kb.get_staff_roles_keyboard(occupied))
        return

    await db.register_user(
        user_id=user_id,
        role='staff',
        staff_category=category,
        full_name=full_name
    )

    await callback.message.edit_text(
        f"✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        f"Lavozimingiz: <b>{cat_name}</b>\n\n"
        f"📌 <b>Qoida:</b> Har bir lavozimga faqat 1 ta akkaunt biriktiriladi. "
        f"Kelajakda lavozimni boshqa kishiga o'tkazmoqchi bo'lsangiz, avval quyidagi tugma yoki /leave_staff orqali "
        f"o'zingizni ozod qilishingiz kerak bo'ladi.",
        reply_markup=kb.get_staff_panel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# Lavozimdan ozod bo'lish buyrug'i
@router.message(Command("leave_staff"))
async def cmd_leave_staff(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or user['role'] != 'staff':
        await message.answer("Siz hozirda hech qanday mas'ul lavozimga biriktirilmagansiz.")
        return

    cat_name = CATEGORIES.get(user['staff_category'], user['staff_category'])
    await message.answer(
        f"Hozirgi lavozimingiz: <b>{cat_name}</b>\n\n"
        f"Haqiqatan ham o'z lavozimingizdan ozod bo'lmoqchimisiz? "
        f"Shundan so'ng ushbu lavozim bo'shaydi va boshqa xodim ro'yxatdan o'tishi mumkin bo'ladi.",
        reply_markup=kb.get_leave_staff_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "ask_leave_staff")
async def cb_ask_leave_staff(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or user['role'] != 'staff':
        await callback.answer("Siz mas'ul lavozimda emassiz.", show_alert=True)
        return

    cat_name = CATEGORIES.get(user['staff_category'], user['staff_category'])
    await callback.message.edit_text(
        f"Hozirgi lavozimingiz: <b>{cat_name}</b>\n\n"
        f"Haqiqatan ham o'z lavozimingizdan ozod bo'lmoqchimisiz? "
        f"Shundan so'ng ushbu lavozim bo'shaydi va boshqa xodim ro'yxatdan o'tishi mumkin bo'ladi.",
        reply_markup=kb.get_leave_staff_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_leave_staff")
async def cb_cancel_leave_staff(callback: CallbackQuery):
    await callback.message.edit_text("Amal bekor qilindi. Siz o'z lavozimingizda qoldingiz.")
    await callback.answer()

@router.callback_query(F.data == "confirm_leave_staff")
async def cb_confirm_leave_staff(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if user and user['role'] == 'staff':
        cat_name = CATEGORIES.get(user['staff_category'], user['staff_category'])
        await db.unregister_staff(user_id)
        await callback.message.edit_text(
            f"✅ Siz <b>{cat_name}</b> lavozimidan muvaffaqiyatli ozod bo'ldingiz.\n\n"
            f"Endi ushbu lavozim bo'sh va unga yangi xodim biriktirilishi mumkin.",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text("Siz allaqachon lavozimdan ozod qilingansiz.")
    await callback.answer()

# Muloqotni yakunlash (Talaba yoki Mas'ul bosganda)
@router.callback_query(F.data.startswith("close_"))
async def process_close_ticket(callback: CallbackQuery, bot: Bot):
    ticket_id = int(callback.data.replace("close_", ""))
    ticket = await db.get_ticket_by_id(ticket_id)

    if not ticket or ticket['status'] == 'CLOSED':
        await callback.message.answer("Ushbu murojaat allaqachon yakunlangan.")
        await callback.answer()
        return

    await db.close_ticket(ticket_id)

    student_id = ticket['student_id']
    staff_id = ticket['staff_id']

    # Talabaga xabar
    try:
        await bot.send_message(
            chat_id=student_id,
            text=f"🛑 <b>Murojaat #{ticket_id} yakunlandi.</b>\n\n"
                 f"Sizga yordam bera olganimizdan xursandmiz. Agar yana biror muammo bo'lsa, "
                 f"istalgan vaqtda /start bosib yangi murojaat qoldirishingiz mumkin.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Mas'ulga xabar
    if staff_id:
        try:
            await bot.send_message(
                chat_id=staff_id,
                text=f"🛑 <b>Murojaat #{ticket_id} yakunlandi va yopildi.</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer("Muloqot yakunlandi.")

# Mas'ul xodimning javoblarini talabaga yetkazish (Relay)
@router.message(IsStaff())
async def relay_staff_message(message: Message, bot: Bot):
    user_id = message.from_user.id

    # 1. Mas'ul xodim Telegramda 'Reply' qilganmi?
    if not message.reply_to_message:
        await message.answer(
            "⚠️ <b>Xabaringiz hech kimga yetkazilmadi!</b>\n\n"
            "Talabaga javob qaytarish uchun uning bot orqali kelgan xabariga Telegramda <b>Reply (Javob berish)</b> qilib yozishingiz shart.\n\n"
            "📌 <i>Nima uchun? Sizga bir vaqtning o'zida bir nechta talaba murojaat qilayotgan bo'lishi mumkin. "
            "Xabarlar boshqa talabaga adashib ketmasligi uchun aynan qaysi talabaning murojaatiga javob berayotganingizni Reply orqali ko'rsatishingiz shart.</i>",
            parse_mode="HTML"
        )
        return

    # 2. Reply qilingan xabar bo'yicha murojaatni topish
    mapping = await db.get_mapping_by_staff_msg(
        staff_msg_id=message.reply_to_message.message_id,
        staff_id=user_id
    )

    if not mapping:
        await message.answer(
            "⚠️ Ushbu xabar bo'yicha faol murojaat topilmadi.\n"
            "Iltimos, aynan talabaning xabariga Reply qilib javob yozing.",
            parse_mode="HTML"
        )
        return

    ticket_id = mapping['ticket_id']
    student_id = mapping['student_id']

    # Murojaat ochiq ekanini tekshirish
    ticket = await db.get_ticket_by_id(ticket_id)
    if not ticket or ticket['status'] == 'CLOSED':
        await message.answer("⚠️ Ushbu murojaat yakunlangan. Yangi javob yuborib bo'lmaydi.")
        return

    cat_name = CATEGORIES.get(ticket['category'], "Mas'ul xodim")

    # Talabaga xodim javobini nusxalash
    await bot.send_message(
        chat_id=student_id,
        text=f"💬 <b>{cat_name} javobi:</b>",
        parse_mode="HTML"
    )
    
    await message.copy_to(
        chat_id=student_id,
        reply_markup=kb.get_close_ticket_keyboard(ticket_id)
    )

    await message.answer(f"✅ Javobingiz talabaga yetkazildi (Murojaat #{ticket_id}).")
