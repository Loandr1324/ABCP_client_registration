# Author Loik Andrey 7034@balancedv.ru
import config
from get_params import url_params
import requests
#import json
import logging
import time
from datetime import datetime, timedelta

logging.basicConfig(filename="set_client.log", level=logging.INFO)


def req_get_abcp(urlParams):
    """
    Посылаем GET-запрос согласно переданных параметров из urlParams => (url, params)

    :return: json массив с данными по вновь зарегистрированным клиентам
    """
    try:
        req = requests.get(urlParams[0], params=urlParams[1])

        if req.status_code == 200 and len(req.json()) > 0:
            logging.info(f" {datetime.utcnow()} - Correct answer for users. Working...")
            return req.json()

        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f" {datetime.utcnow()} - Empty answer.\n"
                         f"Not new data, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
            return {}

    except BaseException:
        logging.exception(f"{datetime.utcnow()} - Failed to send GET request:\n{BaseException}")
        return {}

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
                logging.error(
                    f" { datetime.utcnow()} - "
                    f"Quantity client offices: {len(item['offices'])}."
                    f"It is not possible to automatically install a profile."
                    f"Requires manual installation."
                    )
                return

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
            logging.info(
                f" {datetime.utcnow()} - "
                f"Do not change. Client {item['userId']} the correct profile {item['profileId']}."
                )

def req_payments():
    """
    Запрашиваем онлайн оплаты на последние 2 дня

    :return: json массив с данными по поступившим онлай оплатам
    """
    # Запрос по датам платежа
    dateStart = config.DATE_START.strftime('%Y-%m-%d')
    dateEnd = config.DATE_END.strftime('%Y-%m-%d')
    url = config.GET_URL_PAYMENT

    # Подготовка параметров запроса
    params_pay = config.GENERAL_PARAMS.copy()
    params_pay.update({
        'filter[dateStart]': dateStart,
        'filter[dateEnd]': dateEnd,
        'filter[statusIds][]': 2
    })

    try:
        req = requests.get(url, params=params_pay)

        if req.status_code == 200 and len(req.json()) > 0:
            logging.info(f"{datetime.utcnow()} - Correct answer for payments. Working...")
            return req.json()

        elif req.status_code == 200 and len(req.json()) == 0:
            logging.info(f"{datetime.utcnow()} - Empty answer.\n"
                         f"Not new payments, or error.\n"
                         f"If there are problems in the program, then run the request in the browser.")
            return {}
    except BaseException:
        logging.exception(f"{datetime.utcnow()} - Failed to send GET-payments request:\n{BaseException}")
        return {}

def create_dict_new_pay(js):
    """
    Преобразуем список словарей в словарь с ключами по Id оплат с необходимыми данными для дальнейшей работы

    :param js: список словарей по новым оплатам из запроса на платформу ABCP

    :return: dict{
        id: {
            'date':
            'clientId':
            'clientName':
            'orderId':
            'amount':
            'status': 'new'
        }}
    """
    # TODO Планирую вынести из этой функции в отдельные:
    #  1. Подстановку параметров для POST запроса
    #  2. Выделить в отдельную функцию POST запрос и унифицировать.
    #  3. Добавить логирование
    #  4. Определение новых платежей из списка платежей и отправка писем


    # Создаём словарь по оплатам из полученного js
    user_pay = {}
    for item in js:
        user_pay[item['id']] = {
            'date': item['dateTime'],
            'clientId': item['customerId'],
            'clientName': item['customerName'],
            'orderId': item['orderId'],
            'amount': item['amount'],
            'status': 'new'
        }
    return user_pay

    for id in user_pay:
        # Если платёж новый, то отправляем письмо менеджерам офиса
        if id not in CLOBAL_PAYMENTS:
            print(f'{id} - этот платёж новый')
            print(f"По платежу {id} id клиента= {user_pay[id]['clientId']}")
            req_param_user = url_params(user=user_pay[id]['clientId'])
            cl = req_get_abcp(req_param_user)
            print(f"офис клиента {cl[0]['offices'][0]}")
            if len(cl[0]['offices']) == 1:
                cl_office = cl[0]['offices'][0]
            else:
                print('Офисов больше одного не могу отправить письмо')

            user_pay[id]['office'] = cl_office

            # Получение списка email сотрудников по номеру офиса
            email_list = chek_dict_mng(cl_office)

            #Отправка информации на почту сотрудников офиса
            #send_mail(email_list, user_pay[id])

            #Добавление новой оплаты в глобальный список оплат
            CLOBAL_PAYMENTS[id] = user_pay[id]

