# Python
from typing import Optional
from enum import Enum

# Pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr, HttpUrl
from pydantic.types import PaymentCardNumber, constr


# FastAPI
from fastapi import FastAPI
from fastapi import Body, Query, Path

app = FastAPI()

# Models

class HairColor(Enum):
    black = 'black'
    blonde = 'blonde'
    brown = 'brown'
    red = 'red'
    white = 'white'

class Location(BaseModel):
    city: str = Field(
        ...,
        min_length=1,
        max_length=58,
        example='La Plata'
    )
    state: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example='Buenos Aires'
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=21,
        example='Argentina'
    )

class Person(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example='Juan'
        )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example='Di Pasquo'
        )
    age: int = Field(
        ...,
        gt=0,
        le=115,
        example=21
    )
    hair_color: Optional[HairColor] = Field(default=None)
    is_married: Optional[bool] = Field(default=None, example=False)
    email: Optional[EmailStr] = Field(default=None, example='example@gmail.com')
    website: Optional[HttpUrl] = Field(example='http://google.com')
    card_name: constr(strip_whitespace=True, min_length=1) = Field(example='Juan Agustin Di Pasquo')
    card_number: Optional[PaymentCardNumber] = Field(example='4000000000000002')#? This number is for Visa cards

#*   This is the same as the parameter "example" from class Field
    # class Config():
    #     schema_extra = {
    #         "example": {
    #             "first_name": "Juan",
    #             "last_name": "Di Pasquo",
    #             "age": 21,
    #             "hair_color": "brown",
    #             "is_married": False
    #         }
    #     }

@app.get('/')
def home():
    return {'Hello': 'World'}

# Request and Response Body
@app.post('/person/new')
def create_person(person: Person = Body(...)):#* Los "..." significan que el parametro es OBLIGATORIO
    return person

# Validaciones: Query Parameters

@app.get('/person/detail')
def show_person(
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        title='Person Name',
        description="This is the person name. It's between 1 and 50 characters",
        example='Rocio'
        ),
    age: int = Query(
        ...,
        title='Person Age',
        description="This is the person age. It's require",
        example=25
        )
):
    return {name: age}

# Validaciones: Path Parameters

@app.get('/person/detail/{person_id}')
def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        title='Person ID',
        description='This shows person ID',
        example=123
        )
):
    return {person_id: 'It exists!'}

# Validaciones: Request Body

@app.put('/person/{person_id}')
def update_person(
    person_id: int = Path(
        ...,
        title='Person ID',
        description='This is the person ID',
        gt=0,
        example=123
    ),
    person: Person = Body(...),
    Location: Location = Body(...)
):
    results = person.dict()
    results.update(Location.dict())
    return results