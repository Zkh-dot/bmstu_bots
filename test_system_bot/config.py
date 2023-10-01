token=""

# get users file mesages
saved_text = "Сохранил ваш тест!"
example_text = "Пример документа:"

# pass test messages
start_test = "Начинаем тест!"
test_readfile_error = "С этим тестом что-то не так"
test_expired_error = f"Эта экспертная система устарела! Обратитесь к автору-эксперту для ее обновления."
test_wrongresult_error = "Автор теста ебланчик :С"
test_result = "Тест завершен! Ваш результат: \n"
notexistingresult_error = "Странная ошибка в системе. Обраитесь к эксперту."

# create test in constructor messages
end_test_command = "/test_is_done"
end_question_command = "/question_is_done"
end_options_command = "/option_is_done"
abort_creation_command = "/break"
start_test_creation = f"Сейчас вы начнете создание своей экспертной системы. Чтобы прервать создание экспертной системы и отчистить все результаты, введите команду {abort_creation_command}"

ask_for_question = f"Пожалуйста, напишите вопрос. Если вы ввели все вопросы, введите команду {end_test_command}"
ask_for_option = f"Пожалуйста, напишите вариант ответа. Если вы ввели все варианты, введите команду {end_question_command}"
ask_for_option_param = f"Пожалуйста, напишите, какие параметры увеличатся при выборе этого варианта. В случае, если вы ввели все параметры, введите команду {end_options_command}"

end_test_creation = "Ваша экспертная система успешно сохранена! Введите команду /list чтобы посмотреть на нее."
not_valid_test_creation_error = "Вы ввели что-то не так. К сожалению, на данный момент система не поддерживает редактирование, поэтому вам придется создать систему заново."
no_username_error = "К сожалению, люди без юзернейма ограничены в правах и не могут создавать тесты. Вы можете поплакать об этом."
creation_end = "Создание теста завершено."