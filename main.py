# Python
from typing import Optional
from enum import Enum

# Pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr, HttpUrl
# from pydantic.types import PaymentCardNumber, constr

# FastAPI
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException
from fastapi import Body, Query, Path, Form, Header, Cookie, File, UploadFile

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

class PersonBase(BaseModel):
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
    # email: Optional[EmailStr] = Field(default=None, example='example@gmail.com')
    # website: Optional[HttpUrl] = Field(example='http://google.com')
    # card_name: constr(strip_whitespace=True, min_length=1) = Field(example='Juan Agustin Di Pasquo')
    # card_number: Optional[PaymentCardNumber] = Field(example='4000000000000002')#? This number is for Visa cards

class Person(PersonBase):
    password: str = Field(..., min_length=8)

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

class PersonOut(PersonBase):
    pass

class LoginOut(BaseModel):
    username: str = Field(..., max_length=20, example='Miguel2021')
    message: str = Field(default='Login Successful')


@app.get(
    path='/',
    status_code=status.HTTP_200_OK,
    tags=['Home'],
    summary='Home'
)
def home():
    """# Home

    This is the home of the app

    Returns:
    - a JSON {'Hello': 'World'} to confirm the app function
    """
    return {'Hello': 'World'}

# Request and Response Body

@app.post(
    path='/person/new',
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    tags=['Persons'],
    summary='Create person in the app'
    )
def create_person(person: Person = Body(...)):#* Los "..." significan que el parametro es OBLIGATORIO
    """
    # Create person

    This path operation creates a person in the app and saves the information in the database

    Parameters:
    - Request body parameters:
        - **person: Person** -> A person model with first name, last name, age, hair color and marital status

    Returns:
    - Person model with first name, last name, age, hair color and marital status
    """
    return person

# Validaciones: Query Parameters

@app.get(
    path='/person/detail',
    status_code=status.HTTP_200_OK,
    tags=['Persons'],
    summary='Get person details',
    deprecated=True
    )
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
    """# Show person

    This endpoint recieves a person name and age and returns a dictionary with the person information

    Parameters:
    - Query parameters:
        - **name: Optional[str]** -> Name of the person
        - **age: int(Required)** -> Age of the person

    Returns:
    - JSON with the person information {name: age}
    """
    return {name: age}

# Validaciones: Path Parameters

persons = [1, 2, 3, 4, 5]

@app.get(
    path='/person/detail/{person_id}',
    status_code = status.HTTP_202_ACCEPTED,
    tags=['Persons'],
    summary='Get person details with person_id and validate them'
    )
def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        title='Person ID',
        description='This shows person ID',
        example=123
        )
):
    """# Validate person existence with ID

    This endpoint recieves a person_id and validates whether the person exists or not

    Parameters:
    - Path parameters:
        - **gt(greater than)=0** ->The ID must be greater than cero
        - **title='Person ID'** ->The title of the section
        - **description='This shows person ID'** ->This is a description for the parameter
        - **example=123** ->This is an example to test the app

    Returns:
    - JSON with a message which defines if the validation is correct or not
    """
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This person does not exists'
        )
    return {person_id: 'It exists!'}

# Validaciones: Request Body

@app.put(
    path='/person/{person_id}',
    status_code = status.HTTP_201_CREATED,
    tags=['Persons'],
    summary='Update a person details'
    )
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
    """# Update a person details

    This endpoint recieves a person_id and updates the information of that person

    Parameters:
    - Request body parameters:
        - **...** ->This marks that the parameter is obligatory
        - **title='Person ID'** ->This is the title of the section
        - **description='This is the person ID'** ->This is a description for the parameter
        - **gt=0** ->The ID must be greater than cero
        - **example=123** ->This is an example to test the app

    Returns:
    - results = person.dict() -> Returns a dictionary with the person information
    - results.update(Location.dict()) -> Returns a dictionary with the Location of the person
    - results -> Returns a response body with person and Location simultaneously
    """
    results = person.dict()
    results.update(Location.dict())
    return results

# Forms

@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    tags=['Login','Persons'],
    summary='Login of the app'
)
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """# Login

    This endpoint returns the login of a person

    - Form parameters:
        - **username (str, required)** ->This is the username for the login.
        - **password (str, required)** ->This is the password for the login.

    Returns:
    - LoginOut(username=username): This returns the username and a message of login successful
    """
    return LoginOut(username=username)

# Cookies and Headers parameters

@app.post(
    path='/contact',
    status_code=status.HTTP_200_OK,
    tags=['Contact']
)
def contact(
    first_name: str = Form(
        ...,
        max_length=20,
        min_length=1
    ),
    last_name: str = Form(
        ...,
        max_length=20,
        min_length=1
    ),
    email: EmailStr = Form(...),
    message: str = Form(
        ...,
        min_length=20
    ),
    user_agent: Optional[str] = Header(default=None),
    ads: Optional[str] = Cookie(default=None)
):
    """# Contact

    This endpoint returns a person message with the contact

    Parameters
    - Form parameters:
        - **first_name (str, required)** -> First name of person.
        - **last_name (str, required)** -> Last name of person.
        - **email (EmailStr, required)** -> Email of the peson.
        - **message (str, required)** -> Message of the person.
    - Header parameters:
        - **user_agent (Optional[str], optional)** -> User agent of the browser used by the person.
    - Cookie parameters:
        - **ads (Optional[str], optional)** ->Cookies at browser.

    Returns:
    - The user agent
    """
    return user_agent

# Files

@app.post(
    path='/post-image',
    tags=['Posts'],
    summary='Post image'
)
def post_image(
    image: UploadFile = File(...)
):
    """# Upload an image

    Parameters
    - File parameters:
        - **image (UploadFile, required)** -> Tool to upload an image

    Returns:
    - Returns a json with the file name, the format and the size of it in kilobytes
    """
    return {
        'Filename': image.filename,
        'Format': image.content_type,
        'Size(kb)': round(len(image.file.read())/1024, ndigits=2)
    }