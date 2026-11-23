from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from config import CATEGORIES, CONTACTS_INFO
from filters import IsStudent

router = Router()

class StudentForm(StatesGroup):
    waiting_for_problem = State()
    waiting_for_category = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Mas'ul xodim ekanligini tekshirish
    user = await db.get_user(user_id)
    if user and user['role'] == 'staff':
        cat_name = CATEGORIES.get(user['staff_category'], user['staff_category'])
        await message.answer(
            f"Salom, hurmatli mas'ul xodim!\n"
            f"Sizning yo'nalishingiz: <b>{cat_name}</b>\n\n"
            f"Talabalardan yangi murojaatlar tushsa, shu yerda xabardor qilinasiz.\n\n"
            f"Lavozimni topshirmoqchi bo'lsangiz, quyidagi tugmani bosing:",
            reply_markup=kb.get_staff_panel_keyboard(),
            parse_mode="HTML"
        )
        return

    # Faol murojaati bormi?
    active_ticket = await db.get_active_student_ticket(user_id)
    if active_ticket:
        cat_name = CATEGORIES.get(active_ticket['category'], active_ticket['category'])
        await message.answer(
            f"Sizda hozirda ochiq murojaat mavjud (<b>Murojaat #{active_ticket['id']}</b>).\n"
            f"Yo'nalish: <b>{cat_name}</b>\n\n"
            f"Mas'ulga yangi xabar yuborish uchun shunchaki shu yerga yozing (matn, ovozli xabar yoki rasm).\n\n"
            f"Muloqotni yakunlash uchun quyidagi tugmani bosing:",
            reply_markup=kb.get_close_ticket_keyboard(active_ticket['id']),
            parse_mode="HTML"
        )
        return

    await state.clear()
    await state.set_state(StudentForm.waiting_for_problem)
    await message.answer(
        "Assalomu alaykum! Universitet talaba qizlari uchun tezkor yordam va murojaatlar botiga xush kelibsiz.\n\n"
        "Bu yerda siz o'zingizni qiynayotgan har qanday muammo, tazyiq, xavfsizlik yoki noxush holatlar bo'yicha murojaat qilishingiz mumkin.\n\n"
        "🔒 <b>Sizning shaxsingiz to'liq sir saqlanadi.</b>\n\n"
        "Iltimos, muammoingizni bayon qiling (matn, ovozli xabar yoki rasm ko'rinishida yuborishingiz mumkin):\n\n"
        "<i>(Yoki mas'ullar bilan to'g'ridan-to'g'ri bog'lanish uchun quyidagi tugmani bosing)</i>",
        reply_markup=kb.get_start_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("contacts"))
async def cmd_contacts(message: Message):
    await message.answer(
        CONTACTS_INFO,
        reply_markup=kb.get_contacts_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "view_contacts")
async def cb_view_contacts(callback: CallbackQuery):
    await callback.message.answer(
        CONTACTS_INFO,
        reply_markup=kb.get_contacts_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "start_write_problem")
