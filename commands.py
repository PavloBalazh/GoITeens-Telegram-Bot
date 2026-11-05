from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand
START_COMMAND = Command("start")
START_BOTCOMMAND = BotCommand(command="start",description="start chatting")

FILM_COMMAND = Command("showfilms")
FILM_BOTCOMMAND = BotCommand(command="showfilms",description="shows you all films")

ADDFILM_COMMAND = Command("addfilm")
ADDFILM_BOTCOMMAND = BotCommand(command="addfilm",description="adds a film")

SEARCH_BY_ACTOR = Command("search_by_actor")
SEARCH_BY_ACTOR_BOTCOMMMAND = BotCommand(command="search_by_actor",description="searches films by their actors")

FILTERSEARCH = Command("filter_search")
FILTERSEARCH_BOTCOMMAND = BotCommand(command="filter_search",description="searches films by some filter")

CANCEL = Command("cancel")
CANCEL_BOTCOMMAND = BotCommand(command="cancel",description="cancels the previous command")

RETURN = Command("return")
RETURN_BOTCOMMAND = BotCommand(command="return",description="returns to the previous step")
list_bot_commands = [CANCEL_BOTCOMMAND,RETURN_BOTCOMMAND,FILM_BOTCOMMAND,ADDFILM_BOTCOMMAND,FILTERSEARCH_BOTCOMMAND,SEARCH_BY_ACTOR_BOTCOMMMAND]