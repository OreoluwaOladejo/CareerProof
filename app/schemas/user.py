from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator


class UserCreate(BaseModel):
    email: EmailStr
    '''This tells Pydantic to run this function as a validator for the email field.
      "email" specifies which field to validate.
      "mode="before" means the function runs before Pydantic's normal validation
       of the field's type and constraints.'''
    @field_validator("email", mode="before")
    #This says the method/function you are reatig uses a class 
    #That is why when it uses cls it knows immeiately where to search 
    #We already defined it as a class method
    #And when you have value 
    #It looks for the value in that class which is email
    @classmethod
    def normalize_email(cls, value):
        # mode="before" means this runs BEFORE the email format check,
        # so " Ada@X.com " becomes "ada@x.com" first. Lowercasing here
        # means every layer after this only ever sees the clean version,
        # which is what makes the unique constraint behave correctly.

        #iisinstance checks whether the value given is a string 
        if isinstance(value, str):
            #strip()-removes spaces
            #.lower()-makes it lower case
            return value.strip().lower()
        return value

    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    # What the API sends back about a user. Note what is MISSING:
    # password_hash. Only the fields listed here can ever be returned.
    # from_attributes=True lets Pydantic read these values straight off
    # a SQLAlchemy User object instead of requiring a dictionary.

    #If I give you an object, you are allowed to read its attributes to get the information you need."
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime