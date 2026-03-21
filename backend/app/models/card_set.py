from pydantic import BaseModel, Field


PREDEFINED_CARD_SETS: dict[str, list[str]] = {
    "Fibonacci": ["1", "2", "3", "5", "8", "13", "21", "34", "55", "89", "?", "☕"],
    "Modified Fibonacci": ["0", "½", "1", "2", "3", "5", "8", "13", "20", "40", "100", "?", "☕"],
    "T-Shirt Size": ["XS", "S", "M", "L", "XL", "XXL", "?"],
    "Powers-Of-2": ["1", "2", "4", "8", "16", "32", "64", "?", "☕"],
}


# The definition of a set of voting cards for a room.
# Responsible for holding the card set's name and the ordered list
# of valid card values that participants may vote with.
class CardSet(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    cards: list[str] = Field(..., min_length=2, max_length=20)
