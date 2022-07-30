# Author Loik Andrey 7034@balancedv.ru
import config
import requests
import json
import logging
from datetime import datetime, timedelta


def new_client():
    """
    Запрашиваем список клиентов за последний час

    :return: json массив с данными по вновь зарегистрированным клиентам
    """

    dateRegStart = (datetime.now() + timedelta(hours=-20)).strftime('%Y-%m-%d %H:%M:%S')
    dateRegEnd = (datetime.now() + timedelta(hours=-7)).strftime('%Y-%m-%d %H:%M:%S')

    try:
        req = requests.get(
            f'{config.GET_URL_USERS}userlogin={config.USERNAME}&userpsw={config.MD5PASS}'
            f'&dateRegistredStart={dateRegStart}&dateRegistredEnd={dateRegEnd}'
        )
        if req.status_code == 200 and len(req.json()) > 0:
            print('Пришёл корректный ответ. Обрабатываем...')
            logging.info('Пришёл корректный ответ. Обрабатываем...')
            return req.json()
        elif req.status_code == 200 and len(req.json()) == 0:
            print('Приходит пустой ответ.\nЛибо не было регистраций, либо в ответе приходит ошибка.\n'
                  'Если есть проблемы в работе программы, то выполните запрос в браузере.')
    except BaseException:
        print(f'Не смог отправить GET-запрос{BaseException}')


def set_profile_client(js):
    for item in js:
        param_json = {}
        print(item)
        print(item['offices'])
        if item['profileId'] == '6922524':
            if len(item['offices']) == 1:

                param_json = {
                    'userlogin': config.USERNAME,
                    'userpsw': config.MD5PASS,
                    'userId': item['userId']
                }

                print(f"У клиента один офис: {item['offices'][0]}. Подставляем профиль.")
                if item['offices'][0] in ['35880', '35881', '35883']:
                    param_json['profileId'] = config.profileSV_ID
                elif item['offices'][0] in ['35884', '35885']:
                    param_json['profileId'] = config.profileAV_ID
            else:
                print(
                    f"Количество офисов клиента: {len(item['offices'])}."
                    f"Автоматически установить профиль не возможно."
                    f"Требуется установка вручную."
                )

            print(param_json)
            req_set_user_profile = requests.post(f'{config.POST_URL_USER}', data=param_json)
            print(req_set_user_profile.status_code)
            print(json.loads(req_set_user_profile.text))
            print('\n')


def main():
    js_user_id = new_client()
    print(js_user_id)
    set_profile_client(js_user_id)
    print('Установка профиля произведена')


if __name__ == '__main__':
    main()
