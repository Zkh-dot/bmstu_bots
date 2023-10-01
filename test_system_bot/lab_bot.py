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
    bot.send_message(message.chat.id, config.saved_text)


@bot.message_handler(commands=["list"])
def list_all(message):
    bot.send_message(message.chat.id, "/" + "\n/".join(os.listdir("./tests")))


@bot.message_handler(commands=["help"])
def list_all(message):
    bot.send_message(message.chat.id, config.example_text)
    with open(os.path.join("tests", "example"), "rb") as file:
        bot.send_document(message.chat.id, document=file)


@bot.message_handler(commands=["create"])
def start_test_creation(message):
    bot.send_message(message.chat.id, config.start_test_creation)
    bot.send_message(message.chat.id, config.ask_for_question)
    test = {
        "questions": [],
        "test_results": {}
    }
    bot.register_next_step_handler(message, lambda m: get_test_question(m, test))


def start_result(message, test):
    bot.send_message(message.chat.id, config.ask_for_result)
    bot.register_next_step_handler(message, lambda m: get_results(m, test))


def get_test_question(message, test):
    if message.text == config.abort_creation_command:
        bot.send_message(message.chat.id, config.creation_end)
        del test
    elif message.text == config.end_test_command:
        start_result(message, test)     
    else:
        test["questions"].append({message.text: {}})    
        bot.send_message(message.chat.id, config.ask_for_option)
        bot.register_next_step_handler(message, lambda m: get_test_option(m, test))


def get_test_option(message, test):
    if message.text == config.abort_creation_command:
        bot.send_message(message.chat.id, config.creation_end)
    elif message.text == config.end_test_command:
        start_result(message, test)     
    elif message.text == config.end_question_command:
        bot.send_message(message.chat.id, config.ask_for_question)
        bot.register_next_step_handler(message, lambda m: get_test_question(m, test))
    else:
        test["questions"][-1][list(test["questions"][-1].keys())[0]][message.text] = []
        bot.send_message(message.chat.id, config.ask_for_option_param)
        bot.register_next_step_handler(message, lambda m: get_option_params(m, test, message.text))


def get_option_params(message, test, question):
    if message.text == config.abort_creation_command:
        bot.send_message(message.chat.id, config.creation_end)
    elif message.text == config.end_test_command:
        start_result(message, test)     
    elif message.text == config.end_question_command:
        bot.send_message(message.chat.id, config.ask_for_question)
        bot.register_next_step_handler(message, lambda m: get_test_question(m, test))
    elif message.text == config.end_options_command:
        bot.send_message(message.chat.id, config.ask_for_option)
        bot.register_next_step_handler(message, lambda m: get_test_option(m, test))
    else:
        test["questions"][-1][list(test["questions"][-1].keys())[0]][question].append(message.text)
        bot.send_message(message.chat.id, config.ask_for_option_param)
        bot.register_next_step_handler(message, lambda m: get_option_params(m, test, question))



def get_results(message, test):
    if message.text == config.abort_creation_command:
        bot.send_message(message.chat.id, config.creation_end)
    elif message.text == config.end_test_command:
        publish_test(message, test)    
    else:
        bot.send_message(message.chat.id, config.ask_for_result_param)
        test["test_results"][message.text] = {}
        bot.register_next_step_handler(message, lambda m: get_result_param(m, test, message.text))

def get_result_param(message, test, result):
    if message.text == config.abort_creation_command:
        bot.send_message(message.chat.id, config.creation_end)
    elif message.text == config.end_test_command:
        publish_test(message, test)    
    elif message.text == config.end_result_command:
        bot.send_message(message.chat.id, config.ask_for_result)
        bot.register_next_step_handler(message, lambda m: get_results(m, test))
    else:
        try:
            test["test_results"][result][message.text.split()[0]] = [int(message.text.split()[1]), int(message.text.split()[2])]
        except:
            bot.send_message(message.chat.id, config.not_valid_test_creation_error)
            del test
            return
        bot.send_message(message.chat.id, config.ask_for_result_param)
        bot.register_next_step_handler(message, lambda m: get_result_param(m, test, message.text))


def publish_test(message, test):
    # TODO: check
    if evaluate(test):
        with open(os.path.join("tests", message.chat.username), 'w') as new_file:
            json.dump(test, new_file)
        bot.send_message(message.chat.id, config.end_test_creation)
    else:
        bot.send_message(message.chat.id, config.not_valid_test_creation_error)
    del test

def get_all_options(test):
    all = []
    for i in range(len(test["questions"])):
        for question in test["questions"][-1][list(test["questions"][-1].keys())[0]]:
            for option in test["questions"][-1][list(test["questions"][-1].keys())[0]][question]:
                all.append(*test["questions"][-1][list(test["questions"][-1].keys())[0]][question][option])
    return all
def get_result_options(test):
    all = {}
    for result in test["test_results"]:
        for option in test["test_results"][result]:
                all[option] = 0
    return all


def evaluate(test):
    return True


    all_options = get_all_options(test)
    result_options = get_result_options(test)
    if len(all_options) == 0 or set(all_options) != set(result_options):
            return False
    return True


@bot.message_handler(content_types=["text"])
def start_test(message):
    try: 
        with open(os.path.join("./tests", message.text[1:]), encoding="utf-8") as test_file:
            test = json.load(test_file)
    except Exception as e:
        bot.send_message(message.chat.id, config.test_readfile_error, reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, config.start_test)
    answers = get_result_options(test)

    test_step(message, 0, test, answers)
    

def test_step(message, i, test, answers):
    if message.text in test["questions"][max(i-1, 0)][list(test["questions"][max(i-1, 0)].keys())[0]]: #list(test["questions"][i].keys())[0]
        for option in test["questions"][max(i-1, 0)][list(test["questions"][max(i-1, 0)].keys())[0]][message.text]:
            try:
                answers[option] += 1
            except KeyError:
                bot.send_message(message.chat.id, config.test_wrongresult_error, reply_markup=telebot.types.ReplyKeyboardRemove())
    if i >= len(test["questions"]):
        try:
            test_results(message, test, answers)
        except Exception as e:
            bot.send_message(message.chat.id, config.test_expired_error, reply_markup=telebot.types.ReplyKeyboardRemove())
    
    else:
        buttons = []
        for option in test["questions"][i][list(test["questions"][i].keys())[0]]: #list(test["questions"][i].keys())[0]
            buttons.append(telebot.types.KeyboardButton(option  ))
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*buttons)
        bot.send_message(message.chat.id, list(test["questions"][i].keys())[0], reply_markup=markup)
        bot.register_next_step_handler(message, lambda m: test_step(m, i + 1, test, answers))


def test_results(message, test, answers):
    for result in test["test_results"]:
        for option in test["test_results"][result]:
            if type(test["test_results"][result][option]) == int:
                test["test_results"][result][option] = [test["test_results"][result][option]] * 2
            if answers[option] < test["test_results"][result][option][0] or answers[option] > test["test_results"][result][option][1]:
                break
        else:
            bot.send_message(message.chat.id, config.test_result + result, reply_markup=telebot.types.ReplyKeyboardRemove())
            return
    bot.send_message(message.chat.id, config.notexistingresult_error, reply_markup=telebot.types.ReplyKeyboardRemove())


if __name__ == "__main__":
    os.makedirs("tests", exist_ok=True)
    bot.infinity_polling()