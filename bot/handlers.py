from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from bot.keyboards import (
    get_form_keyboard,
    get_subjects_keyboard,
    get_directions_keyboard,
    get_direction_options_keyboard,
)
from bot.utils import calculate_chance, get_directions_data

router = Router()

# -------------------------------
# Глобальные данные и состояния
# -------------------------------
user_data = {}

STAGE_FORM = "form"
STAGE_SUBJECTS = "subjects"
STAGE_DIRECTIONS = "directions"

# -------------------------------
# Команда /start и выбор формы
# -------------------------------
@router.message(F.text == "/start")
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"stage": STAGE_FORM, "form": None, "subjects": [], "directions": []}

    text = "Привет! Выберите форму обучения:"
    keyboard = get_form_keyboard()
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("form:"))
async def select_form(callback: CallbackQuery):
    form = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user_data[user_id]["form"] = form

    # Обновляем клавиатуру с выделением выбранной формы
    keyboard = get_form_keyboard(selected_form=form)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == "confirm_form")
async def confirm_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected_form = user_data[user_id].get("form")

    if not selected_form:
        await callback.answer("Выберите одну форму обучения!", show_alert=True)
        return

    user_data[user_id]["stage"] = STAGE_SUBJECTS
    text = "Выберите дисциплины:"
    keyboard = get_subjects_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)


# -------------------------------
# Выбор дисциплин
# -------------------------------
@router.callback_query(F.data.startswith("subject:"))
async def select_subject(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    user_id = callback.from_user.id

    # Добавление/удаление дисциплин
    if subject in user_data[user_id]["subjects"]:
        user_data[user_id]["subjects"].remove(subject)
    else:
        if len(user_data[user_id]["subjects"]) >= 3:
            await callback.answer("Вы можете выбрать только 3 дисциплины!", show_alert=True)
            return
        user_data[user_id]["subjects"].append(subject)

    keyboard = get_subjects_keyboard(selected_subjects=user_data[user_id]["subjects"])
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == "confirm_subjects")
async def confirm_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    subjects = user_data.get(user_id, {}).get("subjects", [])
    form = user_data.get(user_id, {}).get("form")

    if len(subjects) < 3:
        await callback.answer("Выберите ровно три дисциплины!", show_alert=True)
        return

    user_data[user_id]["stage"] = STAGE_DIRECTIONS
    # Исправленный вызов функции с двумя аргументами
    directions = get_directions_data(subjects)  # Здесь form исключен, так как он не используется
    keyboard = get_directions_keyboard(directions)

    await callback.message.edit_text(
        "Вы выбрали дисциплины. Теперь выберите направление:", reply_markup=keyboard
    )

# -------------------------------
# Выбор направлений
# -------------------------------
from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from bot.keyboards import (
    get_form_keyboard,
    get_subjects_keyboard,
    get_directions_keyboard,
    get_direction_options_keyboard,
)
from bot.utils import calculate_chance, get_directions_data

router = Router()

# -------------------------------
# Глобальные данные и состояния
# -------------------------------
user_data = {}

STAGE_FORM = "form"
STAGE_SUBJECTS = "subjects"
STAGE_DIRECTIONS = "directions"

# -------------------------------
# Команда /start и выбор формы
# -------------------------------
@router.message(F.text == "/start")
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "stage": STAGE_FORM,
        "form": None,
        "subjects": [],
        "directions": []
    }

    text = "Привет! Выберите форму обучения:"
    keyboard = get_form_keyboard()
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("form:"))
async def select_form(callback: CallbackQuery):
    form = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user_data.setdefault(user_id, {})
    user_data[user_id]["form"] = form
    user_data[user_id]["stage"] = STAGE_FORM  # на всякий случай

    keyboard = get_form_keyboard(selected_form=form)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == "confirm_form")
async def confirm_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected_form = user_data.get(user_id, {}).get("form")

    if not selected_form:
        await callback.answer("Выберите одну форму обучения!", show_alert=True)
        return

    user_data[user_id]["stage"] = STAGE_SUBJECTS
    text = "Выберите дисциплины:"
    keyboard = get_subjects_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)


