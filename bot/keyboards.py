from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional, List, Dict
import re
from urllib.parse import quote

def safe_callback_data(text: str, prefix: str = "") -> str:
    # Удаляем недопустимые символы
    clean_text = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ_\- ]', '', text)
    # Обрезаем до 30 символов
    clean_text = clean_text[:30]
    # URL-кодируем
    encoded = quote(clean_text)
    full_data = f"{prefix}{encoded}"
    
    # Дополнительно укорачиваем, если больше 64 байт
    while len(full_data.encode('utf-8')) > 64:
        clean_text = clean_text[:-1]
        encoded = quote(clean_text)
        full_data = f"{prefix}{encoded}"
    
    return full_data
class BotKeyboards:
    """Класс для генерации всех клавиатур бота"""

    _BUTTONS_CONFIG = {
        "next": ("Далее ▶️", "confirm"),
        "back": ("Назад ◀️", "back"),
        "exit": ("Выход ❌", "exit"),
        "none": ("❌ Направления не найдены", "none")
    }

    _EDU_FORMS = [
        ("очная бюджет", "form:очная_бюджет"),
        ("очная договор", "form:очная_договор"),
        ("очно-заочная бюджет", "form:очно-заочная_бюджет"),
        ("очно-заочная договор", "form:очно-заочная_договор")
    ]

    _SUBJECTS = [
        "Профильная математика",
        "Базовая математика",
        "Информатика",
        "Физика",
        "Химия",
        "Биология",
        "История",
        "Обществознание",
        "Иностранный язык",
        "Литература",
        "География"
    ]

    _ACHIEVEMENTS = {
        "attestat_diplom": "Диплом/аттестат с отличием",
        "gto": "Золотой значок ГТО"
    }

    @classmethod
    def _add_control_buttons(cls, buttons: list, back_step: str = None) -> None:
        """Добавляет стандартные кнопки управления"""
        controls = []

        if back_step:
            controls.append(InlineKeyboardButton(
                text=cls._BUTTONS_CONFIG["back"][0],
                callback_data=f"back_to_{back_step}"
            ))

        controls.append(InlineKeyboardButton(
            text=cls._BUTTONS_CONFIG["exit"][0],
            callback_data=cls._BUTTONS_CONFIG["exit"][1]
        ))

        buttons.append(controls)

    @classmethod
    def get_form_keyboard(cls, selected_form: Optional[str] = None) -> InlineKeyboardMarkup:
        """Клавиатура выбора формы обучения"""
        buttons = []

        for text, callback_data in cls._EDU_FORMS:
            if selected_form and callback_data.split(":")[1] == selected_form:
                text = f"✅ {text}"
            buttons.append([InlineKeyboardButton(
                text=text,
                callback_data=callback_data
            )])

        # Кнопки управления
        buttons.append([InlineKeyboardButton(
            text=cls._BUTTONS_CONFIG["next"][0],
            callback_data="confirm_form"
        )])
        cls._add_control_buttons(buttons)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def get_subjects_keyboard(cls, selected_subjects: Optional[List[str]] = None) -> InlineKeyboardMarkup:
        """Клавиатура выбора предметов"""
        selected_subjects = selected_subjects or []
        buttons = []
        row = []

        for subject in cls._SUBJECTS:
            prefix = "✅ " if subject in selected_subjects else ""
            row.append(InlineKeyboardButton(
                text=f"{prefix}{subject}",
                callback_data=f"subject:{subject}"
            ))

            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        # Кнопки управления
        buttons.append([InlineKeyboardButton(
            text=cls._BUTTONS_CONFIG["next"][0],
            callback_data="confirm_subjects"
        )])
        cls._add_control_buttons(buttons, back_step="form")

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def get_direction_options_keyboard(cls) -> InlineKeyboardMarkup:
        """Клавиатура опций направления"""
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=cls._BUTTONS_CONFIG["back"][0],
                callback_data="back_to_directions"
            )
        ]])
    @classmethod
    def get_directions_keyboard(cls, directions: List[str]) -> InlineKeyboardMarkup:
        buttons = []
        for direction in directions:
            # Извлекаем код направления (до первого пробела или точки)
            code_match = re.match(r'^\s*(\d+\.\d+\.\d+)', direction.strip())
            code = code_match.group(1) if code_match else direction[:10]

            # Для отображения: обрезаем длинные строки
            display_text = direction[:30] + "..." if len(direction) > 30 else direction
            
            # callback_data содержит код направления
            callback_data = f"direction:{code}"

            buttons.append([
                InlineKeyboardButton(
                    text=display_text,
                    callback_data=callback_data
                )
            ])

        # Кнопки управления
        buttons.append([
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_subjects"),
            InlineKeyboardButton(text="❌ Выход", callback_data="exit")
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    @classmethod
    def get_direction_details_keyboard(cls) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_directions")],
            [InlineKeyboardButton(text="❌ Выход", callback_data="exit")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def get_achievements_keyboard(cls, selected_achievements: Optional[List[str]] = None) -> InlineKeyboardMarkup:
        """Клавиатура выбора достижений"""
        selected_achievements = selected_achievements or []
        buttons = []

        for key, label in cls._ACHIEVEMENTS.items():
            prefix = "✅ " if key in selected_achievements else ""
            buttons.append([InlineKeyboardButton(
                text=f"{prefix}{label}",
                callback_data=f"achievement:{key}"
            )])

        # Кнопки управления
        buttons.append([InlineKeyboardButton(
            text=cls._BUTTONS_CONFIG["next"][0],
            callback_data="confirm_achievements"
        )])
        cls._add_control_buttons(buttons, back_step="subjects")

        return InlineKeyboardMarkup(inline_keyboard=buttons)