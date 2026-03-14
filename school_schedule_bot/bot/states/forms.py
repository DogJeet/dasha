from aiogram.fsm.state import State, StatesGroup


class NewProjectForm(StatesGroup):
    name = State()
    days = State()
    lessons = State()


class AddTeacherForm(StatesGroup):
    school_id = State()
    full_name = State()
