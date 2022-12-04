import emoji

sticker = {
    'thumb_up': emoji.emojize(':thumbs_up:'),
    'thumb_dn': emoji.emojize(':thumbs_down:'),
    'stop': emoji.emojize(':no_entry:')

}

token = 'vk1.a.dGK2h48Ya21UE7yAuyTPK30Cwf8m3P-aM1qeyHzwR2oR7-_jtJNuin6K-nXYaC2Vmz4IIqPr3qsr2TzY6Eb-XBAALYJbWcO59zajsH99-TdhnDp7D3fkVUUAutzWYVKOhH5-CLMRc5a4L0S7cZGAbe1CpqvMsGzBWgGBI69AYex7tOQhdtG75ckmosteTkFmEzRoYHHN2PT9KjBeD2TY3w'

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

Month_names = {
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