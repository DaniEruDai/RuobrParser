import asyncio

from datetime import datetime
from dateutil.relativedelta import relativedelta

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from data import headers, marks,months_name


class RuobrException(Exception):
    class NoDateException(Exception):
        pass

    class DateException(Exception):
        pass

    class AuthorizationException(Exception):
        pass


class RuobrRecipient:

    def __init__(self, username, password):
        self.__username, self.__password = username, password
        self.__cookie = self.__cookies()

        if len(self.__cookie) != 2:
            raise RuobrException.AuthorizationException('Логин или пароль неверные')

    def __cookies(self):
        session = requests.Session()
        session.get('https://cabinet.ruobr.ru/login/', headers=headers)
        data = {'username': f'{self.__username}', 'password': f'{self.__password}',
                'csrfmiddlewaretoken': dict(session.cookies)['csrftoken']}
        session.post('https://cabinet.ruobr.ru/login/', headers=headers, data=data)
        return dict(session.cookies)

    def __get_esimation(self):

        async def __taskmaster():
            pagination = await __pagination()
            tasks = []
            urls = (f'https://cabinet.ruobr.ru//student/progress/?page={num}' for num in range(1, pagination))

            async with ClientSession() as session:
                for url in urls:
                    tasks.append(asyncio.create_task(__fetch(url, session)))
                    await asyncio.sleep(0.02)

                return await asyncio.gather(*tasks)

        async def __fetch(url, session):
            async with session.get(url, cookies=self.__cookie) as response:
                return await response.text()

        async def __pagination():
            async with ClientSession() as session:
                async with session.get('https://cabinet.ruobr.ru//student/progress/?page=1',
                                       cookies=self.__cookie) as response:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                    pagination = int([link.get('href') for link in soup.find_all('a')][-2].split('=')[1]) + 1
                    return pagination

        async def __handler():
            all_marks = []
            for request in await __taskmaster():
                soup = BeautifulSoup(request, 'lxml')
                data = list(map(str, soup.find_all('tr')))
                for t in data:
                    cleantext = BeautifulSoup(t, 'lxml').text.split('\n')[3:6]
                    if cleantext != ['Дата', 'Дисциплина', 'Отметка']:
                        all_marks.append(cleantext)

            '''Изменение оценок на числа'''
            for i, ell in enumerate(all_marks):
                all_marks[i][2] = marks[f'{all_marks[i][2]}']

            '''Изменение дат на реверсивные им'''
            for i, ell in enumerate(all_marks):
                newdata = all_marks[i][0].split('.')
                newdata = '.'.join(newdata[::-1])
                all_marks[i][0] = newdata

            return all_marks

        return asyncio.run(__handler())

    def marks(self, date=None):

        def __student_year(date):
            start = datetime.strptime(f'{date}0901', "%Y%m%d").date()
            dates = [(start + relativedelta(months=date)).strftime('%Y.%m') for date in range(1, 9)]
            dates.insert(0, start.strftime('%Y.%m'))
            return dates

        all_marks = self.__get_esimation()

        match date:
            case 'year':
                date = datetime.today().strftime('%Y')
            case 'month':
                date = datetime.today().strftime('%Y.%m')
            case 'day':
                date = datetime.today().strftime('%Y.%m.%d')
            case None:
                return 'Дата неуказана'

        match len(date):
            case 4:
                sorted_marks = [ell for ell in all_marks if ell[0][:7] in __student_year(date)]
                sorted_marks.sort()
            case 7:
                sorted_marks = [ell for ell in all_marks if ell[0][:7] in date]
                sorted_marks.sort()
            case 10:
                sorted_marks = [ell for ell in all_marks if ell[0] in date]
                sorted_marks.sort()
            case _:
                return 'Дата указана неверно'

        return sorted_marks

    def year_estimnation(self, date):
        if date == 'year': date = datetime.today().strftime('%Y')
        all_marks = self.marks(date)
        if len(date) == 4:
            lessons = {lesson[1] for lesson in all_marks}
            year_marks = [f' - {l} - {"%.2f" % (sum(lst := [ell[2] for ell in all_marks if ell[1] == l]) / len(lst))}' for l in
                          lessons]
            year_marks.sort()
            if year_marks:
                result = f'Средний балл за {date} год\n\n' + '\n'.join(year_marks)
            else:
                result = f'Оценок за {date} нет!'
            return result


    def month_estimnation(self, date):
        if date == 'month': date = datetime.today().strftime('%Y.%m')
        all_marks = self.marks(date)
        if len(date) == 7:
            lessons = {lesson[1] for lesson in all_marks}
            year_marks = [f' - {l} - {"%.2f" % (sum(lst := [ell[2] for ell in all_marks if ell[1] == l]) / len(lst))}' for l in
                          lessons]
            year_marks.sort()
            if year_marks:
                result = f'Средний балл за {months_name[int(date[5:])]} {date[:4]} года\n\n' + '\n'.join(year_marks)
            else:
                result = f'Оценок за {date} нет!'
            return result

    def day_estimnation(self, date):
        if date == 'day': date = datetime.today().strftime('%Y.%m.%d')
        all_marks = self.marks(date)
        if len(date) == 10:
            lessons = {lesson[1] for lesson in all_marks}
            year_marks = [f'{l} - {[ell[2] for ell in all_marks if ell[1] == l]}' for l in lessons]
            year_marks.sort()
            if year_marks:
                result = f'Оценки за {date}\n\n' + '\n'.join(year_marks)
            else:
                result = f'Оценок за {date} нет!'
            return result
