import pytest
from pydantic_core import ValidationError

from src.Model.Movie import Movie


def test_movie_constructor_ok():
    the_shining = Movie(id=12, original_title="The Shining")
    assert the_shining.id == 12
    assert the_shining.original_title == "The Shining"


def test_movie_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        Movie(id="Twelve", original_title="Dracula")
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)
