import requests
from tokens import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, executor, types

url = "https://fpln.ru/api/info/contains"
fpln_info = 0

dp = Dispatcher(Bot(token=tg_token))

coords = {
    "lat": '',
    "lng": '',
    "key": fpln_token
}


def main_function(info):
    for t in info:
        if not t.get('active') or t.get('alts').get('str') == 'GND - UNL':  # Убираем неактивные зоны и нелимитированную зону
            info.remove(t)

        if t.get('type') == 'LZ' or t.get('type') == 'EZ' or t.get('type') == 'DZ':  # Зоны огран полетов, запретные зоны, опасные зоны
            return 'В данном месте летать запрещено'

    for d in info:
        if len(info) == 1:
            return 'Летай спокойно, но не выше ' + str(info[0].get('alts').get('range')[-1]) + ' метров'  # Максимальная высота свободной зоны полета

        elif d.get('type') == 'CTRZ' and d.get('alts').get('range')[0] == 0:  # Проверка на диспетчерскую зону
            return 'Летать можно только с разрешения: ' + str(d.get('name'))

        elif d.get('type') == 'CTRZ' and d.get('alts').get('range')[0] != 0:  # Проверка на диспетчерский район
            return 'Летать без разрешения можно не выше ' + str(d.get('alts').get('range')[0]) + ' метров от поверхности. ' + 'Выше ' + str(d.get('alts').get('range')[0]) + ' метров от поверхности, летать можно только с разрешения: ' + str(d.get('name'))

        elif d.get('type') == 'MDPZ':
            return 'Летай спокойно, но не выше ' + str(info[0].get('alts').get('range')[-1]) + ' метров'


async def on_startup(_):
    print('Я вышел в онлайн, бот')


b1 = KeyboardButton('Отправить геопозицию', request_location=True)
b2 = KeyboardButton('/help')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b2).add(b1)


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    await message.answer('Привет, я помогу тебе определить местность для полёта! Отправь мне геолокацию или координаты (долгота, широта):', reply_markup=kb_client)


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    global coords, fpln_info
    coords["lat"] = str(message.location.latitude)
    coords["lng"] = str(message.location.longitude)
    fpln_info = (requests.get(url, params=coords)).json()
    await message.answer(str(main_function(fpln_info)))


@dp.message_handler()
async def coords_command(message: types.Message):
    global coords, fpln_info
    message_coords = message.text.split()
    coords["lat"] = str(message_coords[0])
    coords["lng"] = str(message_coords[1])
    try:
        fpln_info = (requests.get(url, params=coords)).json()
        await message.answer(str(main_function(fpln_info)))
    except:
        await message.answer('Я не могу прочитать ваше сообщение, отправьте мне координаты или геолокацию')


@dp.message_handler(commands=['show_me'])
async def show_command(message: types.Message):
    await message.answer(coords.get("lat"), coords.get("lng"))


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
