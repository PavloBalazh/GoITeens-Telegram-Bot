from aiogram.fsm.state import State, StatesGroup
class AddFilm(StatesGroup):
    name = State()
    description = State()
    year = State()
    genre = State()
    rating = State()
    actors = State()
    poster = State()
class Filter(StatesGroup):
    name = State()
    year = State()
    genre = State()
    rating = State()
class SearchByActor(StatesGroup):
    author = State()