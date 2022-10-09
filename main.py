import grequests
import requests
import re
import datetime
from bs4 import BeautifulSoup


class Ruobr:

    def __init__(self, username, password):
        self.__cookies = self.__cookies(username, password)

    def __cookies(self, username, password):

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://cabinet.ruobr.ru',
            'Referer': 'https://cabinet.ruobr.ru/login/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }
        cookies = dict(requests.get('https://cabinet.ruobr.ru/login/', headers=headers).cookies)
        data = {'username': f'{username}', 'password': f'{password}', 'next': '/',
                'csrfmiddlewaretoken': cookies['csrftoken']}
        sessionid = dict(
            requests.post('https://cabinet.ruobr.ru/login/', cookies=cookies, headers=headers, data=data).cookies)
        cookies['sessionid'] = sessionid['sessionid']

        return cookies

    def average_marks(self, MonthYear: str, OnlyResult: bool = True) -> str:

        response = requests.get('https://cabinet.ruobr.ru/student/progress/', params={'page': '1'},
                                cookies=self.__cookies, )
        soup = BeautifulSoup(response.text, 'lxml')
        quantity_pages = int(
            [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile("page")})][-1].split('page=')[
                1]) + 1
        pages = [f'https://cabinet.ruobr.ru//student/progress/?page={num}' for num in range(1, quantity_pages)]
        response = (grequests.get(url, cookies=self.__cookies) for url in pages)
        resp = grequests.map(response)

        '''Составление списка предметов'''
        all_marks = []
        for request in resp:
            soup = BeautifulSoup(request.text, 'lxml')
            data = list(map(str, soup.find_all('tr')))
            for t in data:
                cleantext = BeautifulSoup(t, 'lxml').text.split('\n')[3:6]
                if cleantext != ['Дата', 'Дисциплина', 'Отметка']:
                    all_marks.append(cleantext)

        '''Изменение оценок на числа'''
        marks = {
            'отлично': 5,
            'хорошо': 4,
            'удовлетворительно': 3,
            'неудовлетворительно': 2,
        }
        for i, ell in enumerate(all_marks):
            all_marks[i][2] = marks[f'{all_marks[i][2]}']

        '''Получение оценок среднего бала за месяц'''
        stud_year = [ell for ell in all_marks if ell[0][3:] == f'{MonthYear}']
        lesons = set([ell[1] for ell in stud_year])
        mark = []

        if OnlyResult:
            for l in lesons:
                for_lesson = f'{l} - {"%.2f" % (sum(lst := [ell[2] for ell in stud_year if ell[1] == l]) / len(lst))}'
                mark.append(for_lesson)

        if not OnlyResult:
            for l in lesons:
                for_lesson = [l, [ell[2] for ell in stud_year if ell[1] == l]]
                mark.append(for_lesson)

        month = {'01': 'Январь',
                 '02': 'Февраль',
                 '03': 'Март',
                 '04': 'Апрель',
                 '05': 'Май',
                 '06': 'Июнь',
                 '07': 'Июль',
                 '08': 'Август',
                 '09': 'Сентябрь',
                 '10': 'Октябрь',
                 '11': 'Ноябрь',
                 '12': 'Декабрь',

                 }

        return f'Оценки за {month[MonthYear[:2]]} {MonthYear[3:]}г. :\n\n·' + '\n·'.join(mark)

    def schedule(self, YearMonthDay: str):

        if YearMonthDay is None:
            YearMonthDay = str(datetime.datetime.today() + datetime.timedelta(days=1))[:10]
        else:
            YearMonthDay = YearMonthDay.replace('.', '-')

        response = requests.get('https://cabinet.ruobr.ru/student/get_schedule/g0/',
                                params={'start': YearMonthDay,
                                        'end': YearMonthDay},
                                cookies=self.__cookies)
        text = response.json()
        schedule = [ell['title'].split('\n')[0] for ell in text]
        time = [(i['start'].split('T')[1][:5] + " - " + i['end'].split('T')[1][:5]) for i in text]
        group = [ell['title'].split('\n')[1] for ell in text]

        for i, e in enumerate(group):
            match e[24]:
                case 'В':
                    group[i] = ''
                case '1':
                    group[i] = '[1-ая подгруппа]'
                case '2':
                    group[i] = '[2-ая подгруппа]'

        go = [f'|{t}| {s} {g}' for s, t, g in zip(schedule, time, group)]
        go = list(set(go))
        go.sort()

        return '\n'.join(go)


print(Ruobr('DaniEruDai', '182801DanieruDaicabinet').schedule('2022.10.13'))
