class Product:
    def __init__(
        self,
        name: str,
        category: str,
        waiting_time: int = 0,
        discount: bool = False,
    ) -> None:
        assert (
            isinstance(name, str) and len(name) > 0
        ), "Product name must be non-empty string"
        assert (
            isinstance(category, str) and len(category) > 0
        ), "Category must be non-empty string"
        assert waiting_time >= 0, "Waiting time cannot be negative"
        assert isinstance(discount, bool), "Discount must be boolean"
        self._name = name
        self._category = category
        self._waiting_time = waiting_time
        self._discount = discount

    def __repr__(self) -> str:
        return (
            f"Product(name={self.name}, category={self.category}, "
            f"waiting_time={self.waiting_time})"
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def waiting_time(self) -> int:
        return self._waiting_time

    @property
    def discount(self) -> bool:
        return self._discount