async def cb_start_write_problem(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StudentForm.waiting_for_problem)
    await callback.message.answer(
        "Iltimos, o'zingizni qiynayotgan muammoni yozib qoldiring (matn, ovozli xabar yoki rasm yuborishingiz mumkin):\n\n"
        "🔒 <i>Shaxsingiz to'liq sir saqlanadi.</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(StudentForm.waiting_for_problem)
async def process_problem(message: Message, state: FSMContext):
    # Foydalanuvchining boshlang'ich xabarini saqlash
    await state.update_data(problem_msg_id=message.message_id)
    await state.set_state(StudentForm.waiting_for_category)
    
    active_staff = await db.get_all_staff_positions()
    await message.answer(
        "Murojaatingiz qabul qilindi. ✍️\n\n"
        "Ushbu muammo universitetning qaysi mas'ul xodimiga yuborilishini xohlaysiz? "
        "Quyidagi ro'yxatdan o'zingizga mos bo'limni tanlang:\n\n"
        "🟢 — Botga ulangan va xabarlarni qabul qiladi\n"
        "🔴 — Hozircha botga ulanmagan (faqat telefon orqali)",
        reply_markup=kb.get_categories_keyboard(active_staff)
    )

@router.callback_query(F.data.startswith("catoffline_"))
async def process_offline_category(callback: CallbackQuery):
    await callback.answer(
        "⚠️ Bu xodim hozircha botga ulanmagan!\n\n"
        "Murojaatingiz javobsiz qolmasligi uchun uni tanlab bo'lmaydi. "
        "Iltimos, u bilan telefon orqali bog'laning yoki botda faol (🟢) mas'ulni tanlang.",
        show_alert=True
    )

@router.callback_query(F.data == "cancel_request")
async def cancel_request(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Murojaat bekor qilindi. Yangi murojaat uchun /start buyrug'ini bosing.")
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    category = callback.data.replace("cat_", "")
    cat_name = CATEGORIES.get(category, category)
    student_id = callback.from_user.id

    data = await state.get_data()
    problem_msg_id = data.get("problem_msg_id")

    if not problem_msg_id:
        await callback.message.edit_text("Xatolik yuz berdi. Iltimos, /start buyrug'i orqali qaytadan urinib ko'ring.")
        await state.clear()
        return

    # Ushbu yo'nalishdagi mas'ul xodimni tekshirish
    staff = await db.get_active_staff_by_category(category)
    if not staff:
        await callback.answer(
            "⚠️ Ushbu mas'ul xodim hozirda botda ro'yxatdan o'tmagan! Boshqa faol mas'ulni tanlang.",
            show_alert=True
        )
        active_staff = await db.get_all_staff_positions()
        await callback.message.edit_reply_markup(reply_markup=kb.get_categories_keyboard(active_staff))
        return

    staff_id = staff['user_id']

    # Murojaat yaratish (faqat xodim mavjud bo'lsagina yaratiladi!)
    ticket_id = await db.create_ticket(student_id=student_id, category=category, staff_id=staff_id)
    await state.clear()

    notify_text = (
        f"🔔 <b>YANGI MUROJAAT! (Murojaat #{ticket_id})</b>\n"
        f"Yo'nalish: <b>{cat_name}</b>\n\n"
        f"Quyida talaba tomonidan yuborilgan murojaat keltirilgan:\n"
        f"<i>(Talabaga javob qaytarish uchun ushbu xabarga Telegramda 'Reply' qilib yozing)</i>"
    )
    await bot.send_message(chat_id=staff_id, text=notify_text, parse_mode="HTML")
    
    # Talaba xabarini xodimga nusxalash
    copied_msg = await bot.copy_message(
        chat_id=staff_id,
        from_chat_id=student_id,
        message_id=problem_msg_id,
        reply_markup=kb.get_close_ticket_keyboard(ticket_id)
    )
    
    # Mappingni saqlash (reply qilinganda topish uchun)
    await db.save_message_mapping(
        ticket_id=ticket_id,
        staff_msg_id=copied_msg.message_id,
        staff_id=staff_id,
        student_id=student_id
    )

    await callback.message.edit_text(
        f"✅ Murojaatingiz <b>{cat_name}</b>ga muvaffaqiyatli yetkazildi!\n\n"
        f"🔒 Sizning shaxsingiz sir saqlanadi.\n"
        f"Mas'ul xodim javob berishi bilan xabar shu yerga keladi. "
        f"Unga qo'shimcha xabar yozish uchun shunchaki shu yerga yozing.",
        reply_markup=kb.get_close_ticket_keyboard(ticket_id),
        parse_mode="HTML"
    )
    await callback.answer()

# Ochiq murojaati bor talabaning xabarlarini mas'ulga yetkazish (Relay)
@router.message(IsStudent())
async def relay_student_message(message: Message, bot: Bot):
    student_id = message.from_user.id


    active_ticket = await db.get_active_student_ticket(student_id)
    if not active_ticket:
        await message.answer("Yangi murojaat yo'llash uchun /start buyrug'ini bosing.")
        return

    staff_id = active_ticket['staff_id']
    if not staff_id:
        await message.answer(
            f"Murojaatingiz #{active_ticket['id']} navbatda turibdi. "
            f"Mas'ul xodim biriktirilishi bilan xabarlaringiz yetkaziladi."
        )
        return

    # Xodimga bildirishnoma va xabar nusxasi
    copied_msg = await message.copy_to(
        chat_id=staff_id,
        reply_markup=kb.get_close_ticket_keyboard(active_ticket['id'])
    )

    await db.save_message_mapping(
        ticket_id=active_ticket['id'],
        staff_msg_id=copied_msg.message_id,
        staff_id=staff_id,
        student_id=student_id
    )

    await message.answer("✅ Xabaringiz mas'ul xodimga yetkazildi.")
