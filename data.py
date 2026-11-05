import json
from models import FilmModel
if __name__ == "__init__":
    pass
default_path = "data.json"
def read(file_path=default_path):
    with open(file_path, "r",encoding="utf-8") as file:
        return json.load(file)
def add_film(film_data,file_path=default_path):
    data = read(file_path)
    data.append(FilmModel(**film_data).model_dump(mode="json"))

    with open(file_path,"w",encoding="utf-8") as file:
        json.dump(data,file,ensure_ascii=False,indent=4)

def set_films(file_path=default_path):
    data = def_data
    with open(file_path,"w",encoding="utf-8") as file:
        json.dump(data,file,ensure_ascii=False,indent=4)
def_data = read()
def_data = def_data[:7]
set_films()