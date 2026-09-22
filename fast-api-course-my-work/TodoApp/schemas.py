from pydantic import BaseModel, Field


class TodoRequest(BaseModel):
    title: str = Field(
        min_length=3, description="Naslov todo zadatka mora imati najmanje 3 karaktera"
    )
    description: str = Field(
        min_length=3, description="Opis todo zadatka mora imati najmanje 3 karaktera"
    )
    priority: int = Field(
        gt=0,
        lt=6,
        description="Prioritet todo zadatka mora biti veći od 0 i manji od 6",
    )
    complete: bool = Field(description="Status završenosti todo zadatka")