# -------------------------------
# Выбор дисциплин
# -------------------------------
@router.callback_query(F.data.startswith("subject:"))
async def select_subject(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user_data.setdefault(user_id, {})
    subjects = user_data[user_id].setdefault("subjects", [])

    if subject in subjects:
        subjects.remove(subject)
    else:
        if len(subjects) >= 3:
            await callback.answer("Вы можете выбрать только 3 дисциплины!", show_alert=True)
            return
        subjects.append(subject)

    keyboard = get_subjects_keyboard(selected_subjects=subjects)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == "confirm_subjects")
async def confirm_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    subjects = user_data.get(user_id, {}).get("subjects", [])
    form = user_data.get(user_id, {}).get("form")

    if len(subjects) < 3:
        await callback.answer("Выберите ровно три дисциплины!", show_alert=True)
        return

    user_data[user_id]["stage"] = STAGE_DIRECTIONS
    directions = get_directions_data(subjects, form)
    keyboard = get_directions_keyboard(directions)

    await callback.message.edit_text(
        "Вы выбрали дисциплины. Теперь выберите направление:", reply_markup=keyboard
    )


# -------------------------------
# Выбор направлений
# -------------------------------
@router.callback_query(F.data.startswith("direction:"))
async def direction_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    direction_code = callback.data.split(":")[1]
    form = user_data.get(user_id, {}).get("form")

    details = calculate_chance(direction_code, form)
    await callback.message.edit_text(details, reply_markup=get_direction_options_keyboard())


# -------------------------------
# Кнопки "Назад" и "Выход"
# -------------------------------
@router.callback_query(F.data == "back_to_form")
async def back_to_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_FORM

    text = "Привет! Выберите форму обучения:"
    keyboard = get_form_keyboard(selected_form=user_data[user_id].get("form"))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_subjects")
async def back_to_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_SUBJECTS

    text = "Выберите дисциплины:"
    keyboard = get_subjects_keyboard(selected_subjects=user_data[user_id].get("subjects", []))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_directions")
async def back_to_directions(callback: CallbackQuery):
    user_id = callback.from_user.id
    subjects = user_data[user_id].get("subjects", [])
    form = user_data[user_id].get("form")

    directions = get_directions_data(subjects, form)
    keyboard = get_directions_keyboard(directions)

    await callback.message.edit_text("Выберите направление для подробной информации:", reply_markup=keyboard)


@router.callback_query(F.data == "exit")
async def exit(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data.pop(user_id, None)

    text = "Давайте начнем сначала. Выберите форму обучения:"
    keyboard = get_form_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)
@router.callback_query(F.data.startswith("direction:"))
async def direction_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    direction_code = callback.data.split(":")[1]
    user_score = user_data[user_id].get("user_score", 0)

    details = calculate_chance(user_score, direction_code)
    await callback.message.edit_text(details, reply_markup=get_direction_options_keyboard())


# -------------------------------
# Кнопки "Назад" и "Выход"
# -------------------------------
@router.callback_query(F.data == "back_to_form")
async def back_to_form(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_FORM

    text = "Привет! Выберите форму обучения:"
    keyboard = get_form_keyboard(selected_form=user_data[user_id].get("form"))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_subjects")
async def back_to_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id]["stage"] = STAGE_SUBJECTS

    text = "Выберите дисциплины:"
    keyboard = get_subjects_keyboard(selected_subjects=user_data[user_id].get("subjects", []))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_directions")
async def back_to_directions(callback: CallbackQuery):
    user_id = callback.from_user.id
    directions = get_directions_data(user_data[user_id]["subjects"])
    keyboard = get_directions_keyboard(directions)

    await callback.message.edit_text("Выберите направление для подробной информации:", reply_markup=keyboard)


@router.callback_query(F.data == "exit")
async def exit(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data.pop(user_id, None)

    text = "Давайте начнем сначала. Выберите форму обучения:"
    keyboard = get_form_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)
