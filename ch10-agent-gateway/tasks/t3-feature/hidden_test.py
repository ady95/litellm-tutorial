import pytest
from inventory import Inventory


def make():
    inv = Inventory()
    inv.add("apple", 5, 2.0)
    inv.add("pear", 2, 3.5)
    return inv


def test_remove_partial():
    inv = make()
    inv.remove("apple", 2)
    assert inv.quantity("apple") == 3


def test_remove_all_deletes():
    inv = make()
    inv.remove("pear", 2)
    assert "pear" not in inv.items


def test_remove_errors():
    inv = make()
    with pytest.raises(ValueError):
        inv.remove("apple", 6)
    with pytest.raises(ValueError):
        inv.remove("kiwi", 1)


def test_total_value():
    assert make().total_value() == pytest.approx(17.0)


def test_existing_add_still_works():
    inv = make()
    inv.add("apple", 1, 2.0)
    assert inv.quantity("apple") == 6
