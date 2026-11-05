import asyncio
import logging
import sys
import math
from aiogram import Bot, Dispatcher, html
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from commands import *
from data import read,add_film
from states import AddFilm, SearchByActor,Filter
from aiogram.types import ReplyKeyboardRemove
dp = Dispatcher()
genres = ["comedy","thriller","detective","fantasy","horror","action","sci-fi","romance","musical"]
dp["m"] = "None"
dp["page2"] = 1
dp["page3"] = 1
dp["page"] = 1
dp["state"] = 0
dp["max_page"] = 2
dp["max_page2"] = math.ceil(len(genres) / 6)
async def stylize(data,message):
    film = data
    film_name = film["name"]
    film_year = film["year"]
    film_rating = film["rating"]
    film_description = film["description"]
    film_genre = film["genre"]
    film_actors = film["actors"]
    film_poster = film["poster"]
    text = f"""
{html.bold(film_name)}

{film_description}

Year: {film_year}
Rating: {film_rating}
Genre: {film_genre}
Actors: {", ".join(film_actors)}
{film_poster}
"""
    await message.answer(text)
TOKEN = "Enter your token"
def make_reply_keyboard(n=0):
    data = read()
    dp["max_page"] = math.ceil(len(data) / 4)
    builder = ReplyKeyboardBuilder()
    if n == 0:
        buttons = [film["name"] +" film" for film in data[(int(dp["page"])-1)*4:int(dp["page"])*4]]
        if len(buttons) % 2 == 1:
            buttons.append(" ")
        if dp["page"] > 1:
            buttons.append("<---")
        if dp["page"] < dp["max_page"]:
            buttons.append("--->")
    elif n == 2:
        buttons = ["Next step.","Delete previous actor."]
    for i in buttons:
        builder.add(KeyboardButton(text=i))
    builder.adjust(2)
    return builder.as_markup()    
def make_inline_keyboard(n):
    builder = InlineKeyboardBuilder()
    if n == 0:
        buttons = ["name","rating","year","genre"]
    elif n == 1 or n == 4:
        if n == 1:
            buttons = [genre for genre in genres[(dp["page2"]-1) * 6 : dp["page2"] * 6]]
        else:
            buttons = [genre for genre in genres[(dp["page3"]-1) * 6 : dp["page3"] * 6]]
        if len(buttons) % 3 == 1:
            buttons.append(" ")
        if len(buttons) % 3 == 2:
            buttons.append(" ")
        buttons.append("<---")
        buttons.append("--->")
    elif n == 2 or n == 3:
        buttons = ["Lower","Higher"]
    for i in buttons:
        if n == 0:
            builder.button(text=i,callback_data=f"filters_{i}")
            builder.adjust(3)
        elif n == 1:
            builder.button(text=i,callback_data=f"genres_{i}")
            builder.adjust(3)
        elif n == 2:
            builder.button(text=i,callback_data=f"spec_{i}")
            builder.adjust(2)
        elif n == 3:
            builder.button(text=i,callback_data=f"Spec_{i}")
            builder.adjust(2)
        elif n == 4:
            builder.button(text=i,callback_data=f"genrescreate_{i}")
            builder.adjust(3)
    return builder.as_markup()

@dp.message(RETURN)
async def return_state(message,state:FSMContext):
    save = await state.get_state()
    if save == AddFilm.year:
        await message.answer("Enter a films name:")
        await state.set_state(AddFilm.name)
    elif save == AddFilm.rating:
        await message.answer("Enter a films year:")
        await state.set_state(AddFilm.year)
    elif save == AddFilm.description:
        await message.answer("Enter a films rating:")
        await state.set_state(AddFilm.rating)
    elif save == AddFilm.actors:
        await message.answer("Enter a description:")
        await state.set_state(AddFilm.description)
    elif save == AddFilm.poster:
        await message.answer("Enter actors name and/or surname:",reply_markup=make_reply_keyboard(2))
        await state.set_state(AddFilm.actors)
    elif save == AddFilm.genre:
        await message.answer("Enter a poster's URL:")
        await state.set_state(AddFilm.poster)
    elif "Filter" in str(save):
        await message.answer("Choose a thing to filter with:",reply_markup=make_inline_keyboard(0))
    else:
        await message.answer("There is nothing to return.")

