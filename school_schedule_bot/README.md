# School Schedule Bot MVP

## 1) Краткое архитектурное описание
Проект разделён на слои: `bot` (Telegram UX, FSM), `api` (FastAPI endpoints), `app/services` (use-cases), `app/repositories` (доступ к БД), `app/scheduling` (constraint/greedy/local search engine), `exports` (Excel/PDF/JSON).

## 2) Почему такой алгоритмический подход
Использован гибрид: feasibility checks -> greedy construction с учётом жёстких ограничений -> simulated annealing swap-улучшение -> penalty-based scoring. Это даёт работоспособный MVP без исторических данных, но с потенциалом ML-ранжирования позже.

## 3) Структура проекта
См. дерево в задании; реализованы все ключевые каталоги для расширения.

## 4) Основные команды
```bash
uvicorn api.main:app --reload
python -m bot.main
pytest -q
```

## 5) Выбор интеграции Bot↔Backend
Бот работает через HTTP к FastAPI (`httpx`), что отделяет UX-слой от бизнес-логики и упрощает будущую веб-панель.

## 6) Пример тестовых данных
1. Создать школу `POST /schools`.
2. Добавить классы/предметы/учителей.
3. Назначить teacher-subject и teacher-class через `POST /entities/assignments`.
4. Задать нагрузку через `POST /entities/requirements`.
5. Сгенерировать `POST /schedules/generate`.

## 7) Возможные улучшения
- OR-Tools CP-SAT для более сильного exact solving.
- Импорт исходных данных из Excel.
- Хранение top-3 альтернатив в отдельной таблице.
- Роли admin/viewer и JWT.
- Веб-панель поверх существующего API.
