import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import pickle
import pandas as pd

import config

bot = telebot.TeleBot(config.TOKEN)

user_answers = {}
model_path = 'model_diabetes.pkl'
columns = ['HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack',
           'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
           'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income']
questions = [
    "Страдаете ли вы повышенным артериальным давлением?",
    "Повышен ли у вас холестерин?",
    "Проверяли ли вы холестерин за последние 5 лет?",
    "Введите ваш индекс массы тела, округленный до целого? (BMI) = m/h^2, гду m - масса тела в кг, h - рост в м",
    "Курили ли вы более по меньшей мере 100 сигарет за всю жизнь?",
    "Был ли у вас инсульт?",
    "Были ли у вас ишемическая болезнь сердца или инфаркт миокарда?",
    "Была ли физическая активность в течение последних 30 дней?",
    "Употребляете ли вы фрукты 1 или более раз в день?",
    "Употребляете ли вы овощи 1 или более раз в день?",
    "Употребляете ли вы более 14 порций алкоголя в неделю (если вы - мужчина) и более 7 - (если вы - женщина)?",
    "Есть ли у вас медицинская страховка?",
    "Была ли за последние 12 месяцев ситуация, когда нужно было обратиться к врачу,но это было невозможно из-за "
    "стоимости?",
    "Ваша оценка здоровья по шкале: 1 - отличное, 2 - очень хорошее, 3 - хорошее, 4 - удовлетворительное, 5 - плохое",
    "Количество дней плохого психологического состояния за последние 30 дней",
    "Количество дней физической болезни или травмы за последние 30 дней",
    "Испытываете ли вы трудности при ходьбе или подъеме по лестнице?",
    "Ваш пол",
    "Ваш возраст",
    "Степень образования",
    "Доход"
]

current_question_index = 0


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("Новое предсказание")
    markup.add(btn1)
    bot.send_message(message.chat.id, text="Здравствуйте! Ответьте на несколько вопросов для предсказания наличия "
                                           "диабета", reply_markup=markup)
    user_id = message.from_user.id
    user_answers[user_id] = []
    send_question(message, current_question_index, user_id)


@bot.message_handler(content_types=['text'])
def new_prediction(message):
    if message.text == "Новое предсказание":
        user_id = message.from_user.id
        user_answers[user_id] = []
        send_question(message, 0, user_id)


def handle_text_answer(message, question_index):
    user_id = message.from_user.id
    if question_index == 3:
        try:
            imt = int(message.text)
            user_answers[user_id].append(imt)
            send_question(message, question_index + 1, user_id)
        except:
            bot.send_message(message.chat.id, text="Введите целое число")
            bot.register_next_step_handler(message, handle_text_answer, question_index)


def send_question(message, question_index, user_id):
    chat_id = message.chat.id
    if question_index < len(questions):
        question = questions[question_index]
        keyboard = InlineKeyboardMarkup()

        if question_index == 3:
            bot.register_next_step_handler(message, handle_text_answer, question_index)
        elif question_index == 13:
            health = ["1 - отличное", "2 - очень хорошее", "3 - хорошее", "4 - удовлетворительное", "5 - плохое"]
            for i in range(1, 6):
                keyboard.add(InlineKeyboardButton(text=health[i - 1], callback_data=f"{i}_{question_index}"))
        elif question_index in [14, 15]:
            for i in range(0, 31):
                keyboard.add(InlineKeyboardButton(text=str(i), callback_data=f"{i}_{question_index}"))
        elif question_index == 17:
            female_button = InlineKeyboardButton(text="Женский", callback_data=f"0_{question_index}")
            male_button = InlineKeyboardButton(text="Мужской", callback_data=f"1_{question_index}")
            keyboard.add(female_button, male_button)
        elif question_index == 18:
            age = ["18-24", "25-29", "30 -34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74",
                   "75-79", "80 и старше"]
            for i in range(1, 14):
                keyboard.add(InlineKeyboardButton(text=age[i - 1], callback_data=f"{i}_{question_index}"))
        elif question_index == 19:
            education = ["не посещал школу", "начальное образование", "средняя школа",
                         "старшая школа", "1-3 года высшего образования", ">=4 лет высшего образования"]
            for i in range(1, 7):
                keyboard.add(InlineKeyboardButton(text=education[i - 1], callback_data=f"{i}_{question_index}"))
        elif question_index == 20:
            income = ["<$10,000", "<$16,250", "<$22,500", "<$28,750", "<$35,000", "<$55,000", "<$75,000", ">=$75,000"]
            for i in range(1, 9):
                keyboard.add(InlineKeyboardButton(text=income[i - 1], callback_data=f"{i}_{question_index}"))
        else:
            yes_button = InlineKeyboardButton(text="Да", callback_data=f"1_{question_index}")
            no_button = InlineKeyboardButton(text="Нет", callback_data=f"0_{question_index}")
            keyboard.add(yes_button, no_button)

        bot.send_message(chat_id, text=question, reply_markup=keyboard)
    else:
        if not (os.path.exists(model_path)):
            bot.send_message(chat_id, text="Простите, предсказание невозможно из-за технических проблем")
        df = pd.DataFrame([user_answers[user_id]], columns=columns)
        with open(model_path, "rb") as f:
            m = pickle.load(f)
        y_pred = "нет диабета" if m.predict(df)[0] == 0 else "есть диабет"
        bot.send_message(chat_id, text=f"Ваше предсказание: {y_pred}")
        user_answers[user_id] = []


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data.split("_")
    answer = int(data[0])
    question_index = int(data[1])
    user_answers[user_id].append(answer)
    send_question(call.message, question_index + 1, user_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
