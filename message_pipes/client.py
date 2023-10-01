import json
from telethon import TelegramClient, sync, events 
from random import randint
from time import sleep


try:
    with open("config.json") as config_file:
        config = json.load(config_file)
except:
    print("no config.json")

def save_config():
    with open("config.json", "w"):
        json.dump(config)


client = TelegramClient(str(randint(10000, 99999)), config["user"]["api_id"], config["user"]["api_hash"])


@client.on(events.NewMessage(chats=config["pipes"]))
async def send_to_bot(event):
    await client.forward_messages(config["bot"]["id"])


@client.on(events.NewMessage(chats=[config["bot"]["id"]]))
async def send_from_bot(event):
    text = event.message.message.split()
    print(text)
    try:
        if text[0] == "add_pipe":
            config["pipes"][text[1]] = text[2]
            save_config() 
        elif text[0] == "del_pipe":
            del config["pipes"][text[1]]
            save_config()
        else:
            try:
                await client.send_message(text[0], *text[1:])
                await client.send_message(config["bot"]["id"], "true")
            except:
                await client.send_message(config["bot"]["id"], "false")
    except Exception as e:
        print(e)

def start():
    print('starting...')
    client.start()
    client.run_until_disconnected()
    print('here')

while True:
    try:
        start()
        break
    except KeyboardInterrupt:
        client.log_out()

    except Exception as e:
        print('Телеграм решил, что я пидорас. Я сплю минут на 10-12')
        # sleep(600 + randint(0, 120))
