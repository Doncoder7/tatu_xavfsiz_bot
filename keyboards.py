from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CATEGORIES

def get_categories_keyboard(active_categories: dict = None) -> InlineKeyboardMarkup:
    if active_categories is None:
        active_categories = {}
    buttons = []
    for key, title in CATEGORIES.items():
        if key in active_categories:
            buttons.append([InlineKeyboardButton(text=f"🟢 {title}", callback_data=f"cat_{key}")])
        else:
            buttons.append([InlineKeyboardButton(text=f"🔴 {title} (Ulanmagan)", callback_data=f"catoffline_{key}")])
    buttons.append([InlineKeyboardButton(text="📞 To'g'ridan-to'g'ri kontaktlar", callback_data="view_contacts")])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_request")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Mas'ullar bilan to'g'ridan-to'g'ri kontaktlar", callback_data="view_contacts")]
    ])

def get_contacts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Bot orqali maxfiy murojaat yo'llash", callback_data="start_write_problem")]
    ])

def get_close_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛑 Muloqotni yakunlash", callback_data=f"close_{ticket_id}")]
    ])

def get_staff_roles_keyboard(occupied_categories: dict = None) -> InlineKeyboardMarkup:
    if occupied_categories is None:
        occupied_categories = {}
    buttons = []
    for key, title in CATEGORIES.items():
        if key in occupied_categories:
            occupant = occupied_categories[key]['full_name'] or "Xodim"
            buttons.append([InlineKeyboardButton(text=f"🔒 {title} (Band - {occupant})", callback_data=f"staffrole_occupied_{key}")])
        else:
            buttons.append([InlineKeyboardButton(text=f"🟢 {title} (Bo'sh)", callback_data=f"staffrole_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_leave_staff_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Ha, lavozimdan ozod bo'lish", callback_data="confirm_leave_staff")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_leave_staff")]
    ])

def get_staff_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Lavozimdan ozod bo'lish", callback_data="ask_leave_staff")]
    ])
