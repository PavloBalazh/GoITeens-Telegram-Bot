from pydantic import BaseModel
class FilmModel(BaseModel):
    name : str
    description : str
    year : int
    genre : str
    rating : float
    actors : list
    poster : str
class Filter(BaseModel):
    name : str
    year : int
    genre : str
    rating : float
class SearchByActor(BaseModel):
    name : str