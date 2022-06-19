import telebot
from telebot import TeleBot
import sqlite3
import config
from string import Template

bot: TeleBot = telebot.TeleBot(config.token)

@bot.message_handler(commands=["ping"]) #Создаем команду
def start(message):
	try: #Заворачиваем все в try
		bot.send_message(message.chat.id, "<b>PONG!</b>" , parse_mode="HTML")
		bot.forward_message(config.owner, message.chat.id, message.message_id)
	except:
		bot.send_message(config.owner, 'Что-то пошло не так!') #Данная система (оборачивание в try и except позволит продолжить выполнение кода, даже если будут ошибки)


user_dict = {}


class User:
    def __init__(self, city):
        self.city = city

        keys = ['fullname', 'phone', 'adress',
                'appeal']

        for key in keys:
            self.key = None

@bot.message_handler(commands=['reg'])
def user_reg(message):
        msg = bot.send_message(message.chat.id, 'В каком городе\населённом пункте вы проживаете?')
        bot.register_next_step_handler(msg, process_city_step)

def process_city_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        msg = bot.send_message(chat_id, 'Введите ваше ФИО полностью, без аббревиатур, пожалуйста.')
        bot.register_next_step_handler(msg, process_fullname_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!')

def process_fullname_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.fullname = message.text

        msg = bot.send_message(chat_id, 'Введите ваш адрес:')
        bot.register_next_step_handler(msg, process_adress_step)

    except Exception as e:
        bot.reply_to(message, 'oops!')

def process_adress_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.adress = message.text

        msg = bot.send_message(chat_id, 'Введите ваш номер телефона в формате 89*********')
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!')


def process_phone_step(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text

        msg = bot.send_message(chat_id, 'Введите своё обращение. По какой причине вы хотите вызвать специалиста?')
        bot.register_next_step_handler(msg, process_appeal_step)

    except Exception as e:
        bot.reply_to(message, 'oops!')

def process_appeal_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.appeal = message.text

        #
        bot.send_message(chat_id, getRegData(user, "Ваша заявка, ", message.from_user.first_name), parse_mode="Markdown")
        bot.send_message(chat_id, "Подождите немного, скоро специалист позвонит вам по номеру телефона, указанному в анкете и уже определит время для прибытия на дом или решит проблему сразу, консультируя вас по телефону")
        #
        bot.send_message(config.group, getRegData(user, "Заявка от бота", bot.get_me().username), parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, 'oops!')

#
#
#
def getRegData(user, title, name):
    t = Template('$title *$name* \n Город: *$city* \n Адрес: *$adress* \n ФИО: *$fullname* \n Телефон: *$phone* \n Обращение: *$appeal*')

    return t.substitute({
        'title': title,
        'name': name,
        'city': user.city,
        'adress': user.adress,
        'fullname': user.fullname,
        'phone': user.phone,
        'appeal': user.appeal,
    })



keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Покупка услуг', 'Обратная связь')
keyboard.row('Заявка')

connection = sqlite3.connect('Data.db', check_same_thread=False)
cursor = connection.cursor()
Sqlquery = 'create table if not exists users(id int primary key, name text, username text, lastname text)'
cursor.execute(Sqlquery)
connection.commit()


def send(id, text):
    bot.send_message(id, text, reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send(message.chat.id, "Клавиатура подключена")
    bot.reply_to(message,
                 "Добро пожаловать, что вас интересует? Используйте /help, для того, чтобы ознакомиться с краткой спракой для моего функционирования")

    userid = message.from_user.id
    userfirstname = message.from_user.first_name
    userlastname = message.from_user.last_name
    username = message.from_user.username
    Sqlquery = "select * from users where id = '{0}'".format(userid)
    cursor.execute(Sqlquery)
    if cursor.fetchone() == None:
        assert isinstance(userid, object)
        sqlquery = 'insert into users(name, username, id, lastname) values("{0}","{1}","{2}", "{3}")'.format(
            userfirstname, username, userid, userlastname)
        cursor.execute(sqlquery)
        connection.commit()


@bot.message_handler(commands=['send'])
def process_start(message):
    if int(message.chat.id) == config.owner:
        try:
            bot.send_message(message.chat.id, 'Для отправки сообщения сделай реплей')
            bot.forward_message(config.owner, message.chat.id, message.message_id)
            bot.register_next_step_handler(message, process_mind)
        except:
            bot.send_message(message.chat.id,
                             "Что-то пошло не так! Ошибка возникла в блоке кода:\n<code>@bot.message_handler(commands=['send_message'])</code>",
                             parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь администратором для выполнения этой команды!')


def process_mind(message):
    if int(message.chat.id) == config.owner:
        try:
            text = 'Сообщение было отправлено пользователю ' + str(message.reply_to_message.forward_from.first_name)
            bot.forward_message(message.reply_to_message.forward_from.id, config.owner, message.message_id)
            bot.send_message(config.owner, text)
        except:
            bot.send_message(message.chat.id,
                             'Что-то пошло не так! Бот продолжил свою работу.' + ' Ошибка произошла в блоке кода:\n\n <code>def process_mind(message)</code>',
                             parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь администратором для выполнения этой команды!')


@bot.message_handler(commands=['id'])
def process_start(message):
    bot.send_message(message.chat.id, "Твой ID: " + str(message.from_user.id), parse_mode='HTML')
    bot.forward_message(config.owner, message.chat.id, message.message_id)


@bot.message_handler(commands=["help"])
def start(message):
    bot.send_message(message.chat.id,
                     'Приветствую, я бот-ассистент под покровительством компании "Адей". Тут вы можете обратиться за обратной связью к нашим работникам, приобрести необходимые продукты, для разработки на 1С, а также оставить заявку на вызов специалиста с почасовой оплатой труда. А ещё этот бот создан для обратной связи с нашими работниками. Дополнительные команды:\n\n/ping — проверяет работоспособность бота\n/id — показывает твой ID\nКнопка "обратная связь" — подсказывает, как отправить сообщение напрямую администратору\nКнопка "покупка услуг" — перенаправляет вас на сайт для выбора и покупок товаров и услуг для работы с 1с и платформы Windows, а так же для автоматизации способов оплаты на вашем производстве\nКнопка "заявка" — Помогает вам заполнить заявку на вызов специалиста')
    bot.send_message(config.owner,
                     'Привет, хозяин! ' + str(message.from_user.first_name) + ' использовал команду /help')
    bot.forward_message(config.owner, message.chat.id, message.message_id)


@bot.message_handler(commands=["feedback"])
def messages(message):
    if int(message.chat.id) == config.owner:
        try:
            bot.send_message(message.chat.id, 'Сообщение от администратора было получено')
        except:
            bot.send_message(config.owner,
                             'Что-то пошло не так!! Бот продолжил свою работу.' + ' Ошибка произошла в блоке кода:\n\n <code>@bot.message_handler(content_types=["text"])</code>',
                             parse_mode='HTML')
    else:
        pass
        try:
            bot.forward_message(config.owner, message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             str(message.from_user.first_name) + ',' + ' я получил сообщение и очень скоро на него отвечу :)')
        except:
            bot.send_message(config.owner, 'Что-то пошло не так! Бот продолжил свою работу.')




#@bot.callback_query_handler(func=lambda call: True)
#def callback_worker(call):
 #     if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
   #     Sqlquery = 'create table if not exists feedback(id integer primary key autoincrement not null, message text, userid int)'
    #    cursor.execute(Sqlquery)
     #   connection.commit()
      #  msg = call.message.text
       # msg = msg.replace("Это ваше обращение? \n ", "")
        #Sqlquery = 'insert into feedback(message, userid) values("{0}", "{1}")'.format(msg, call.message.from_user.id)
        #cursor.execute(Sqlquery)
        #connection.commit()
        #bot.send_message(call.message.chat.id, 'Сейчас передам сотрудникам')
    #elif call.data == "no":
        #bot.send_message(call.message.chat.id, "Отправьте обращение заново")  # переспрашиваем


#def obr(question):
    #answer = yield question
    #return answer


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
                     'Приветствую, я бот-ассистент под покровительством компании "Адей". Тут вы можете обратиться за обратной связью к нашим работникам, приобрести необходимые продукты, для разработки на 1С, а также оставить заявку на вызов специалиста с почасовой оплатой труда.')


@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text
    if message.text.lower() == 'заявка':
        send(id, 'Используйте команду /reg для составления заявки')
    elif msg == 'Покупка услуг':
        send(id,
             'Для покупки продуктов и вызова специалиста воспользуйтесь нашим сайтом https://adey.ru/magazin , чтобы избежать неприятностей с оплатой и дальнейшим получением купленного продукта')
    elif message.text.lower() == 'обратная связь':
        send(id, "Используйте команду /feedback *****, где ***** - ваше обращение")
    else:
        send(id, 'Не понимаю вас, я не искусственый интеллект, пожалуйста, воспользуйся командами /start; /info;')


if __name__ == '__main__':
    bot.polling(none_stop=True)
