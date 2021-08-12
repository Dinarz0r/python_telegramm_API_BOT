class Users:

    def __init__(self, id_user: str, id_city=None) -> None:
        self.id_user = id_user
        self.check_choice_city = False
        self.bool_city = False
        self.data = dict()
        self.id_city = id_city

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, id_user):
        self._id_user = id_user

    @property
    def id_city(self):
        return self._id_city

    @id_city.setter
    def id_city(self, id_city):
        self._id_city = id_city

    @property
    def check_choice_city(self):
        return self._check_choice_city

    @check_choice_city.setter
    def check_choice_city(self, boolean: bool) -> None:
        self._check_choice_city = boolean

    @property
    def bool_city(self):
        return self._bool_city

    @bool_city.setter
    def bool_city(self, boolean: bool) -> None:
        self._bool_city = boolean

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, json_data: dict) -> None:
        self._data = json_data