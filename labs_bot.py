import re
import requests
from bs4 import BeautifulSoup
import hashlib
import setting
import json
import asyncio
import datetime
import os

def find_all_files(soup: BeautifulSoup) -> dict:
    raw_tags = soup.find_all("a")
    tags = {}
    for tag in raw_tags:
        r_res = re.match(r'.*?href=\"(.*?)\".*?title=\"(.*?)\"', str(tag))
        if r_res != None:
            tags[r_res[1]] = r_res[2]

    return tags


def check_new_files(old, new):
    result = ""
    for file in new:
        if file not in old:
            result += f"{file}: {new[file]}\n"
    return result


async def ping():
    while(True):
        await check_new()
        await asyncio.sleep(10)

try:
    with open("dump.json") as dump_file:
        subsctiptions = json.load(dump_file)
except FileNotFoundError:
    subsctiptions = {}

bot = telebot(setting.token)

    # json.dump(json_to_save, file_name)

@bot.message_handler(func=lambda call: True)
async def add_subjetct(message):
    if len(message.text.split()) != 1:
        await bot.send_message(message.chat.id, setting.page_error)
        return 404
    try:
        if message.text not in subsctiptions:
            subsctiptions[message.text] = {
                "subs": [],
                "hash": "",
                 "files": {},
                 "counter": 0
            }
        subsctiptions[message.text]["subs"].append(message.chat.id)
        json.dump(subsctiptions, "dump.json")
        await bot.send_message(message.chat.id, setting.success_add_message)
    except:
        await bot.send_message(message.chat.id, setting.ask_for_help_message)


async def check_new():
    to_delete = []
    for site in subsctiptions: 
        if subsctiptions[site]['counter'] == 2:
            to_delete.append(site)
            continue
        try:
            res = requests.post(site, data={'page': '3'})
        except Exception as e: 
            subsctiptions[site]['counter'] += 1
            print(f"{site} вышел с ошибкой {e}\nСчетчик:{subsctiptions[site]['counter']}")
            continue
        soup = BeautifulSoup(res.text)
        if hashlib.md5(soup.prettify().encode('utf-8')).hexdigest() == subsctiptions[site]["hash"]: 
            print(f"{site} не изменился!")
        elif subsctiptions[site]["hash"] == "":
            print(f"{site} проверен первый раз!")
            subsctiptions[site]["hash"] = hashlib.md5(soup.prettify().encode('utf-8')).hexdigest()
            subsctiptions[site]["files"] = find_all_files(soup)
        else: 
            subsctiptions[site]["hash"] = hashlib.md5(soup.prettify().encode('utf-8')).hexdigest()
            new_files = check_new_files(subsctiptions[site]["files"], find_all_files(soup))
            if new_files != "":
                subsctiptions[site]["files"] == find_all_files(soup)
                for sub in subsctiptions[site]["subs"]:
                    try:
                        bot.send_message(sub, f"Новые файлы на сайте {site}:\n{new_files}")
                    except:
                        print(f"Ошибка с пользователем {sub}")
    # json.dump(subsctiptions, "dump.json")
    with open("dump.json", "w") as dump_file:
        json.dump(subsctiptions, dump_file)
    print("endjson")

    for site in to_delete:
        del subsctiptions[site]



loop = asyncio.get_event_loop()
task = loop.create_task(ping())
bot_task = loop.create_task(bot.polling())

loop.run_until_complete(task)
loop.run_until_complete(bot_task)

asyncio.run(bot.polling())

print("hi")

