import pandas as pd
from pathlib import Path
import logging
from typing import List, Set, Dict, Optional, Union
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы
DATA_DIR = Path(__file__).parent.parent / "data"
EXCEL_FILE = DATA_DIR / "directions.xlsx"

# Сопоставление форм обучения с листами Excel
FORM_TO_SHEET = {
    "очная бюджет": "очная бюджет",
    "очная договор": "Договор ОЧ",
    "очно-заочная бюджет": "Бюджет ОЗ",
    "очно-заочная договор": "Договор ОЗ"
}

# -------------------------------
# Чтение и обработка данных Excel
# -------------------------------

def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Загружает данные листа Excel"""
    try:
        if not EXCEL_FILE.exists():
            raise FileNotFoundError(f"Файл {EXCEL_FILE} не найден")

        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None, engine='openpyxl')
        if df.empty:
            raise ValueError("Лист пустой")

        return df.dropna(how='all').dropna(axis=1, how='all')

    except Exception as e:
        logger.error(f"Ошибка загрузки листа {sheet_name}: {str(e)}")
        raise ValueError(f"Ошибка загрузки данных: {str(e)}")


def parse_directions_sheet(sheet_name: str) -> pd.DataFrame:
    """Обрабатывает лист с направлениями обучения"""
    df = load_sheet(sheet_name)

    # Установка заголовков
    headers = df.iloc[0].fillna('').astype(str).str.strip()
    df.columns = headers
    df = df.iloc[1:]

    # Фильтрация строк
    df = df[
        ~df["Направление"].str.contains(
            "Вес|Больше чем зн|между|Меньше чем зн",
            na=False,
            regex=True
        )
    ].fillna("-")

    logger.debug(f"Загружено {len(df)} направлений для формы {sheet_name}")
    return df


# -------------------------------
# Нормализация данных
# -------------------------------

def normalize_form(form: str) -> Optional[str]:
    """Стандартизирует название формы обучения"""
    form = form.lower().strip()

    form_mapping = {
        "очная бюджет": ["очная бюджет", "очная_бюджет"],
        "очная договор": ["очная договор", "очная_договор"],
        "очно-заочная бюджет": ["очно-заочная бюджет", "очно_заочная_бюджет"],
        "очно-заочная договор": ["очно-заочная договор", "очно_заочная_договор"]
    }

    for normalized, variants in form_mapping.items():
        if any(v in form for v in variants):
            return normalized
    return None


def normalize_subject_name(subject: str) -> str:
    """Приводит названия предметов к стандартному виду"""
    subject = subject.lower().strip()

    # Обработка математики
    if any(math_word in subject for math_word in ["мат", "матем"]):
        if any(prof_word in subject for prof_word in ["проф", "profile"]):
            return "профильная математика"
        elif any(base_word in subject for base_word in ["баз", "base"]):
            return "базовая математика"
        return "математика"

    # Удаляем спецсимволы
    subject = re.sub(r'[^a-zа-яё\s]', '', subject)
    subject = re.sub(r'\s+', ' ', subject).strip()

    # Стандартизация названий
    subject_aliases = {
        "инф": "информатика",
        "физ": "физика",
        "хим": "химия",
        "био": "биология",
        "ист": "история",
        "общ": "обществознание",
        "лит": "литература",
        "гео": "география",
        "англ": "иностранный язык"
    }

    for alias, full_name in subject_aliases.items():
        if alias in subject:
            return full_name

    return subject


# -------------------------------
# Логика поиска направлений
# -------------------------------

def extract_required_subjects(subjects_str: str) -> Set[str]:
    """Извлекает и нормализует предметы из строки"""
    if not isinstance(subjects_str, str) or subjects_str.strip() in ("-", ""):
        return set()

    # Нормализация строки
    subjects_str = re.sub(r'[^a-zа-яё/\s]', '', subjects_str.lower())
    subjects = set()

    for part in re.split(r'[/\s]+', subjects_str):
        part = part.strip()
        if part:
            normalized = normalize_subject_name(part)
            if normalized:
                subjects.add(normalized)

    return subjects


def find_matching_subjects(selected: Set[str], required: Set[str]) -> Set[str]:
    """Находит совпадения между выбранными и требуемыми предметами"""
    matched = set()

    for user_subj in selected:
        user_norm = normalize_subject_name(user_subj)
        for req_subj in required:
            req_norm = normalize_subject_name(req_subj)

            # Проверяем различные варианты совпадений
            if (user_norm == req_norm or
                user_norm in req_norm or
                req_norm in user_norm):
                matched.add(user_subj)
                break

    return matched


def get_directions_data(selected_subjects: List[str], form: str) -> List[str]:
    """Основная функция поиска подходящих направлений"""
    normalized_form = normalize_form(form)
    if not normalized_form:
        raise ValueError(f"Неизвестная форма обучения: {form}")

    sheet_name = FORM_TO_SHEET[normalized_form]
    df = parse_directions_sheet(sheet_name)

    # Нормализуем выбранные предметы
    selected_normalized = {normalize_subject_name(s) for s in selected_subjects}
    result = []

    for _, row in df.iterrows():
        direction = row["Направление"]
        subjects_str = str(row.get("Предметы", "-"))

        # Получаем требуемые предметы
        required_subjects = extract_required_subjects(subjects_str)

        # Находим совпадения
        matched = find_matching_subjects(selected_normalized, required_subjects)

        # Проверяем наличие математики
        has_math = any("математика" in subj for subj in matched)

        # Если есть хотя бы 2 предмета и математика — направление подходит
        if len(matched) >= 2 and has_math:
            result.append(direction)

    logger.info(f"Для предметов {selected_subjects} найдено {len(result)} направлений")
    return result


# -------------------------------
# Расчет шансов поступления
# -------------------------------

def calculate_chance(user_score: int, direction_code: str, form: str) -> str:
    normalized_form = normalize_form(form)
    if not normalized_form:
        raise ValueError(f"Неизвестная форма обучения: {form}")

    sheet_name = FORM_TO_SHEET[normalized_form]
    df = parse_directions_sheet(sheet_name)

    # Ищем направление по коду
    code_pattern = re.escape(direction_code.strip())
    direction_row = df[df["Направление"].str.contains(code_pattern, case=False, na=False)]

    if direction_row.empty:
        logger.warning(f"Направление с кодом '{direction_code}' не найдено")
        raise ValueError(f"Направление с кодом '{direction_code}' не найдено")

    direction = direction_row.iloc[0]

    # Получаем данные из таблицы
    score_2022 = direction.get("Год 2022", "-")
    score_23 = direction.get("Год 2023", "-")
    score_24 = direction.get("Год 2024", "-")
    budget_places = direction.get("Кол-во бюджетных мест всего", "-")
    quota_target = direction.get("квота приема на целевое обучение", "-")
    quota_special = direction.get("особая квота", "-")
    quota_separate = direction.get("отдельная квота", "-")
    high_score = direction.get("Высокие", 0)
    mid_score = direction.get("Средние", 0)

    # Определяем шансы
    if user_score >= high_score:
        chance = "🟢 Высокие"
    elif user_score >= mid_score:
        chance = "🟡 Средние"
    else:
        chance = "🔴 Низкие"

    # Формируем ответ без вывода кода направления
    return f"""
