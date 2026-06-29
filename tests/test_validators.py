import pytest

from utils.errors import ValidationError
from utils.validators import validate_city_name


def test_validate_city_name_valid() -> None:
    assert validate_city_name("  Ciudad de México  ") == "Ciudad de México"


def test_validate_city_name_empty() -> None:
    with pytest.raises(ValidationError):
        validate_city_name("   ")


def test_validate_city_name_only_numbers() -> None:
    with pytest.raises(ValidationError):
        validate_city_name("12345")


def test_validate_city_name_too_long() -> None:
    with pytest.raises(ValidationError):
        validate_city_name("a" * 81)
