import asyncio
import os

import emoji

import parser
from database import DataBase
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from parser import Ruobr, RuobrException

from data import token, sticker

import requests
import threading


def chose_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(sticker['thumb_up'], color=VkKeyboardColor.POSITIVE)
    keyboard.add_button(sticker['thumb_dn'], color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def default_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('За месяц', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('За год', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Выгрузить Excel', color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


def get_fullname(session, vkid):
    user = session.method("users.get", {"user_ids": {vkid}})
    fullname = user[0]['first_name'] + '_' + user[0]['last_name']
    return fullname


class Bot:

    def __init__(self):
        self.threads = None
        self.DB, self.text, self.vk_id = None, None, None
        self.stage, self.login, self.password = None, None, None

        """VK API"""
        self.session = vk_api.VkApi(login='89609130789', password='182801DanieruDaivkontakte', token=token)
        self.longpoll = VkLongPoll(self.session)

        """Клавиатуры"""
        self.d_key = default_keyboard()
        self.ch_key = chose_keyboard()

    def __upload_document(self, filename: str = 'file'):
        file = open(f'{filename}', 'rb')
        a = self.session.method("docs.getMessagesUploadServer", {"type": "doc", "peer_id": self.vk_id})
        b = requests.post(a['upload_url'], files={"file": file}).json()
        c = self.session.method('docs.save', {'file': b['file']})
        attachment = f'doc{c["doc"]["owner_id"]}_{c["doc"]["id"]}'
        return attachment

    def __send_message(self, vk_id=None, message=None, keyboard=None, attachment=None):
        if vk_id is None:
            vk_id = self.vk_id

        self.session.method('messages.send',
                            {'user_id': vk_id,
                             'message': message,
                             'attachment': attachment,
                             'keyboard': keyboard,
                             'random_id': 0})

    def __login(self, vkid=None):
        vid = vkid

        def __test_password_login(login, password):
            try:
                Ruobr(login, password)
            except RuobrException.AuthorizationException:
                return True

        if self.stage == -1:
            self.__send_message(vid, 'Вы не зарегистрированы!\n'
                                     'Для регистрации необходимо ввести данные от Cabinet Ruobr')
            self.DB.update_stage(0)
            self.__send_message(vid, 'Введите логин : ')

        if self.stage == 0:
            self.DB.writer('login', self.text)
            self.DB.update_stage(1)
            self.__send_message(vid, 'Введите пароль : ')

        if self.stage == 1:
            if self.DB.information()[3] != self.text:
                self.DB.writer('password', self.text)
                self.DB.update_stage(2)
                login, password = self.DB.information()[2], self.DB.information()[3]
                self.__send_message(vid, f'Проверьте введенные данные!\nЛогин : {login}\nПароль : {password}',
                                    self.ch_key)

        if self.stage == 2:

            if self.text == sticker['thumb_up']:
                self.__send_message(vid, 'Сейчас выполнится проверка ваших данных!')
                self.DB.update_stage(3)
                self.__send_message(vid, 'Напишите что-нибудь для продолжения', self.d_key)

            elif self.text == sticker['thumb_dn']:
                self.DB.update_stage(0)
                self.__send_message(vid, 'Начните сначала\nВведите логин : ')

        if self.stage == 3:

            login, password = self.DB.information()[2], self.DB.information()[3]
            if __test_password_login(login, password):
                self.__send_message(vid, 'Пароль неверный, попробуйте заново!')
                self.__send_message(vid, 'Введите логин : ')
                self.DB.update_stage(0)
            else:
                self.__send_message(vid, 'Ваши данные успешно прошли проверку!\nМожете начианать пользоваться!',
                                    self.d_key)
                self.DB.update_stage(4)
                self.__send_message(vid, 'Введите дату в формате : \n'
                                         '2022 - Для года\n'
                                         '2022.10 - Для месяца\n'
                                         '2022.10.01 - Для дня')

    def __base(self, vkid=None):

        fullname = get_fullname(self.session, vkid)
        login, password = str(self.login), str(self.password)
        try:
            if self.stage == 4:
                """Общие даты"""
                if self.text == 'Сегодня':
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).day_estimnation('day'))

                elif self.text == 'За год':
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).year_estimnation('year'))

                elif self.text == 'За месяц':
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).month_estimnation('month'))

                    """Конкретные даты"""

                elif len(self.text) == 4 and self.text[0].isdigit():
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).year_estimnation(self.text))

                elif len(self.text) == 7 and self.text[0].isdigit():
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).month_estimnation(self.text))

                elif len(self.text) == 10 and self.text[0].isdigit():
                    self.__send_message(vkid, 'Ожидайте...', self.d_key)
                    self.__send_message(vkid, Ruobr(login, password).day_estimnation(self.text))

                elif self.text == 'Выгрузить Excel':
                    self.__send_message(vkid, 'Ожидайте...')
                    Ruobr(self.login, self.password).ToExcel(f'{fullname}-оценки')
                    attachment = self.__upload_document(filename=f'{fullname}-оценки.xlsx')
                    self.__send_message(vkid, attachment=attachment)

        except parser.RuobrException.Ruobr503Exception:
            self.__send_message(vkid, 'Проблемы на сайте! Попробуйте позже')

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.vk_id = event.user_id
                self.text = event.text

                """Инициализация таблицы и пользователя"""
                self.DB = DataBase(self.vk_id)
                self.DB.create_table()
                self.DB.new_user()

                """Получение этапа"""
                information = self.DB.information()
                self.stage, self.login, self.password, self.threads = information[1], information[2], information[3], \
                                                                      information[4]
                self.__login(self.vk_id)

                for thread in threading.enumerate():
                    print(thread)
                threading.Thread(target=self.__base, args=[self.vk_id]).start()


Bot().run()