def chek_dict_mng(office):
    if len(config.LIST_EMAIL_MENAGER) == 0:
        update_dict_mng()
    elif config.LIST_EMAIL_MENAGER['updateDate'] < datetime.utcnow() - timedelta(minutes=1):#timedelta(month=1): TODO Раскомментировать после тестов
        update_dict_mng()
    return config.LIST_EMAIL_MENAGER['email_offices'][office]

def update_dict_mng():
    """Обновляем список email адресов сотрудников по офисам"""
    # Записываем дату обновления
    config.LIST_EMAIL_MENAGER['updateDate'] = datetime.utcnow()

    # Получаем массив сотрудников
    req_param_mng = url_params(managers=True)
    js_managers = req_get_abcp(req_param_mng)

    # Записываем email адреса сотрудников по офисам
    config.LIST_EMAIL_MENAGER['email_offices'] = dict.fromkeys(config.LIST_IdOffice_AV + config.LIST_IdOffice_SV, [])

    for item in config.LIST_EMAIL_MENAGER['email_offices']:
        d = [i['email'] for i in js_managers if i['officeId'] == item]
        config.LIST_EMAIL_MENAGER['email_offices'][item] = d

def send_mail(emails=None, payment=None):
    emails = ['7034@balancedv.ru', 'abcdf_2021@mail.ru']

    import smtplib  # Импортируем библиотеку по работе с SMTP

    # Добавляем необходимые подклассы - MIME-типы
    from email import encoders  # Импортируем энкодер
    from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
    from email.mime.text import MIMEText  # Текст/HTML
    from email.mime.base import MIMEBase  # Общий тип

    addr_from = "7034@balancedv.ru"  # Адресат
    addr_to = emails  # Получатель
    password = "orlov1357loik"  # Пароль

    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = ','.join(addr_to)  # Получатель
    msg['Subject'] = f"Проведение online-оплаты от клиента {payment['clientName']}"  # Тема сообщения

    # Текст сообщения в формате html
    email_content = f"""
<html>
  <head></head>
  <body>
    <p>
        Проведена online - оплата<br>
        Клиент: {payment['clientName']}<br>
        Дата и время: {payment['date']}<br>
        Сумма: {payment['amount']},00 руб.<br>
        &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;&nbsp;
        <br>
        
        <a href="https://cp.abcp.ru/?page=orders&id_order={payment['orderId']}">Перейти к заказазу: {payment['orderId']}</a>
        &emsp;
        <b></b>
    </p>
  </body>
</html>
    """

    msg.attach(MIMEText(email_content, 'html'))  # Добавляем в сообщение html

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)  # Создаем объект SMTP
    # server.starttls()                                  # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()  # Выходим
    return

def pauseWorkTime():
    """
    Определяем количество сеунд паузы в зависимости от рабочего времени

    :return: int -> Количество секунд
    """
    hour_UTC = datetime.utcnow().strftime('%H') # Получаем текущий час по UTC

    # Выбираем количество секунд паузы, согласно рабочему графику сотрудников и логируем
    # Рабочее время сотрудников по часовому поясу UTC с 23 до 9
    if int(hour_UTC) < 23 and int(hour_UTC) >= 9:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_UTC}. Pause 50 min. Working hours from 23 to 9")
        pause_sec = 3000
    else:
        logging.info(f"{datetime.utcnow()} - UTC hour = {hour_UTC}. Pause 5 min. Working hours from 23 to 9")
        pause_sec = 300
    return pause_sec

def main():
    while True:
        # Получаем массив новых склиентов
        req_param_users = url_params() # Получаем параметры запроса
        js_user_id = req_get_abcp(req_param_users)

        # Подставляем профиль если полученный массив не пустой
        if len(js_user_id) > 0:
            set_profile_clients(js_user_id)

        # Устанавливаем паузу согласно рабочего времени
        time.sleep(pauseWorkTime())

def main1():
    # Получаев массив новых оплат
    js_payments = req_payments()

    # Проверыем новые оплаты и отправляем письма
    if len(js_user_id) > 0:
        create_dict_new_pay(js_payments)

def main2():
    send_mail()



if __name__ == '__main__':
    main()
    #main1()
    #main2()
