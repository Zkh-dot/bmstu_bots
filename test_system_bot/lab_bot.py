import telebot 
import config
import os
import json

bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=['document'])
def add_test(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(os.path.join("tests", message.chat.username), 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Сохранил ваш тест!")

@bot.message_handler(commands=["list"])
def list_all(message):
    bot.send_message(message.chat.id, "/" + "\n/".join(os.listdir("./tests")))

@bot.message_handler(commands=["help"])
def list_all(message):
    bot.send_message(message.chat.id, "Пример документа:")
    with open(os.path.join("tests", "Lunitarik"), "rb") as file:
        bot.send_document(message.chat.id, document=file)


@bot.message_handler(content_types=["text"])
def start_test(message):
    try: 
        with open(os.path.join(".\\tests", message.text[1:]), encoding="utf-8") as test_file:
            test = json.load(test_file)
    except:
        bot.send_message(message.chat.id, "С этим тестом что-то не так")
    else:
        bot.send_message(message.chat.id, "Начинаем тест!")
    answers = test["results"].copy()
    for a in answers:
        answers[a] = 0
    print("and =", answers)
    test_step(message, 0, test, answers)
    
    # print(list(test["questions"][0].keys())[0])
    

def test_step(message, i, test, answers):
    if message.text in test["questions"][max(i-1, 0)][list(test["questions"][max(i-1, 0)].keys())[0]]: #list(test["questions"][i].keys())[0]
        for option in test["questions"][max(i-1, 0)][list(test["questions"][max(i-1, 0)].keys())[0]][message.text]:
            try:
                answers[option] += 1
                print(answers)
            except KeyError:
                bot.send_message(message.chat.id, "Автор теста ебланчик :С")
    if i >= len(test["questions"]):
        # validate(message, test, answers)
        try:
            validate(message, test, answers)
        except Exception as e:
            bot.send_message(message.chat.id, f"Эта экспертная система устарела! Обратитесь к автору-эксперту для ее обновления.\n{e}")
        # bot.send_message(message.chat.id, f"Тест завершен! Ваш результат: \n{test['results'][max(answers, key=answers.get)]}", reply_markup=telebot.types.ReplyKeyboardRemove())
    
    else:
        buttons = []
        for option in test["questions"][i][list(test["questions"][i].keys())[0]]: #list(test["questions"][i].keys())[0]
            buttons.append(telebot.types.KeyboardButton(option  ))
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*buttons)
        print(test["questions"][i][list(test["questions"][i].keys())[0]])
        bot.send_message(message.chat.id, list(test["questions"][i].keys())[0], reply_markup=markup)
        bot.register_next_step_handler(message, lambda m: test_step(m, i + 1, test, answers))


def validate(message, test, answers):
    print(answers)
    print(test["test_results"])
    for result in test["test_results"]:
        for option in test["test_results"][result]:
            if type(test["test_results"][result][option]) == int:
                test["test_results"][result][option] = [test["test_results"][result][option]] * 2
            if answers[option] < test["test_results"][result][option][0] or answers[option] > test["test_results"][result][option][1]:
                break
        else:
            bot.send_message(message.chat.id, f"Тест завершен! Ваш результат: \n{result}", reply_markup=telebot.types.ReplyKeyboardRemove())
            return
    bot.send_message(message.chat.id, "Странная ошибка в системе. Обраитесь к эксперту.", reply_markup=telebot.types.ReplyKeyboardRemove())

                
            



if __name__ == "__main__":
    os.makedirs("tests", exist_ok=True)
    bot.infinity_polling()
    # with open(os.path.join(".\\tests", "Lunitarik.json")) as test_file:
    #     test = json.load(test_file)
    # print(list(test["questions"][0].keys())[0])