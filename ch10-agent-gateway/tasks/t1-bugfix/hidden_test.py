import pytest
from stats import mean, median


def test_mean_float():
    assert mean([1, 2]) == 1.5


def test_median_even():
    assert median([4, 1, 3, 2]) == 2.5


def test_median_unsorted_odd():
    assert median([9, 1, 5]) == 5


@pytest.mark.parametrize("fn", [mean, median])
def test_empty_raises(fn):
    with pytest.raises(ValueError):
        fn([])
