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
        self.e_key = self.extra_keyboard()
        self.ch_key = self.chose_keyboard()
        self.ee_key = self.extra_extra_keyboard()

    def default_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('За месяц', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('За год', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Дополнительно', color=VkKeyboardColor.PRIMARY)
        return keyboard.get_keyboard()

    def extra_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('За год', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('За месяц', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('За день', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Ещё', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(sticker['stop'], color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def chose_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sticker['thumb_up'], color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(sticker['thumb_dn'], color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def extra_extra_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Удалить аккаунт', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(sticker['stop'], color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def __send_message(self, message, keyboard=None):
        self.session.method('messages.send',
                            {'user_id': self.vk_id, 'message': message, 'keyboard': keyboard, 'random_id': 0})

    def __testPL(self, login, password):
        try:
            RuobrRecipient(login, password)
        except RuobrException.AuthorizationException:
            return True

    def __login(self):

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
                self.DB.update_stage(3)
                self.__send_message('Сейчас выполнится проверка ваших данных!')


            elif self.text == sticker['thumb_dn']:
                self.DB.update_stage(0)
                self.__send_message('Начните сначала\nВведите логин : ')

        if self.stage == 3:
            login, password = self.DB.information()[2], self.DB.information()[3]
            if self.__testPL(login, password):
                self.__send_message('Пароль неверный, попробуйте заново!')
                self.__send_message('Введите логин : ')
                self.DB.update_stage(0)
            else:
                self.__send_message('Ваши данные успешно прошли проверку!\nМожете начианать пользоваться!', self.d_key)
                self.DB.update_stage(4)

    def __today_marks(self, stage):
        login, password = str(self.login), str(self.password)
        if self.stage == stage and self.text == 'Сегодня':
            self.__send_message('Ожидайте...', self.d_key)
            self.__send_message(RuobrRecipient(login, password).day_estimnation('day'), None)

    def __year_marks(self, stage):
        login, password = str(self.login), str(self.password)
        if self.stage == stage and self.text == 'За год':
            self.__send_message('Ожидайте...', self.d_key)
            self.__send_message(RuobrRecipient(login, password).year_estimnation('year'), None)

    def __month_marks(self, stage):
        login, password = str(self.login).strip(), str(self.password).strip()
        if self.stage == stage and self.text == 'За месяц':
            self.__send_message('Ожидайте...', self.d_key)
            self.__send_message(RuobrRecipient(login, password).month_estimnation('month'), None)

    def __extra__(self, stage):
        if self.text == 'Дополнительно' and self.stage == stage:
            self.DB.update_stage(5)
            self.__send_message('Да прибудет с вами сила!', self.e_key)

        if self.stage == 10 and self.text == f'{sticker["stop"]}':
            self.DB.update_stage(7)

    def __for_day(self, stage):
        if self.stage == stage and self.text == 'За день':
            self.__send_message('Введите дату в формате - Год.Месяц.День\nНапример : 2022.10.12')
            self.DB.update_stage(6)

        if self.stage == 6:
            login, password = str(self.login).strip(), str(self.password).strip()
            self.__send_message(RuobrRecipient(login, password).day_estimnation(self.text), self.e_key)
            self.DB.update_stage(5)

    def __for_year(self, stage):
        if self.stage == stage and self.text == 'За год':
            self.__send_message('Введите год\nНапример : 2022')
            self.DB.update_stage(7)

        if self.stage == 7:
            login, password = str(self.login).strip(), str(self.password).strip()
            self.__send_message(RuobrRecipient(login, password).year_estimnation(self.text), self.e_key)
            self.DB.update_stage(5)

    def __for_month(self, stage):
        if self.stage == stage and self.text == 'За месяц':
            self.__send_message('Введите год и месяц\nНапример : 2022.11')
            self.DB.update_stage(8)

        if self.stage == 8:
            login, password = str(self.login).strip(), str(self.password).strip()
            self.__send_message(RuobrRecipient(login, password).month_estimnation(self.text), self.e_key)
            self.DB.update_stage(5)

    def __extra_extra(self,stage):
        if self.text == 'Ещё' and self.stage == stage:
            self.DB.update_stage(10)
            self.__send_message('Да прибудет с вами сила!', self.ee_key)
        if self.stage == 10 and self.text == f'{sticker["stop"]}':
            self.DB.update_stage(5)




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
                self.__today_marks(4)
                self.__year_marks(4)
                self.__month_marks(4)
                self.__extra__(4)
                self.__for_day(5)
                self.__for_month(5)
                self.__for_year(5)
                self.__extra_extra(5)


Bot().run()
