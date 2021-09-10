from datetime import datetime
import re


class Users:
    """
    Класс пользователя, с параметрами необходимые для формирования запроса.
        Args: user: объект вх. сообщения от пользователя
    """

    def __init__(self, user) -> None:
        self.username: str = user.from_user.username
        self.id_user: int = user.from_user.id
        self._search_method = None
        self._search_city = None
        self._id_city = None
        self._cache_data = None
        self._count_show_hotels = None
        self._photo = None
        self._count_show_photo = None
        self._price_min_max: dict = dict()
        self._distance_min_max: dict = dict()
        self._history: dict = dict()
        self._language = 'ru_RU'

    def clear_cache(self) -> None:
        """
        Функция для отчистки кэша параметров поиска отеля.
        """
        self._search_method = None
        self._search_city = None
        self._id_city = None
        self._cache_data = None
        self._count_show_hotels = None
        self._photo = None
        self._count_show_photo = None
        self._price_min_max = dict()
        self._distance_min_max = dict()
        self._language = 'ru_RU'

    @property
    def language(self) -> str:
        """
        Геттер метода языка
        :return: _language
        :rtype: str
        """
        return self._language

    @language.setter
    def language(self, language: str) -> None:
        """
        Сеттер метода языка
        :param language: язык
        """
        self._language: str = language

    @property
    def search_method(self) -> str:
        """
        Геттер метода поиска отелей
        :return: _search_method
        :rtype: str
        """
        return self._search_method

    @search_method.setter
    def search_method(self, method: str) -> None:
        """
        Сеттер метода поиска отелей
        :param method: город
        """
        self._search_method = method

    @property
    def search_city(self):
        """
        Геттер искомого города
        :return: __search_city
        :rtype: str
        """
        return self._search_city

    @search_city.setter
    def search_city(self, city: str) -> None:
        """
        Сеттер искомого города
        :param city: город
        """
        self._search_city = city

    @property
    def id_city(self):
        """
        Геттер id города
        :return: _id_city
        :rtype: int
        """
        return self._id_city

    @id_city.setter
    def id_city(self, id_city: int) -> None:
        """
        Сеттер id города
        :param id_city: номер города
        """
        self._id_city = id_city

    @property
    def count_show_hotels(self):
        """
        Геттер количества искомых отелей в городе
        :return: _count_show_hotels
        :rtype: int
        """
        return self._count_show_hotels

    @count_show_hotels.setter
    def count_show_hotels(self, number: str) -> None:
        """
        Сеттер количества искомых отелей в городе
        :param number: кол-во искомых отелей
        """
        self._count_show_hotels = int(number)

    @property
    def cache_data(self):
        """
        Геттер кэша с информацией
        :return: _cache_data
        :rtype: [dict, list]
        """
        return self._cache_data

    @cache_data.setter
    def cache_data(self, data: [dict, list]) -> None:
        """
        Сеттер кэша с информацией
        :param data:
        """
        self._cache_data: [dict, list] = data

    @property
    def photo(self):
        """
        Геттер bool значения поиска фотографий отелей.
        :return: _photo
        :rtype: bool
        """
        return self._photo

    @photo.setter
    def photo(self, flag: bool) -> None:
        """
        Сеттер bool значения поиска фотографий отелей
        """
        self._photo: bool = flag

    @property
    def count_show_photo(self):
        """
        Геттер кол-вы выводимых фотографий
        :return: _count_show_photo
        :rtype: int
        """
        return self._count_show_photo

    @count_show_photo.setter
    def count_show_photo(self, number: str) -> None:
        """
        Сеттер кол-ва выводимых фотографий
        """
        self._count_show_photo: int = int(number)

    @property
    def price_min_max(self):
        """
        Геттер минимальной и максимальной цены искомого отеля
        :return: _price_min_max
        :rtype: dict
        """
        return self._price_min_max

    @price_min_max.setter
    def price_min_max(self, price_min_max: dict) -> None:
        """
        Сеттер минимальной и максимальной цены искомого отеля
        """
        self._price_min_max = price_min_max

    @property
    def distance_min_max(self):
        """
        Геттер диапазона поиска отелей между минимальным и максимальным расстоянием
        :return: _distance_min_max
        :rtype: dict
        """
        return self._distance_min_max

    @distance_min_max.setter
    def distance_min_max(self, distance_min_max: dict) -> None:
        """
        Сеттер диапазона поиска отелей между минимальным и максимальным расстоянием
        """
        self._distance_min_max = distance_min_max

    @property
    def history(self):
        """
        Геттер вывода истории искомых отелей по параметрам "время - метод поиска - отели"
        :return: str_history
        :rtype: str
        """
        str_history = ''
        for i, k in self._history.items():
            str_history += f'*{i}*\nКоманда: {k["command"]}\nОтели: {", ".join([hotel for hotel in k["hotels"]])}.\n\n'
        return str_history

    def save_history(self) -> None:
        """
        Функция сохраняющая данные в _history искомых отелей
        по параметрам "время - метод поиска - отели"
        """
        best_deal_view = 0
        hotels = list()
        command = ''
        for i in self.cache_data['data']['body']['searchResults']['results']:
            if self.distance_min_max \
                    and self.search_method == 'best_deal':
                min_dist = self.distance_min_max.get('min')
                max_dist = self.distance_min_max.get('max')
                test_dist = i["landmarks"][0]["distance"]
                print(test_dist)
                dist_center = int(re.findall(r'\d+', i["landmarks"][0]["distance"])[0])
                print(dist_center)
                if not min_dist <= dist_center <= max_dist:
                    continue
                else:
                    best_deal_view += 1
                    if best_deal_view > self.count_show_hotels:
                        break
            hotels.append(f'\n- *{i["name"]}*')

        if self._search_method == 'PRICE':
            command = '/lowprice'
        elif self._search_method == 'PRICE_HIGHEST_FIRST':
            command = '/highprice'
        elif self._search_method == 'best_deal':
            command = '/bestdeal'

        self._history[datetime.now().strftime("%d-%m-%Y %H:%M:%S")] = {'command': command, 'hotels': hotels}
