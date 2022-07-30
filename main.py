# Author Loik Andrey 7034@balancedv.ru
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import config
import requests
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(filename="set_client.log", level=logging.INFO)


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
            logging.info(f"{datetime.now()} - Correct answer. Working...")
            return req.json()
        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f"{datetime.now()} - Empty answer.\n"
                         f"Not new registration, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
    except BaseException:
        logging.exception(f"{datetime.now()} - Failed to send GET request:\n{BaseException}")


def set_profile_client(js):
    for item in js:
        param_json = {}
        if item['profileId'] == '6922524':
            if len(item['offices']) == 1:

                param_json = {
                    'userlogin': config.USERNAME,
                    'userpsw': config.MD5PASS,
                    'userId': item['userId']
                }

                logging.info(f"{datetime.now()} - The client has one office: {item['offices'][0]}. Set profile.")

                if item['offices'][0] in ['35880', '35881', '35883']:
                    param_json['profileId'] = config.profileSV_ID
                elif item['offices'][0] in ['35884', '35885']:
                    param_json['profileId'] = config.profileAV_ID
            else:
                logging.error(f"{datetime.now()} - "
                              f"Quantity client offices: {len(item['offices'])}."
                              f"It is not possible to automatically install a profile."
                              f"Requires manual installation."
                              )

            req_set_user_profile = requests.post(f'{config.POST_URL_USER}', data=param_json)
            if req_set_user_profile.status_code == 200:
                logging.info(f"{datetime.now()} - "
                             f"Client {param_json['userId']} successfully installed profile {param_json['profileId']}"
                             )
            else:
                logging.error(f"{datetime.now()} - "
                              f"Client {param_json['userId']} failed to install profile {param_json['profileId']}"
                              )
        else:
            logging.info(f"{datetime.now()} - "
                         f"Do not change. Client {item['userId']} the correct profile {item['profileId']}."
                         )


def main():
    js_user_id = new_client()
    set_profile_client(js_user_id)


if __name__ == '__main__':
    main()
