import json
import telebot

# 361380081

with open("help.txt") as help_file:
    help_text = help_file.read()


try: 
    with open("familiar_users.json") as users_file:
        familiar_users = json.load(users_file)
except:
    familiar_users = {}


try:
    with open("config.json") as config_file:
        config = json.load(config_file)
except:
    print("no config.json")


def save_config(dict_to_save=config, file_to_save="config.json"):
    with open(file_to_save, "w") as file:
        json.dump(dict_to_save, file)


bot = telebot.TeleBot(config["bot"]["token"])


@bot.message_handler(commands=["add_pipe"])
def add_pipe(message):
    text = message.text.split()
    if message.from_user.username not in config["pipes"]:
        config["pipes"][message.from_user.username] = {}
    if text[1] in familiar_users and text[2] in familiar_users:
        config["pipes"][message.from_user.username][text[1]] = text[2]
        bot.send_message(message.chat.id, message.text[1:])
        save_config()
    else:
        bot.send_message(message.chat.id, "Я не знаю, кто эти люди. Пожалуйста сперва форвардните мне по одному сообщению от каждого из них, чтобы я сьел их tg_id")
    
@bot.message_handler(commands=["del_pipe"])
def del_pipe(message):
    text = message.text.split()
    bot.send_message(message.chat.id, message.text[1:])
    del config["pipes"][text[1]]
    save_config()


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=["list"])
def list_avaluable_pipes(message):
    pass
    avaluable_users = []
    for user in config["pipes"]:
        for frm in config["pipes"][user]:
            if config["pipes"][user][frm] == message.from_user.username:
                avaluable_users.append(f"{user}: {frm}")
    bot.send_message(message.chat.id, avaluable_users)


@bot.message_handler(commands=["my_pipes"])
def my_pipes(message):
    resp = ""
    try:
        for pipe in config["pipes"][message.from_user.username]:
            resp += f"from {pipe} to {config['pipes'][message.from_user.username][pipe]}\n"
        bot.send_message(message.chat.id, resp)
    except KeyError:
        bot.send_message(message.chat.id, "Ypu dont have pipes yet!")

@bot.message_handler(func=lambda m: True)
def handle_forvarded(message):
    if message.forward_from is not None:
        try:
            print(f"{message.forward_from.username}: {config['pipes'][message.forward_from.username]}")
            bot.forward_message(familiar_users[config['pipes'][message.from_user.username][message.forward_from.username]], message.chat.id, message.id)
        except KeyError:
            familiar_users[message.forward_from.username] = message.forward_from.id
            bot.send_message(message.chat.id, f"Запомнил {message.forward_from.username}")
            save_config(familiar_users, "familiar_users.json")

bot.polling()