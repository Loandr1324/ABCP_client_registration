import config
import logging
from datetime import datetime, timedelta


def url_params(user=None, managers=False, payments=False):
    """
    Получаем тип запроса и возвращаем url и params GET-запроса в зависимости от типа запроса.
    Если тип запроса не передан, то возвращаем параметры для получения списка покупателей за последний час.

    :param user: строка str userID. Передаётся в случае, когда необходимо получить информацию по одному клиенту, по его цифровому коду;
    :param managers: True. Передаётся если необходимо получить список сотрудников
    :param payments: True. Передаётся если необходимо получить список новых оплат
    :return: url, params для GET-запроса
    """
    params = config.GENERAL_PARAMS.copy()

    if user is not None:
        # Задаём переменные запроса покупателя по Id покупателя
        url = config.GET_URL_USERS
        params.update({
            'customersIds[]': user
        })
        logging.info(f" Set params for user {user}")


    elif managers:
        # Задаём переменные запроса по менеджерам
        url = config.GET_URL_MANAGERS

        logging.info(f" Set params for managers")


    elif payments:
        # Задаём переменные запроса по менеджерам
        url = config.GET_URL_PAYMENT

        dateStart = config.DATE_START.strftime('%Y-%m-%d')
        dateEnd = config.DATE_END.strftime('%Y-%m-%d')

        params = config.GENERAL_PARAMS.copy()
        params.update({
            'filter[dateStart]': dateStart,
            'filter[dateEnd]': dateEnd,
            'filter[statusIds][]': 2
        })

        logging.info(f" Set params for payments\nTime on server = {datetime.utcnow()}\nDate start = {dateStart}\nDate end = {dateEnd}")


    else:
        # Задаём переменные запроса по покупателям по периоду регистрации
        url = config.GET_URL_USERS

        dateRegStart = config.DATE_START.strftime('%Y-%m-%d %H:%M:%S')
        dateRegEnd = config.DATE_END.strftime('%Y-%m-%d %H:%M:%S')
        params.update({
            'dateRegistredStart': dateRegStart,
            'dateRegistredEnd': dateRegEnd
        })

        logging.info(f" Set params for users\nTime on server = {datetime.utcnow()}\nDate start = {dateRegStart}\nDate end = {dateRegEnd}")

    return url, params