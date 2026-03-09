from pydantic import BaseModel, Field


PREDEFINED_CARD_SETS: dict[str, list[str]] = {
    "Fibonacci": ["1", "2", "3", "5", "8", "13", "21", "34", "55", "89", "?", "☕"],
    "T-Shirt": ["XS", "S", "M", "L", "XL", "XXL", "?"],
    "Powers-of-2": ["1", "2", "4", "8", "16", "32", "64", "?", "☕"],
}


class CardSet(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    cards: list[str] = Field(..., min_length=2, max_length=20)
