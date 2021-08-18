class Users:

    def __init__(self, id_user: str, id_city=None) -> None:
        self.id_user = id_user
        # self.check_choice_city = False
        # self.bool_city = False
        self.data = dict()
        self.hotels_data = dict()
        self.id_city = id_city
        self.config = {'count_hotels': 0, 'search_price_filter': None, 'bool_city': False,
                       'check_choice_city': False, 'id_last_messages': None, 'messages': None,
                       'check_photo_hotel': False, 'photo_hotel_count': 0, 'flag_search_photo': False,
                       'start_search': False}

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
    def hotels_data(self):
        return self._hotels_data

    @hotels_data.setter
    def hotels_data(self, json_data: dict) -> None:
        self._hotels_data = json_data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, json_data: dict) -> None:
        self._data = json_data

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config
