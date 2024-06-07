from aiogram.fsm.state import StatesGroup, State


class ChoiceDesign(StatesGroup):
    form_state = State()


class AdminState(StatesGroup):
    change = State()
    change_main = State()
    change_main_text = State()
    change_main_image = State()
    change_info_service = State()
    change_info_service_text = State()
    change_info_service_image = State()
    change_service = State()
    change_palette = State()
    current_informathion = State()
    social_links = State()
    change_link = State()
    access_change_test = State()
    create_new_test_questions = State()
    create_new_test_answer = State()
    create_new_question_or_not = State()
    change_image_design = State()

