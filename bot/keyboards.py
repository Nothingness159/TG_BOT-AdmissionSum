from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# -------------------------------
# Кнопки "Назад" и "Выход" для переиспользования
# -------------------------------
def get_back_exit_keyboard(back_callback: str = "back", exit_callback: str = "exit") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад ◀️", callback_data=back_callback),
            InlineKeyboardButton(text="Выход ❌", callback_data=exit_callback),
        ]
    ])
    return keyboard

# -------------------------------
# Клавиатура выбора формы обучения
# -------------------------------
def get_form_keyboard(selected_form=None) -> InlineKeyboardMarkup:
    forms = [
        ("очная бюджет", "form:очная_бюджет"),
        ("очная договор", "form:очная_договор"),
        ("очно-заочная бюджет", "form:очно-заочная_бюджет"),
        ("очно-заочная договор", "form:очно-заочная_договор"),
    ]

    buttons = []
    for text, callback_data in forms:
        if selected_form == callback_data.split(":")[1]:
            text = "✅ " + text
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="Далее ▶️", callback_data="confirm_form")])
    buttons.append([InlineKeyboardButton(text="Выход ❌", callback_data="exit")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# -------------------------------
# Клавиатура выбора дисциплин (до 3)
# -------------------------------
def get_subjects_keyboard(selected_subjects=None) -> InlineKeyboardMarkup:
    if selected_subjects is None:
        selected_subjects = []

    subjects = [
        "Базовая математика",
        "Профильная математика",
        "Физика",
        "Химия",
        "Информатика",
        "Биология",
        "История",
        "Обществознание",
        "Английский язык",
        "Русский язык",
        "Литература",
    ]

    buttons = []
    row = []
    for subject in subjects:
        text = subject
        if subject in selected_subjects:
            text = "✅ " + text
        row.append(InlineKeyboardButton(text=text, callback_data=f"subject:{subject}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:  # Добавляем оставшиеся кнопки, если их нечетное количество
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="Далее ▶️", callback_data="confirm_subjects")])
    
    # Добавляем кнопки "Назад" и "Выход"
    back_exit_buttons = get_back_exit_keyboard(
        back_callback="back_to_form", 
        exit_callback="exit"
    ).inline_keyboard[0]
    buttons.append(back_exit_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# -------------------------------
# Клавиатура с направлениями
# -------------------------------
def get_directions_keyboard(directions: list) -> InlineKeyboardMarkup:
    buttons = []
    for direction in directions:
        buttons.append([InlineKeyboardButton(text=direction, callback_data=f"direction:{direction}")])

    # Добавляем кнопки "Назад" и "Выход"
    back_exit_buttons = get_back_exit_keyboard(
        back_callback="back_to_subjects", 
        exit_callback="exit"
    ).inline_keyboard[0]
    buttons.append(back_exit_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# -------------------------------
# Клавиатура с опциями при просмотре направления
# -------------------------------
def get_direction_options_keyboard() -> InlineKeyboardMarkup:
    return get_back_exit_keyboard(back_callback="back_to_directions", exit_callback="exit")