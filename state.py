from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    name = State()
    lastname = State()
    agreement = State()
