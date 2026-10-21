class Inventory:
    def __init__(self):
        self.items = {}  # name -> {"qty": int, "price": float}

    def add(self, name, qty, price):
        if qty <= 0:
            raise ValueError("qty must be positive")
        item = self.items.setdefault(name, {"qty": 0, "price": price})
        item["qty"] += qty
        item["price"] = price

    def quantity(self, name):
        return self.items.get(name, {"qty": 0})["qty"]
