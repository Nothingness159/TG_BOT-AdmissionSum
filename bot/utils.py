import pandas as pd

# -------------------------------
# Функции для работы с данными
# -------------------------------

def load_data(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Загружает данные из указанного листа Excel-файла.

    :param file_path: Путь к Excel-файлу.
    :param sheet_name: Название листа в Excel.
    :return: DataFrame с данными.
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        raise ValueError(f"Ошибка загрузки файла: {e}")


def normalize_form(form: str) -> str:
    """
    Нормализует форму обучения, приводя к одному из ключей:
    "бюджет оч", "договор оч", "бюджет оз", "договор оз"
    
    Поддерживает варианты с подчеркиваниями и пробелами.
    """
    mapping = {
        "очная бюджет": "бюджет оч",
        "бюджет оч": "бюджет оч",
        "очная_бюджет": "бюджет оч",

        "очная договор": "договор оч",
        "договор оч": "договор оч",
        "очная_договор": "договор оч",

        "очно-заочная бюджет": "бюджет оз",
        "бюджет оз": "бюджет оз",
        "очно_заочная_бюджет": "бюджет оз",

        "очно-заочная договор": "договор оз",
        "договор оз": "договор оз",
        "очно_заочная_договор": "договор оз",
    }
    f = form.lower().replace('_', ' ').strip()
    return mapping.get(f, None)


def get_directions_data(selected_subjects: list, form: str) -> list:
    """
    Фильтрует направления по выбранным дисциплинам и форме обучения.

    :param selected_subjects: Список выбранных дисциплин.
    :param form: Форма обучения с типом финансирования,
                 например: "бюджет оч", "договор оч", "бюджет оз", "договор оз".
    :return: Список направлений, соответствующих условиям.
    """
    form_to_sheet = {
        "бюджет оч": "очная бюджет",
        "договор оч": "очная договор",
        "бюджет оз": "очно-заочная бюджет",
        "договор оз": "очно-заочная договор",
    }

    normalized_form = normalize_form(form)
    if not normalized_form:
        raise ValueError(f"Неизвестная форма обучения: {form}")

    sheet_name = form_to_sheet[normalized_form]

    data = load_data("data/directions.xlsx", sheet_name=sheet_name)

    filtered_directions = []
    for _, row in data.iterrows():
        subjects = str(row[9]).split()
        if len(set(selected_subjects).intersection(subjects)) >= 3:
            filtered_directions.append({
                "code": row['Направление'],
                "name": row['Направление'],
                "high": row['Высокие'],
                "mid": row['Средние'],
                "low": row['Низкие']
            })

    return filtered_directions


def calculate_chance(user_score: int, direction_code: str, form: str) -> str:
    """
    Рассчитывает шансы поступления на выбранное направление.

    :param user_score: Баллы пользователя.
    :param direction_code: Код выбранного направления.
    :param form: Форма обучения с типом финансирования,
                 например: "бюджет оч", "договор оч", "бюджет оз", "договор оз".
    :return: Текст с шансами поступления.
    """
    form_to_sheet = {
        "бюджет оч": "очная бюджет",
        "договор оч": "очная договор",
        "бюджет оз": "очно-заочная бюджет",
        "договор оз": "очно-заочная договор",
    }

    normalized_form = normalize_form(form)
    if not normalized_form:
        raise ValueError(f"Неизвестная форма обучения: {form}")

    sheet_name = form_to_sheet[normalized_form]

    data = load_data("data/directions.xlsx", sheet_name=sheet_name)

    direction = data[data['Направление'] == direction_code]
    if direction.empty:
        raise ValueError(f"Направление '{direction_code}' не найдено на листе '{sheet_name}'")

    direction = direction.iloc[0]

    if user_score >= direction['Высокие']:
        chance = "Высокие шансы"
    elif user_score >= direction['Средние']:
        chance = "Средние шансы"
    else:
        chance = "Низкие шансы"

    details = (
        f"Направление: {direction_code}\n"
        f"Прогнозируемый проходной балл: {direction['Год 2025 Прогнозируемый проходной балл']}\n"
        f"Количество бюджетных мест: {direction['Кол-во бюджетных мест всего']}\n"
        f"Общие места: {direction['общие места']}\n"
        f"Квота на целевое обучение: {direction['квота приема на целевое обучение']}\n"
        f"Особая квота: {direction['особая квота']}\n"
        f"Отдельная квота: {direction['отдельная квота']}\n"
        f"Ваши шансы поступить: {chance}"
    )
    return details


# -------------------------------
# Валидация пользовательских данных
# -------------------------------

def validate_user_score(score: int) -> bool:
    """
    Проверяет корректность введенного балла пользователя.

    :param score: Баллы пользователя.
    :return: True, если баллы корректны, иначе False.
    """
    return 120 <= score <= 310


def validate_individual_achievement(score: int) -> bool:
    """
    Проверяет корректность введенного балла за индивидуальные достижения.

    :param score: Баллы за достижения.
    :return: True, если баллы корректны, иначе False.
    """
    return 0 <= score <= 10


# -------------------------------
# Расчет итогового балла
# -------------------------------

def calculate_total_score(eg_score: int, achievement_score: int) -> int:
    """
    Рассчитывает общий балл пользователя.

    :param eg_score: Баллы за ЕГЭ.
    :param achievement_score: Баллы за достижения.
    :return: Итоговый балл.
    """
    return eg_score + achievement_score
