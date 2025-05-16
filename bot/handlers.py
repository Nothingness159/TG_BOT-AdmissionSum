from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Dict, List, Optional
import logging 
from urllib.parse import unquote
from bot.keyboards import BotKeyboards
from bot.utils import (
    calculate_chance,
    get_directions_data,
    calculate_total_score,
    validate_user_score,
    get_achievements_points
)
logger = logging.getLogger(__name__)
router = Router()
storage = MemoryStorage()

# -------------------------------
# Состояния пользователя
# -------------------------------

STAGE_FORM = "form"
STAGE_SUBJECTS = "subjects"
STAGE_EGE_SCORE = "ege_score"
STAGE_ACHIEVEMENTS = "achievements"
STAGE_RESULTS = "results"

user_data = {}  # user_id -> { stage, form, subjects, ege_score, achievements }

# -------------------------------
# Команда /start
# -------------------------------

@router.message(F.text == "/start")
async def start_command(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "stage": STAGE_FORM,
        "form": None,
        "subjects": [],
    }
    await message.answer(
        "🎓 Я помогу вам найти подходящие направления.\n\nВыберите форму обучения:",
        reply_markup=BotKeyboards.get_form_keyboard()
    )

# -------------------------------
# Выбор формы обучения
# -------------------------------

@router.callback_query(F.data.startswith("form:"))
async def select_form(callback: CallbackQuery):
    form = callback.data.split(":")[1]
    user_id = callback.from_user.id
    user_data[user_id]["form"] = form
    keyboard = BotKeyboards.get_form_keyboard(selected_form=form)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data == "confirm_form")
async def confirm_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected_form = user_data[user_id].get("form")
    if not selected_form:
        await callback.answer("Выберите одну форму обучения!", show_alert=True)
        return
    user_data[user_id]["stage"] = STAGE_SUBJECTS
    text = "📘 Выберите дополнительные предметы (минимум 1):"
    keyboard = BotKeyboards.get_subjects_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

# -------------------------------
# Выбор предметов
# -------------------------------

@router.callback_query(F.data.startswith("subject:"))
async def select_subject(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    user_id = callback.from_user.id
    subjects = user_data[user_id]["subjects"]

    if subject in subjects:
        subjects.remove(subject)
    else:
        if len(subjects) >= 4:
            await callback.answer("Можно выбрать максимум 4 доп. предмета.", show_alert=True)
            return
        subjects.append(subject)

    keyboard = BotKeyboards.get_subjects_keyboard(selected_subjects=subjects)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data == "confirm_subjects")
async def confirm_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    subjects = user_data[user_id]["subjects"]
    if not subjects:
        await callback.answer("Выберите хотя бы один дополнительный предмет.", show_alert=True)
        return
    user_data[user_id]["stage"] = STAGE_EGE_SCORE
    await callback.message.edit_text("🔢 Введите ваш суммарный балл ЕГЭ (от 120 до 310):")

# -------------------------------
# Ввод баллов ЕГЭ
# -------------------------------

@router.message(F.text)
async def process_ege_score(message: Message):
    user_id = message.from_user.id
    if user_data.get(user_id, {}).get("stage") != STAGE_EGE_SCORE:
        return

    try:
        score = validate_user_score(message.text)
        user_data[user_id]["ege_score"] = score
        user_data[user_id]["stage"] = STAGE_ACHIEVEMENTS

        await message.answer(
            "🏆 Выберите ваши индивидуальные достижения:",
            reply_markup=BotKeyboards.get_achievements_keyboard()
        )
    except ValueError as e:
        await message.answer(f"❌ {str(e)}\nПопробуйте еще раз:")

# -------------------------------
# Выбор достижений
# -------------------------------

@router.callback_query(F.data.startswith("achievement:"))
async def select_achievement(callback: CallbackQuery):
    achievement = callback.data.split(":")[1]
    user_id = callback.from_user.id

    current_achievements = user_data[user_id].setdefault("selected_achievements", [])

    if achievement in current_achievements:
        current_achievements.remove(achievement)
    else:
        current_achievements.append(achievement)

    keyboard = BotKeyboards.get_achievements_keyboard(selected_achievements=current_achievements)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data == "confirm_achievements")
async def confirm_achievements(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        # Проверяем наличие всех необходимых данных
        if not all(k in user_data[user_id] for k in ["ege_score", "form", "subjects"]):
            await callback.answer("Недостаточно данных. Начните с /start", show_alert=True)
            return

        # Получаем и проверяем данные
        ege_score = user_data[user_id]["ege_score"]
        achievements = user_data[user_id].get("selected_achievements", [])
        form = user_data[user_id]["form"]
        subjects = user_data[user_id]["subjects"]

        # Рассчитываем общий балл
        total_score = calculate_total_score(
            ege_score,
            get_achievements_points(achievements)
        )
        user_data[user_id]["total_score"] = total_score
        user_data[user_id]["stage"] = STAGE_RESULTS

        # Получаем направления
        directions = get_directions_data(subjects, form)
        if not directions:
            await callback.message.edit_text(
                "😕 Подходящих направлений не найдено",
                reply_markup=BotKeyboards.get_back_keyboard()
            )
            return

        user_data[user_id]["directions"] = directions
        keyboard = BotKeyboards.get_directions_keyboard(directions)
        await callback.message.edit_text(
            "🎯 Подходящие направления:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка подтверждения достижений: {str(e)}", exc_info=True)
        await callback.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)

# -------------------------------
# Просмотр информации о направлении
# -------------------------------
@router.callback_query(F.data.startswith("direction:"))
async def direction_details(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        direction_code = callback.data.split(":", 1)[1].strip()

        details = calculate_chance(
            user_data[user_id]["total_score"],
            direction_code,
            user_data[user_id]["form"]
        )

        await callback.message.edit_text(details, reply_markup=BotKeyboards.get_direction_details_keyboard(), parse_mode="HTML")
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при отображении направления: {e}", exc_info=True)
        await callback.answer("Произошла ошибка", show_alert=True)

# -------------------------------
# Кнопки "Назад", "Выход"
# -------------------------------

@router.callback_query(F.data == "back_to_form")
async def back_to_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data.pop(user_id, None)
    await start_command(callback.message)

@router.callback_query(F.data == "back_to_subjects")
async def back_to_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_SUBJECTS
    subjects = user_data[user_id].get("subjects", [])
    await callback.message.edit_text(
        "📘 Выберите дополнительные предметы (минимум 1):",
        reply_markup=BotKeyboards.get_subjects_keyboard(selected_subjects=subjects)
    )

@router.callback_query(F.data == "back_to_achievements")
async def back_to_achievements(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_ACHIEVEMENTS
    await callback.message.edit_text(
        "🏆 Выберите ваши индивидуальные достижения:",
        reply_markup=BotKeyboards.get_achievements_keyboard()
    )

@router.callback_query(F.data == "back_to_directions")
async def back_to_directions(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_RESULTS
    directions = user_data[user_id].get("directions", [])
    await callback.message.edit_text(
        "🎯 Вот подходящие направления:",
        reply_markup=BotKeyboards.get_directions_keyboard(directions)
    )

@router.callback_query(F.data == "exit")
async def exit_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await callback.message.edit_text("👋 До свидания! Напишите /start, чтобы начать заново.")
