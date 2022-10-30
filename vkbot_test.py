import emoji

from database import DataBase
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from parser import RuobrRecipient, RuobrException

from data import token, sticker


class Bot:
    def __init__(self):
        self.DB, self.text, self.vk_id = None, None, None
        self.stage, self.login, self.password = None, None, None

        """VK API"""
        self.session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.session)

        """Клавиатуры"""
        self.d_key = self.default_keyboard()
        self.ch_key = self.chose_keyboard()

    def default_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('За месяц', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('За год', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def chose_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sticker['thumb_up'], color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(sticker['thumb_dn'], color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def __send_message(self, message, keyboard=None):
        self.session.method('messages.send',
                            {'user_id': self.vk_id, 'message': message, 'keyboard': keyboard, 'random_id': 0})

    def __login(self):
        def __test_password_login(login, password):
            try:
                RuobrRecipient(login, password)
            except RuobrException.AuthorizationException:
                return True

        if self.stage == -1:
            self.__send_message('Вы не зарегистрированы!')
            self.DB.update_stage(0)
            self.__send_message('Введите логин : ')

        if self.stage == 0:
            self.DB.writer('login', self.text)
            self.DB.update_stage(1)
            self.__send_message('Введите пароль : ')

        if self.stage == 1:
            if self.DB.information()[3] != self.text:
                self.DB.writer('password', self.text)
                self.DB.update_stage(2)
                login, password = self.DB.information()[2], self.DB.information()[3]
                self.__send_message(f'Проверьте введенные данные!\nЛогин : {login}\nПароль : {password}', self.ch_key)

        if self.stage == 2:
            if self.text == sticker['thumb_up']:
                self.__send_message('Сейчас выполнится проверка ваших данных!')
                self.DB.update_stage(3)
                self.__send_message('Напишите что-нибудь для продолжения')


            elif self.text == sticker['thumb_dn']:
                self.DB.update_stage(0)
                self.__send_message('Начните сначала\nВведите логин : ')

        if self.stage == 3:

            login, password = self.DB.information()[2], self.DB.information()[3]
            if __test_password_login(login, password):
                self.__send_message('Пароль неверный, попробуйте заново!')
                self.__send_message('Введите логин : ')
                self.DB.update_stage(0)
            else:
                self.__send_message('Ваши данные успешно прошли проверку!\nМожете начианать пользоваться!', self.d_key)
                self.DB.update_stage(4)
                self.__send_message('Введите дату в формате : \n'
                                    '2022 - Для года\n'
                                    '2022.10 - Для месяца\n'
                                    '2022.10.01 - Для дня')

    def __base(self, stage):
        login, password = str(self.login), str(self.password)
        if self.stage == stage:
            """Общие даты"""

            if self.text == 'Сегодня':
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).day_estimnation('day'))

            elif self.text == 'За год':
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).year_estimnation('year'))

            elif self.text == 'За месяц':
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).month_estimnation('month'))

                """Конкретные даты"""
            elif len(self.text) == 4 and self.text[0].isdigit():
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).year_estimnation(self.text))

            elif len(self.text) == 7 and self.text[0].isdigit():
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).month_estimnation(self.text))

            elif len(self.text) == 10 and self.text[0].isdigit():
                self.__send_message('Ожидайте...', self.d_key)
                self.__send_message(RuobrRecipient(login, password).day_estimnation(self.text))

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
                self.stage, self.login, self.password = information[1], information[2], information[3]

                self.__login()
                self.__base(4)


Bot().run()
