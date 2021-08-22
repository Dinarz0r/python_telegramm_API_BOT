class Users:

    def __init__(self, user) -> None:
        self.username = user.from_user.username
        self.id_user = user.from_user.id
        self._search_method = None
        self._search_city = None
        self._id_city = None
        self._cache_data = None
        self._count_show_hotels = None
        self._photo = None
        self._count_show_photo = None
        self._price_min_max = dict()
        self._distance_min_max = dict()

    @property
    def search_method(self):
        return self._search_method

    @search_method.setter
    def search_method(self, method: str) -> None:
        self._search_method = method

    @property
    def search_city(self):
        return self._search_city

    @search_city.setter
    def search_city(self, city: str) -> None:
        self._search_city = city

    @property
    def id_city(self):
        return self._id_city

    @id_city.setter
    def id_city(self, id_city: int) -> None:
        self._id_city = id_city

    @property
    def count_show_hotels(self):
        return self._count_show_hotels

    @count_show_hotels.setter
    def count_show_hotels(self, number: str) -> None:
        self._count_show_hotels = int(number)

    @property
    def cache_data(self):
        return self._cache_data

    @cache_data.setter
    def cache_data(self, data) -> None:
        self._cache_data = data

    @property
    def photo(self):
        return self._photo

    @photo.setter
    def photo(self, flag: bool) -> None:
        self._photo = flag

    @property
    def count_show_photo(self):
        return self._count_show_photo

    @count_show_photo.setter
    def count_show_photo(self, number: str) -> None:
        self._count_show_photo = int(number)

    @property
    def price_min_max(self):
        return self._price_min_max

    @price_min_max.setter
    def price_min_max(self, price_min_max: dict) -> None:
        self._price_min_max = price_min_max

    @property
    def distance_min_max(self):
        return self._distance_min_max

    @distance_min_max.setter
    def distance_min_max(self, distance_min_max: dict) -> None:
        self._distance_min_max = distance_min_max
