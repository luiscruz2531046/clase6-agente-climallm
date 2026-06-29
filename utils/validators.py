from utils.errors import ValidationError


MAX_CITY_LENGTH = 80
ALLOWED_SEPARATORS = {" ", "-", "."}


def validate_city_name(city: str) -> str:
    """Limpia y valida el nombre de una ciudad."""
    if not isinstance(city, str):
        raise ValidationError("La ciudad debe ingresarse como texto.")

    cleaned_city = " ".join(city.strip().split())

    if not cleaned_city:
        raise ValidationError("La ciudad no puede estar vacia.")

    if len(cleaned_city) > MAX_CITY_LENGTH:
        raise ValidationError(
            f"La ciudad no puede tener más de {MAX_CITY_LENGTH} caracteres."
        )

    if cleaned_city.isdigit():
        raise ValidationError("La ciudad no puede ser solo números.")

    if any(character.isdigit() for character in cleaned_city):
        raise ValidationError("La ciudad no puede contener números.")

    if not all(
        character.isalpha() or character in ALLOWED_SEPARATORS
        for character in cleaned_city
    ):
        raise ValidationError(
            "La ciudad solo puede contener letras, espacios, puntos y guiones."
        )

    return cleaned_city
