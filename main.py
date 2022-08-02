# Author Loik Andrey 7034@balancedv.ru
import config
import requests
import json
import logging
import time
from datetime import datetime, timedelta

logging.basicConfig(filename="set_client.log", level=logging.INFO)


def new_clients():
    """
    Запрашиваем список клиентов за последний час

    :return: json массив с данными по вновь зарегистрированным клиентам
    """

    dateRegStart = (datetime.utcnow() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    dateRegEnd = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"\nTime on server = {datetime.utcnow()}\nDate start = {dateRegStart}\nDate end = {dateRegEnd}")


    param_users = config.GENERAL_PARAMS.copy()
    param_users.update({
        'dateRegistredStart': dateRegStart,
        'dateRegistredEnd':dateRegEnd
    })

    try:
        req = requests.get(config.GET_URL_USERS, params=param_users)

        if req.status_code == 200 and len(req.json()) > 0:
            logging.info(f"{datetime.utcnow()} - Correct answer. Working...")
            return req.json()

        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f"{datetime.utcnow()} - Empty answer.\n"
                         f"Not new registration, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
            return {}

    except BaseException:
        logging.exception(f"{datetime.utcnow()} - Failed to send GET request:\n{BaseException}")

def set_profile_clients(js):
    """
    Подставляем базовый профиль согласно офиса нового клиента

    :param js: json массив словарей с данными клиентов
    :return: None
    """
    for item in js:
        # Отрабатываем подстановку офиса только для клиентов с базовым профилем без платёжных систем
        if item['profileId'] == config.BASE_PROFILE:
            # Отрабатываем подстановку профиля если у клиента только один офис
            if len(item['offices']) == 1:
                param_user_update = config.GENERAL_PARAMS.copy()
                param_user_update['userId'] = item['userId']

                logging.info(f"{datetime.utcnow()} - The client has one office: {item['offices'][0]}. Set profile.")

                # Подставляем базовый профиль согласно офиса клиента в параметры запроса
                if item['offices'][0] in config.LIST_IdOffice_SV:
                    param_user_update['profileId'] = config.profileSV_ID

                elif item['offices'][0] in config.LIST_IdOffice_AV:
                    param_user_update['profileId'] = config.profileAV_ID

            else:
                # Логируем ошибку, в случае количества офисов больше одного
                logging.error(f"{datetime.utcnow()} - "
                              f"Quantity client offices: {len(item['offices'])}."
                              f"It is not possible to automatically install a profile."
                              f"Requires manual installation."
                              )

            # Выполняем POST запрос на подстановку офиса
            req_set_user_profile = requests.post(f'{config.POST_URL_USER}', data=param_user_update)

            # Логируем результаты выполнения POST запроса подстановки офиса
            if req_set_user_profile.status_code == 200:
                logging.info(f"{datetime.utcnow()} - "
                             f"Client {param_user_update['userId']} successfully installed profile {param_user_update['profileId']}"
                             )
            else:
                logging.error(f"{datetime.utcnow()} - "
                              f"Client {param_user_update['userId']} failed to install profile {param_user_update['profileId']}"
                              )

        else:
            # Логируем, если у пользователя не нужно менять офис
            logging.info(f"{datetime.utcnow()} - "
                         f"Do not change. Client {item['userId']} the correct profile {item['profileId']}."
                         )

def pauseWorkTime():
    """
    Определяем количество сеунд паузы в зависимости от рабочего времени

    :return: int -> Количество секунд
    """
    hour_UTC = datetime.utcnow().strftime('%H') # Получаем текущий час по UTC

    # Выбираем количество секунд паузы, согласно рабочему графику сотрудников и логируем
    # Рабочее время сотрудников по часовому поясу UTC с 23 до 9
    if int(hour_UTC) <= 23 and int(hour_UTC) >= 9:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_UTC}. Pause 50 min. Working hours from 23 to 9")
        pause_sec = 3000
    else:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_UTC}. Pause 5 min. Working hours from 23 to 9")
        pause_sec = 300
    return pause_sec

def main():
    while True:
        js_user_id = new_clients() # Получаем массив новых склиентов

        # Подставляем профиль если полученный массив не пустой
        if len(js_user_id) > 0:
            set_profile_clients(js_user_id)

        # Устанавливаем паузу согласно рабочего времени
        time.sleep(pauseWorkTime())


if __name__ == '__main__':
    main()
