import time
import aiohttp
from bs4 import BeautifulSoup
import discord

settings = {
    'token': 'None', #Discord bot token
    'bot': 'None', #Discord bot name
    'id': 0, #Channel ID
}

client = discord.Client()

@client.event
async def on_ready():
    print('Bot logged as {}'.format(client.user))
    channel = client.get_channel(int(settings['id']))
    embed = discord.Embed(
        title='Системное сообщение',
        description='Сообщение о начле работы бота\nСейчас будет отправлено расписание',
        colour=discord.Colour.from_rgb(106, 192, 245)
    )
    await channel.send(embed=embed)
    tables_data = []
    while True:
        tables = getter_tables(await get_html('http://opk.sf-misis.ru/?act=2&id=522'))
        for i in range(len(tables)):
            if len(tables_data) == len(tables):
                if tables_data[i] == tables[i]:
                    continue
                else:
                    print('{} | Send new message'.format(client.user))
                    await send_message(client, tables[i])
                    tables_data[i] = tables[i]
            else:
                print('{} | Send new message'.format(client.user))
                await send_message(client, tables[i])
        time.sleep(10)

async def send_message(client, message):
    channel = client.get_channel(int(settings['id']))
    if len(message['lessons']) == 0:
        embed = discord.Embed(
            title='Расписание на {date}'.format(date=message['date']),
            description='На эту дату пар нет!',
            colour=discord.Colour.from_rgb(106, 192, 245)
        )
    else:
        embed = discord.Embed(
            title='Расписание на {date}'.format(date=message['date']),
            description='Кол-во пар: _{len_less}_\n\n'.format(len_less=len(message['lessons'])),
            colour=discord.Colour.from_rgb(106, 192, 245)
        )
        if len(message['lessons']) == 4:
            embed.colour = discord.Colour.from_rgb(255, 0, 0)
        elif len(message['lessons']) == 3:
            embed.colour = discord.Colour.from_rgb(251, 255, 0)
        elif len(message['lessons']) == 2:
            embed.colour = discord.Colour.from_rgb(0, 255, 13)
        for less in message['lessons']:
            if less['status'] == 'Сняли':
                embed.description += 'Пара была снята'
            else:
                embed.description += '**Номер пары**: _{num}_\n**Название пары**: _{less_name}_\n**Преподаватель**: _{tech_name}_\n**Аудитория**: _{classrom}_\n\n'.format(
                num=less['lesson_num'],
                less_name=less['lesson_name'],
                tech_name=less['techer_name'],
                classrom=less['classroom'],
            )
        embed.description += '*[Закинуть на оплату хостинга(ЮMoney)](https://yoomoney.ru/to/4100116286956555)\n[Проект на Github](https://github.com/lastwek1/opk_parser/)\nРазработчик: [lastwek](https://t.me/lastwek)*'
    await channel.send(embed=embed)

async def get_html(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as r:
                if r.status == 200:
                    return await r.text()
                else:
                    print(f'{url} | {r.status}')
                    return None
        except Exception as e:
            print(f'{url} | {e}')
            return None

def getter_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for item_table in soup.find_all('table', {'class': 'features-table'}):
        item_lesson = {
            'date': None,
            'lessons': None
        }
        table = {'classroom': 0, 'techer_name': None, 'lesson_num': 0, 'lesson_name': None, 'status': None}
        tables = []
        n = 1
        for item in item_table:
            for td in item.find('tr').find_all('td'):
                if n == 1:
                    if td.get_text() == '' or td.get_text() == ' ':
                        table['status'] = 'Сняли'
                    table['lesson_num'] = td.get_text()
                    n += 1
                elif n == 2:
                    if td.get_text() == '' or td.get_text() == ' ':
                        table['status'] = 'Сняли'
                    table['lesson_name'] = td.get_text()
                    n += 1
                elif n == 3:
                    if td.get_text() == '' or td.get_text() == ' ':
                        table['status'] = 'Сняли'
                    table['techer_name'] = td.get_text()
                    n += 1
                elif n == 4:
                    if td.get_text() == '' or td.get_text() == ' ':
                        table['status'] = 'Сняли'
                    table['classroom'] = td.get_text()
                    tables.append(table)
                    table = {'classroom': 0, 'techer_name': None, 'lesson_num': 0, 'lesson_name': None, 'status': None}
                    n = 1
        item_lesson['lessons'] = tables
        items.append(item_lesson)
    for i in range(len(items)):
        try:
            items[i]['date'] = soup.find('center').find_all('center')[i+2].get_text()
        except:
            items[i]['date'] = 'Неизвестно'
    return items

if __name__ == '__main__':
    client.run(settings['token'])