import emoji

sticker = {
    'thumb_up': emoji.emojize(':thumbs_up:'),
    'thumb_dn': emoji.emojize(':thumbs_down:'),
    'stop': emoji.emojize(':no_entry:')

}

token = 'vk1.a.GyvtBGANbHcZfAe0-kVoAPEguyxR34ZwvycgVZHDZxg4g5yMyCtjwq_T-fAoxRwZ15CiaUEw0X02u4ueLOMT04YIqIKKnK0A-KtQmfSqjvEhgsJR-R7l9fjA2IKW6lzVQo4vT1lY2pHfNxOz45ma5LbDR0ybtleiPDiYMvYIfAeBv2i_a72X0feEFDS6cx9L'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'https://cabinet.ruobr.ru/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

marks = {
    'отлично': 5,
    'хорошо': 4,
    'удовлетворительно': 3,
    'неудовлетворительно': 2,
}

emoji_months = {
    1: f'январь {emoji.emojize(":snowflake:")}',
    2: f'феварль {emoji.emojize(":cold_face:")}',
    3: f'март {emoji.emojize(":ribbon:")}',
    4: f'апрель {emoji.emojize(":clown_face:")}',
    5: f'май {emoji.emojize(":man_dancing:")}',
    6: f'июнь {emoji.emojize(":fire:")}',
    7: f'июль {emoji.emojize(":person_surfing:")}',
    8: f'август {emoji.emojize(":tear-off_calendar:")}',
    9: f'сентябрь {emoji.emojize(":umbrella:")}',
    10: f'окятбрь {emoji.emojize(":jack-o-lantern:")}',
    11: f'ноябрь {emoji.emojize(":fog:")}',
    12: f'декабрь {emoji.emojize(":Christmas_tree:")}',

}
Month_names = {
    1: f'Январь ',
    2: f'Феварль ',
    3: f'Март ',
    4: f'Апрель',
    5: f'Май ',
    6: f'Июнь ',
    7: f'Июль ',
    8: f'Август ',
    9: f'Сентябрь',
    10: f'Окятбрь',
    11: f'Ноябрь',
    12: f'Декабрь'
}