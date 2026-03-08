import pytest
from pydantic import ValidationError

from app.models.card_set import CardSet, PREDEFINED_CARD_SETS


class TestCardSet:
    def test_valid_card_set(self):
        cs = CardSet(name="custom", cards=["1", "2", "3"])
        assert cs.name == "custom"
        assert len(cs.cards) == 3

    def test_name_required(self):
        with pytest.raises(ValidationError):
            CardSet(name="", cards=["1", "2"])

    def test_minimum_two_cards(self):
        with pytest.raises(ValidationError):
            CardSet(name="bad", cards=["only-one"])

    def test_predefined_sets_exist(self):
        assert "fibonacci" in PREDEFINED_CARD_SETS
        assert "t-shirt" in PREDEFINED_CARD_SETS
        assert "powers-of-2" in PREDEFINED_CARD_SETS
