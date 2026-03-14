from telegram import Update
from telegram.ext import *

import logging
import os
from collections import defaultdict
from copy import deepcopy

# -----------------------------
# Глобальные хранилища данных
# -----------------------------
classes = {}
teachers = {}
subjects = {}
loads = defaultdict(dict)
schedule = {}

# Настройки недели
settings = {
    "days": 5,
    "lessons_per_day": 6,
}

DAY_NAMES = [
    "ПОНЕДЕЛЬНИК",
    "ВТОРНИК",
    "СРЕДА",
    "ЧЕТВЕРГ",
    "ПЯТНИЦА",
    "СУББОТА",
    "ВОСКРЕСЕНЬЕ",
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# -----------------------------
# Вспомогательные функции
# -----------------------------
def generate_time_slots(days_count: int, lessons_per_day: int):
    """Генерирует список временных слотов (день, номер урока)."""
    day_list = DAY_NAMES[:days_count]
    slots = []
    for day in day_list:
        for lesson_num in range(1, lessons_per_day + 1):
            slots.append((day, lesson_num))
    return slots


def check_conflicts(
    day: str,
    lesson_num: int,
    class_name: str,
    teacher_name: str,
    teacher_busy: dict,
    class_busy: dict,
):
    """Проверяет конфликты по учителю и классу в конкретном слоте."""
    slot_key = (day, lesson_num)

    if teacher_name in teacher_busy and slot_key in teacher_busy[teacher_name]:
        return True

    if class_name in class_busy and slot_key in class_busy[class_name]:
        return True

    return False


def score_schedule(schedule_data: dict):
    """
    Простая метрика качества расписания.
    Чем выше, тем лучше.

    Логика:
    - штраф за "окна" у класса в пределах дня
    - штраф за два одинаковых предмета подряд у класса
    """
    if not schedule_data:
        return -10_000

    class_day_lessons = defaultdict(lambda: defaultdict(dict))

    for day, lessons in schedule_data.items():
        for lesson_num, entries in lessons.items():
            for item in entries:
                class_day_lessons[item["class"]][day][lesson_num] = item["subject"]

    score = 0

    for class_name, days_data in class_day_lessons.items():
        for day, day_lessons in days_data.items():
            lesson_numbers = sorted(day_lessons.keys())
            if not lesson_numbers:
                continue

            # Штраф за окна (пустые места между первым и последним уроком)
            min_l = lesson_numbers[0]
            max_l = lesson_numbers[-1]
            placed = set(lesson_numbers)
            for num in range(min_l, max_l + 1):
                if num not in placed:
                    score -= 2

            # Штраф за повтор предмета подряд
            for i in range(len(lesson_numbers) - 1):
                l1 = lesson_numbers[i]
                l2 = lesson_numbers[i + 1]
                if l2 == l1 + 1 and day_lessons[l1] == day_lessons[l2]:
                    score -= 1

    return score


def create_schedule():
    """
    Создает расписание на основе введенных данных.
    Возвращает: (ok: bool, message: str)
    """
    global schedule

    if not classes:
        return False, "Нет классов. Добавьте хотя бы один класс через /add_class"
    if not subjects:
        return False, "Нет предметов. Добавьте хотя бы один предмет через /add_subject"
    if not teachers:
        return False, "Нет учителей. Добавьте хотя бы одного учителя через /add_teacher"

    # Карта: предмет -> список учителей
    subject_teachers = defaultdict(list)
    for teacher_name, t_data in teachers.items():
        for subj in t_data["subjects"]:
            subject_teachers[subj].append(teacher_name)

    # Проверка, что для всех предметов нагрузки есть учитель
    for class_name, class_loads in loads.items():
        for subj, hours in class_loads.items():
            if hours <= 0:
                continue
            if subj not in subject_teachers:
                return False, f"Для предмета '{subj}' не найден учитель"

    lessons_to_place = []
    # Разворачиваем нагрузки в отдельные уроки
    for class_name, class_loads in loads.items():
        for subj, hours in class_loads.items():
            for _ in range(hours):
                lessons_to_place.append(
                    {
                        "class": class_name,
                        "subject": subj,
                        "teacher_options": subject_teachers.get(subj, []),
                    }
                )

    if not lessons_to_place:
        return False, "Нет учебной нагрузки. Используйте /set_load"

    # Сначала размещаем более "сложные" уроки (где меньше выбор учителей)
    lessons_to_place.sort(key=lambda x: len(x["teacher_options"]))

    slots = generate_time_slots(settings["days"], settings["lessons_per_day"])
    if not slots:
        return False, "Неверные настройки количества дней/уроков"

    tentative_schedule = {day: {n: [] for n in range(1, settings["lessons_per_day"] + 1)} for day in DAY_NAMES[: settings["days"]]}

    teacher_busy = defaultdict(set)
    class_busy = defaultdict(set)
    class_subject_day_count = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    unplaced = []

    # Greedy размещение
    for lesson in lessons_to_place:
        c_name = lesson["class"]
        subj = lesson["subject"]
        options = lesson["teacher_options"]

        placed = False
        best_choice = None
        best_penalty = 10**9

        for day, lesson_num in slots:
            for teacher_name in options:
                if check_conflicts(day, lesson_num, c_name, teacher_name, teacher_busy, class_busy):
                    continue

                # Небольшая эвристика: избегать много одинакового предмета в один день
                same_subject_today = class_subject_day_count[c_name][day][subj]
                penalty = same_subject_today * 3

                # Небольшой штраф за поздние уроки
                penalty += lesson_num

                if penalty < best_penalty:
                    best_penalty = penalty
                    best_choice = (day, lesson_num, teacher_name)

        if best_choice is None:
            unplaced.append((c_name, subj))
            continue

        day, lesson_num, teacher_name = best_choice

        entry = {
            "class": c_name,
            "subject": subj,
            "teacher": teacher_name,
        }
        tentative_schedule[day][lesson_num].append(entry)
        teacher_busy[teacher_name].add((day, lesson_num))
        class_busy[c_name].add((day, lesson_num))
        class_subject_day_count[c_name][day][subj] += 1
        placed = True

        if not placed:
            unplaced.append((c_name, subj))

    if unplaced:
        sample = ", ".join([f"{c}-{s}" for c, s in unplaced[:5]])
        return (
            False,
            f"Не удалось полностью составить расписание. Неразмещено: {len(unplaced)}. Примеры: {sample}",
        )

    current_score = score_schedule(tentative_schedule)

    # Легкая локальная оптимизация: пробуем переставить пары уроков, если улучшает score
    optimized = deepcopy(tentative_schedule)
    improved = True
    while improved:
        improved = False
        days = list(optimized.keys())
        for d1 in days:
            for l1 in optimized[d1]:
                for d2 in days:
                    for l2 in optimized[d2]:
                        if (d1, l1) == (d2, l2):
                            continue

                        a = optimized[d1][l1]
                        b = optimized[d2][l2]

                        # Для простоты меняем только если в каждом слоте по 1 записи
                        if len(a) != 1 or len(b) != 1:
                            continue

                        a_item = a[0]
                        b_item = b[0]

                        # После swap нужно проверить конфликты
                        # Создаем временную копию без двух элементов
                        temp = deepcopy(optimized)
                        temp[d1][l1] = [b_item]
                        temp[d2][l2] = [a_item]

                        if _has_any_conflict(temp):
                            continue

                        new_score = score_schedule(temp)
                        if new_score > current_score:
                            optimized = temp
                            current_score = new_score
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    schedule = optimized
    return True, "Расписание успешно создано"


def _has_any_conflict(schedule_data: dict):
    """Проверка конфликтов во всем расписании."""
    teacher_busy = defaultdict(set)
    class_busy = defaultdict(set)

    for day, lessons in schedule_data.items():
        for lesson_num, entries in lessons.items():
            slot = (day, lesson_num)
            for item in entries:
                c_name = item["class"]
                t_name = item["teacher"]

                if slot in teacher_busy[t_name]:
                    return True
                if slot in class_busy[c_name]:
                    return True

                teacher_busy[t_name].add(slot)
                class_busy[c_name].add(slot)

    return False


# -----------------------------
# Telegram handlers
# -----------------------------
def start(update: Update, context: CallbackContext):
    text = (
        "Привет! Я бот для автоматического создания школьного расписания.\n\n"
        "Команды:\n"
        "/help — инструкция\n"
        "/add_class <название>\n"
        "/add_subject <название>\n"
        "/add_teacher <ФИО> <предмет1,предмет2,...>\n"
        "/set_load <класс> <предмет> <часы_в_неделю>\n"
        "/set_days <кол-во_дней>\n"
        "/set_lessons <уроков_в_день>\n"
        "/show_data\n"
        "/generate\n"
        "/show_schedule [класс]\n"
        "/reset"
    )
    update.message.reply_text(text)


def help_command(update: Update, context: CallbackContext):
    text = (
        "Инструкция:\n"
        "1) Добавьте классы: /add_class 7A\n"
        "2) Добавьте предметы: /add_subject Математика\n"
        "3) Добавьте учителей с предметами: /add_teacher Иванов Математика,Алгебра\n"
        "4) Задайте нагрузку: /set_load 7A Математика 4\n"
        "5) (Опционально) Настройки недели: /set_days 5, /set_lessons 6\n"
        "6) Сгенерируйте: /generate\n"
        "7) Посмотрите расписание: /show_schedule или /show_schedule 7A"
    )
    update.message.reply_text(text)


def add_class(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Ошибка: используйте /add_class <название>")
        return

    class_name = " ".join(context.args).strip()
    if class_name in classes:
        update.message.reply_text("Класс уже существует")
        return

    classes[class_name] = {"name": class_name}
    update.message.reply_text("Класс добавлен")


def add_subject(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Ошибка: используйте /add_subject <название>")
        return

    subj = " ".join(context.args).strip()
    if subj in subjects:
        update.message.reply_text("Предмет уже существует")
        return

    subjects[subj] = {"name": subj}
    update.message.reply_text("Предмет добавлен")


def add_teacher(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text(
            "Ошибка: используйте /add_teacher <ФИО> <предмет1,предмет2,...>"
        )
        return

    teacher_name = context.args[0]
    subject_str = " ".join(context.args[1:])
    teacher_subjects = [s.strip() for s in subject_str.split(",") if s.strip()]

    if not teacher_subjects:
        update.message.reply_text("Ошибка: не указаны предметы")
        return

    # Автоматически добавляем предметы, если их еще нет
    for subj in teacher_subjects:
        if subj not in subjects:
            subjects[subj] = {"name": subj}

    teachers[teacher_name] = {
        "name": teacher_name,
        "subjects": set(teacher_subjects),
    }

    update.message.reply_text("Учитель добавлен")


def set_load(update: Update, context: CallbackContext):
    if len(context.args) < 3:
        update.message.reply_text(
            "Ошибка: используйте /set_load <класс> <предмет> <часы_в_неделю>"
        )
        return

    class_name = context.args[0]
    hours_raw = context.args[-1]
    subject_name = " ".join(context.args[1:-1]).strip()

    if class_name not in classes:
        update.message.reply_text("Ошибка: такого класса нет")
        return

    if subject_name not in subjects:
        update.message.reply_text("Ошибка: такого предмета нет")
        return

    try:
        hours = int(hours_raw)
        if hours < 0:
            raise ValueError
    except ValueError:
        update.message.reply_text("Ошибка: часы должны быть целым числом >= 0")
        return

    loads[class_name][subject_name] = hours
    update.message.reply_text("Нагрузка сохранена")


def set_days(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Ошибка: используйте /set_days <1-7>")
        return

    try:
        days = int(context.args[0])
    except ValueError:
        update.message.reply_text("Ошибка: нужно число от 1 до 7")
        return

    if not 1 <= days <= 7:
        update.message.reply_text("Ошибка: нужно число от 1 до 7")
        return

    settings["days"] = days
    update.message.reply_text(f"Количество учебных дней установлено: {days}")


def set_lessons(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Ошибка: используйте /set_lessons <1-12>")
        return

    try:
        lessons_per_day = int(context.args[0])
    except ValueError:
        update.message.reply_text("Ошибка: нужно число от 1 до 12")
        return

    if not 1 <= lessons_per_day <= 12:
        update.message.reply_text("Ошибка: нужно число от 1 до 12")
        return

    settings["lessons_per_day"] = lessons_per_day
    update.message.reply_text(f"Уроков в день установлено: {lessons_per_day}")


def show_data(update: Update, context: CallbackContext):
    lines = []

    lines.append("КЛАССЫ:")
    if classes:
        for c in classes:
            lines.append(f"- {c}")
    else:
        lines.append("(пусто)")

    lines.append("\nПРЕДМЕТЫ:")
    if subjects:
        for s in subjects:
            lines.append(f"- {s}")
    else:
        lines.append("(пусто)")

    lines.append("\nУЧИТЕЛЯ:")
    if teachers:
        for t_name, t_data in teachers.items():
            subj_list = ", ".join(sorted(t_data["subjects"]))
            lines.append(f"- {t_name}: {subj_list}")
    else:
        lines.append("(пусто)")

    lines.append("\nНАГРУЗКА:")
    if loads:
        for c_name, c_loads in loads.items():
            if not c_loads:
                lines.append(f"- {c_name}: (нет)")
            for subj, h in c_loads.items():
                lines.append(f"- {c_name}: {subj} — {h} ч/нед")
    else:
        lines.append("(пусто)")

    lines.append("\nНАСТРОЙКИ:")
    lines.append(f"- Учебных дней: {settings['days']}")
    lines.append(f"- Уроков в день: {settings['lessons_per_day']}")

    update.message.reply_text("\n".join(lines))


def generate(update: Update, context: CallbackContext):
    ok, msg = create_schedule()
    update.message.reply_text(msg)


def _format_schedule_for_class(class_name: str):
    if not schedule:
        return "Расписание пока не создано"

    lines = [f"Расписание для класса {class_name}:"]
    found_any = False

    for day in DAY_NAMES[: settings["days"]]:
        day_lines = []
        for lesson_num in range(1, settings["lessons_per_day"] + 1):
            entries = schedule.get(day, {}).get(lesson_num, [])
            for item in entries:
                if item["class"] == class_name:
                    day_lines.append(
                        f"{lesson_num} урок — {item['subject']} — {item['teacher']}"
                    )
        if day_lines:
            found_any = True
            lines.append(f"\n{day}")
            lines.extend(day_lines)

    if not found_any:
        return f"Для класса {class_name} уроков не найдено"

    return "\n".join(lines)


def _format_full_schedule():
    if not schedule:
        return "Расписание пока не создано"

    lines = []
    for day in DAY_NAMES[: settings["days"]]:
        lines.append(day)
        has_any = False

        for lesson_num in range(1, settings["lessons_per_day"] + 1):
            entries = schedule.get(day, {}).get(lesson_num, [])
            if not entries:
                continue
            has_any = True
            for item in entries:
                lines.append(
                    f"{lesson_num} урок — {item['class']} — {item['subject']} — {item['teacher']}"
                )

        if not has_any:
            lines.append("(уроков нет)")
        lines.append("")

    return "\n".join(lines).strip()


def show_schedule_command(update: Update, context: CallbackContext):
    if context.args:
        class_name = " ".join(context.args).strip()
        if class_name not in classes:
            update.message.reply_text("Ошибка: такого класса нет")
            return
        text = _format_schedule_for_class(class_name)
    else:
        text = _format_full_schedule()

    # Telegram ограничивает длину сообщения, разобьем на части при необходимости
    max_len = 3900
    if len(text) <= max_len:
        update.message.reply_text(text)
    else:
        for i in range(0, len(text), max_len):
            update.message.reply_text(text[i : i + max_len])


def reset(update: Update, context: CallbackContext):
    classes.clear()
    teachers.clear()
    subjects.clear()
    loads.clear()
    schedule.clear()

    settings["days"] = 5
    settings["lessons_per_day"] = 6

    update.message.reply_text("Все данные очищены")


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Неизвестная команда. Используйте /help")


def _get_command_filter():
    """Совместимость фильтра команд, с приоритетом для PTB 13.5."""
    # PTB 13.x
    if "Filters" in globals() and hasattr(Filters, "command"):
        return Filters.command
    # PTB 20+
    if "filters" in globals() and hasattr(filters, "COMMAND"):
        return filters.COMMAND
    raise RuntimeError("Не удалось определить фильтр команд для текущей версии telegram.ext")


def _register_handlers(add_handler):
    """Регистрирует все handlers в переданный add_handler (app.add_handler / dispatcher.add_handler)."""
    add_handler(CommandHandler("start", start))
    add_handler(CommandHandler("help", help_command))
    add_handler(CommandHandler("add_class", add_class))
    add_handler(CommandHandler("add_teacher", add_teacher))
    add_handler(CommandHandler("add_subject", add_subject))
    add_handler(CommandHandler("set_load", set_load))
    add_handler(CommandHandler("set_days", set_days))
    add_handler(CommandHandler("set_lessons", set_lessons))
    add_handler(CommandHandler("show_data", show_data))
    add_handler(CommandHandler("generate", generate))
    add_handler(CommandHandler("show_schedule", show_schedule_command))
    add_handler(CommandHandler("reset", reset))
    add_handler(MessageHandler(_get_command_filter(), unknown))


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN. Установите переменную окружения и запустите снова."
        )

    logger.info("Бот запущен")

    # Приоритет: python-telegram-bot 13.5 (ваш случай)
    if "Updater" in globals():
        updater = Updater(token, use_context=True)
        _register_handlers(updater.dispatcher.add_handler)
        updater.start_polling()
        updater.idle()
        return

    # Fallback для PTB 20+
    if "ApplicationBuilder" in globals():
        app = ApplicationBuilder().token(token).build()
        _register_handlers(app.add_handler)
        app.run_polling()
        return

    raise RuntimeError("В telegram.ext не найдены Updater/ApplicationBuilder")


if __name__ == "__main__":
    main()
