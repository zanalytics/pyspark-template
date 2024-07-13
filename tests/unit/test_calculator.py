from pyspark_template.calculator import addition


def test_addition(first_number: int) -> None:
    """Tests a function with a fixture.

    Parameters
    ----------
    first_number : int
        Pytest fixture

    """
    assert addition(a=first_number, b=7) == 12