@dp.message(CANCEL)
async def cancel(message,state:FSMContext):
    await message.answer("Cancelled the previous command!",reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(AddFilm.name)
async def addyear(message,state: FSMContext):
    film_name = message.text
    films = read()
    dp["m"] = 0
    for film in films:
        if film["name"] == film_name:
            await message.answer("That film name already exists. Try another one")
            dp["m"] = 1
            break
        elif "/" in message.text:
            await message.answer("You can't create film names with the character '/'.")
            dp["m"] = 1
            break
    if dp["m"] == 0:
        await state.update_data(name=message.text)
        await message.answer("Enter a films year")
        await state.set_state(AddFilm.year)

@dp.message(AddFilm.year)
async def addrating(message,state: FSMContext):
    try:
        if int(message.text) > 1800 and int(message.text) < 2027:
            await state.update_data(year=int(message.text))
            await message.answer("Enter a rating")
            await state.set_state(AddFilm.rating)
        else:
            await message.answer("Film cant be created that year.")
    except ValueError:
        await message.answer("Incorrect year number.")

@dp.message(AddFilm.rating)
async def adddesc(message,state: FSMContext):
    try:
        m = float(message.text)
    except ValueError:
        await message.answer("Incorrect rating type.(ex. 4.3)")
    if m <= 0 or m > 10:
        await message.answer("You can only enter ratings in range from 1 to 10.")
    else:
        await state.update_data(rating=m)
        await message.answer("Enter a description:")
        await state.set_state(AddFilm.description)

@dp.message(AddFilm.description)
async def addgenre(message,state):
    await state.update_data(description=message.text)
    await message.answer("Enter actors name and/or surname:",reply_markup=make_reply_keyboard(2))
    await state.set_state(AddFilm.actors)

@dp.message(AddFilm.actors,F.text == "Next step.")
async def contin(message,state):
    data = await state.get_data()
    film_actors = data.get("actors", [])
    if len(film_actors) > 0:
        await state.set_state(AddFilm.poster)
        await message.answer(f"Enter a poster's URL:",reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Minimum one actor required.")
@dp.message(AddFilm.actors,F.text == "Delete previous actor.")
async def contin(message,state):
    data = await state.get_data()
    if len(data.get("actors",[])) != 0:
        data.get("actors",[]).pop(len(data.get("actors",[])) - 1)
        await message.answer("Deleted the last actor.")
    else:
        await message.answer("There is no actors to delete!")
@dp.message(AddFilm.actors)
async def adddesc(message,state: FSMContext):
    data = await state.get_data()
    film_actors = data.get("actors", [])
    await message.answer("Succesfully added actor.")
    film_actors.append(message.text)
    await state.update_data(actors=film_actors)

@dp.message(AddFilm.poster)
async def addgenre(message,state):
    await state.update_data(poster=message.text)
    await message.answer(f"Choose a genre to create a film:",reply_markup=make_inline_keyboard(4))
    await state.set_state(AddFilm.genre)

@dp.callback_query(AddFilm.genre,F.data.startswith("genrescreate_"))
async def genres1(call,state):
    m = call.data.split("genrescreate_")[1]
    dp["m"] = str(m)
    if m == "--->":
        if dp["max_page2"] == dp["page3"]:
            await call.message.answer("You have reached the last page.")
        else:
            dp["page3"] += 1
            await call.message.edit_text(text="Choose a genre to create a film:",reply_markup=make_inline_keyboard(4))
    elif m == "<---":
        if dp["page3"] == 1:
            await call.message.answer("You have reached the first page.")
        else:
            dp["page3"] -= 1
            await call.message.edit_text(text="Choose a genre to create a film:",reply_markup=make_inline_keyboard(4))
    else:
        await call.message.answer(f"You chose {m}")
        await state.update_data(genre=dp["m"])
        content = await state.get_data()
        add_film(content)
        await call.message.answer(f"Succesfully added Film: {content["name"]}.",reply_markup=make_reply_keyboard(0))
        await state.clear()
        dp["state"] = 0
        dp["page3"] = 1

@dp.message(AddFilm.poster)
async def warning(call):
    await call.answer("You are still creating a film. Finish creating it to use other commands.")
@dp.message(ADDFILM_COMMAND)
async def addfilm(message,state: FSMContext):
    await message.answer("Enter a films name:",reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddFilm.name)

@dp.message(FILM_COMMAND)
async def make_keyboard(message):
    await message.answer(text="Choose the film you want to get more info about.",reply_markup=make_reply_keyboard(0))

@dp.message(F.text.endswith(" film"))
async def test2(message):
    filmdata = read()
    for film in filmdata:
        if film["name"] + " film" == message.text:
            film_name = film["name"]
            film_year = film["year"]
            film_rating = film["rating"]
            film_description = film["description"]
            film_genre = film["genre"]
            film_actors = film["actors"]
            film_poster = film["poster"]
            text = f"""
{html.bold(film_name)}

{film_description}

Year: {film_year}
Rating: {film_rating}
Genre: {film_genre}
Actors: {", ".join(film_actors)}
{film_poster}"""
            await message.answer(text)
            break

@dp.message(F.text == ("<---"))
async def backwards(message):
    if dp["page"] > 1:
        dp["page"] -= 1
        await message.answer(f"Page {dp["page"]}.",reply_markup=make_reply_keyboard())
    else:
        await message.answer("You cannot go lower than one.")

@dp.message(F.text == ("--->"))
async def forwards(message):
    if dp["page"] < dp["max_page"]:
        dp["page"] += 1
        await message.answer(f"Page {dp["page"]}.",reply_markup=make_reply_keyboard())
    else:
        await message.answer("You've reached the last page.")

@dp.message(FILTERSEARCH)
async def filtersearch(message):
    await message.answer("Choose a thing to filter with:",reply_markup=make_inline_keyboard(0))
@dp.callback_query(F.data.startswith("filters_"))
async def inline_keyboard(call,state: FSMContext):
    callback = call.data.split("filters_")[1]
    if callback == "name":
        await state.set_state(Filter.name)
        await call.message.answer("Enter a name to filter with:")
    elif callback == "year":
        await state.set_state(Filter.year)
        await call.message.answer("Enter a year to filter with:")
    elif callback == "rating":
        await state.set_state(Filter.rating)
        await call.message.answer("Enter a rating to filter with:")
    elif callback == "genre":
        await state.set_state(Filter.genre)
        await call.message.answer("Choose a genre to filter with:",reply_markup=make_inline_keyboard(1))
    elif callback == "cancel":
        await call.message.answer(f"You cancelled your filter search.")

@dp.callback_query(F.data.startswith("genres_"))
async def genres1(call):
    m = call.data.split("genres_")[1]
    data = read()
    i = 0
    done = 0
    if m == "--->":
        if dp["max_page2"] == dp["page2"]:
            await call.message.answer("You have reached the last page.")
        else:
            dp["page2"] += 1
            await call.message.edit_text(text="Choose a genre to filter with:",reply_markup=make_inline_keyboard(1))
    elif m == "<---":
        if dp["page2"] == 1:
            await call.message.answer("You have reached the first page.")
        else:
            dp["page2"] -= 1
            await call.message.edit_text(text="Choose a genre to filter with:",reply_markup=make_inline_keyboard(1))
    else:
        for film in data:
            if film["genre"] == m:
                if done == 0:
                    await call.message.answer(f"Film found by genre:")
                    done = 1
                await stylize(data[i],call.message)
            i += 1
        if done == 0:
            await call.message.answer("No films found.")
            done = 1
    dp["page2"] = 1

@dp.message(Filter.name)
async def name_filter(message,state):
    m = message.text
    data = read()
    i = 0
    n = 0
    for film in data:
        if m.lower() in film["name"].lower():
            if n == 0:
                await message.answer(f"film found by name:")
            await stylize(data[i],message)
            n = 1
        i += 1
    if n == 0:
        await message.answer("no films found")
    await state.clear()
@dp.message(Filter.year)
async def year_filter(message):
    try:
        dp["m"] = int(message.text)
    except ValueError:
        await message.answer("Incorrect year input!")
    if dp["m"] < 2027 and dp["m"] > 1800:
        await message.answer(f"Search by lower than {dp["m"]} or higher?",reply_markup=make_inline_keyboard(2))
    else:
        await message.answer("Invalid year input. The range is from 1801 to 2026.")
@dp.callback_query(F.data.startswith("spec_"))
async def specify_year(call,state):
    callback = call.data.split("spec_")[1]
    data = read()
    i = 0
    n = 0
    for film in data:
        if film["year"] <= dp["m"] and callback == "Lower" or film["year"] >= dp["m"] and callback == "Higher":
            await stylize(data[i],call.message)
            if n == 0:
                await call.message.answer(f"Films found by year:")
            n = 1
        i += 1
    if n == 0:
        await call.message.answer("No films found.")
    await state.clear()
@dp.message(Filter.rating)
async def rating_filter(message):
    try:
        dp["m"] = float(message.text)
    except ValueError:
        await message.answer("Incorrect rating input (ex. 5.6)!")
    if dp["m"] < 10 and dp["m"] > 1:
        await message.answer(f"Search by lower than {dp["m"]} or higher?",reply_markup=make_inline_keyboard(3))
    else:
        await message.answer("Invalid rating input. The range is from 1 to 10!")
@dp.callback_query(F.data.startswith("Spec_"))
async def specify_rating(call,state):
    callback = call.data.split("Spec_")[1]
    data = read()
    i = 0
    n = 0
    for film in data:
        if film["rating"] <= dp["m"] and callback == "Lower" or film["rating"] >= dp["m"] and callback == "Higher":
            await stylize(data[i],call.message)
            if n == 0:
                await call.message.answer(f"Films found by rating:")
            n = 1
        i += 1
    if n == 0:
        await call.message.answer("No films found.")
    await state.clear()
@dp.message(SEARCH_BY_ACTOR)
async def search(message,state):
    await message.answer("Enter actor's name:")
    await state.set_state(SearchByActor.author)

@dp.message(SearchByActor.author)
async def search2(message,state):
    data = read()
    m = message.text
    i = 0
    found = False
    for film in data:
        text = ""
        for actor in film["actors"]:
            if m.lower() in actor.lower():
                if not found:
                    await message.answer(f'Films found by actor "{m}":')
                found = True
                film = data[i]
                film_name = film["name"]
                film_year = film["year"]
                film_rating = film["rating"]
                film_description = film["description"]
                film_genre = film["genre"]
                film_actors = film["actors"]
                film_poster = film["poster"]
                text = f"""
{html.bold(film_name)}
        
{film_description}

Year: {film_year}
Rating: {film_rating}
Genre: {film_genre}
Actors: {", ".join(film_actors)}
{film_poster}
"""
                await message.answer(text)
                break
        i += 1
    if not found:
        await message.answer(f'No films found by actor "{m}". ')
    await state.clear()
@dp.message(START_COMMAND)
async def test(message):
    await message.answer("Hello!")
    await message.answer(f"This is a {html.bold('Film Bot')}.")

@dp.message()
async def invalid(message):
    await message.answer("This isn't a command.")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands([command for command in list_bot_commands])
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
