from inventory import Inventory


def test_add():
    inv = Inventory()
    inv.add("apple", 3, 1.5)
    inv.add("apple", 2, 2.0)
    assert inv.quantity("apple") == 5
