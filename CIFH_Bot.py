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
        if len(info) == 1 or d.get('type') == 'MDPZ':
            return 'Летать можно. Но не выше 150 метров от поверхности, без установления местного режима'

        elif d.get('type') == 'CTRZ' and d.get('alts').get('range')[0] == 0:  # Проверка на диспетчерскую зону
            return 'Летать от земли до ' + str(info[0].get('alts').get('range')[-1]) + ' можно только с разрешения: ' + str(d.get('name')) + ', при установлении местного режима'

        elif d.get('type') == 'CTRZ' and d.get('alts').get('range')[0] != 0:  # Проверка на диспетчерский район
            if int(info[0].get('alts').get('range')[0]) >= 150:
                return 'Летать можно. Но не выше 150 метров от поверхности, без установления местного режима \nОт ' + str(info[0].get('alts').get('range')[0]) \
                       + ' до ' + str(info[0].get('alts').get('range')[-1]) + ' только с разрешения ' + str(d.get('name'))
            else:
                return 'Летать можно не выше ' + str(info[0].get('alts').get('range')[0]) + ' без установления местного режима \nОт ' + str(info[0].get('alts').get('range')[0]) \
                       + ' до ' + str(info[0].get('alts').get('range')[-1]) + ' только с разрешения ' + str(d.get('name'))


b1 = KeyboardButton('Отправить геопозицию', request_location=True)
b2 = KeyboardButton('/help')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b1).add(b2)


async def on_startup(_):
    print('Я вышел в онлайн, бот')


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    await message.answer('Приветствую, данный бот поможет тебе определиться с местом для полета на квадрокоптере. Отправь мне геолокацию или координаты (долгота, широта):')
    await message.answer('Вот еще несколько команд, которые могут тебе помочь: \n/notification - Дисклеймер (Прочитай обязательно!) \n/register - регистрация дрона \n/rules - правила полета, которые нужно знать', reply_markup=kb_client)


@dp.message_handler(commands=['notification'])
async def command_notification(message: types.Message):
    await message.answer('Помни, что данный бот разработан на базе сайта fpln.ru и не предназначен для замены сертифицированных навигационных устройств! База данных воздушного пространства предоставляется исключительно в информационных целях. \nТак же следует знать, что согласно Постановлению от 03.02.2020 № 74 беспилотник может летать не выше 150 метров от поверхности, без установления временного или местного режима, для просмотра максимальных границ зон полета введи /full_info')


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
    message_coords = message.text.replace(',', ' ').split()
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