📊 <b>Проходные баллы:</b>
- 2022: {score_2022}
- 2023: {score_23}
- 2024: {score_24}

👥 <b>Количество мест:</b> {budget_places}
🎯 <b>Целевая квота:</b> {quota_target}
🎖 <b>Особая квота:</b> {quota_special}
🎖 <b>Отдельная квота:</b> {quota_separate}

📈 <b>Ваши шансы:</b> {chance}
""".strip()


# -------------------------------
# Валидация и вспомогательные функции
# -------------------------------

def validate_user_score(score: Union[int, str]) -> int:
    """Проверяет и преобразует баллы ЕГЭ"""
    try:
        score = int(score)
        if not (120 <= score <= 310):
            raise ValueError("Баллы ЕГЭ должны быть между 120 и 310")
        return score
    except (TypeError, ValueError) as e:
        logger.error(f"Некорректные баллы: {score}. Ошибка: {str(e)}")
        raise ValueError("Введите корректное число от 120 до 310")


def get_achievements_points(achievements: List[str]) -> int:
    """Считает баллы за индивидуальные достижения"""
    points_map = {
        "attestat_diplom": 10,  # Аттестат с отличием
        "gto": 3               # Золотой ГТО
    }
    total = sum(points_map.get(a, 0) for a in achievements)
    return min(total, 10)  # Не более 10 баллов суммарно


def calculate_total_score(ege_score: Union[int, str], achievement_score: int) -> int:
    """Суммирует баллы ЕГЭ и достижений"""
    validated_ege = validate_user_score(ege_score)
    if not (0 <= achievement_score <= 10):
        raise ValueError("Баллы за достижения должны быть от 0 до 10")
    return validated_ege + achievement_score