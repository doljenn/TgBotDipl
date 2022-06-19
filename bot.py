import telebot
from time import sleep
import config
import logging
import datetime
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) 
bot = telebot.TeleBot(token = config.token, threaded=False, skip_pending=False)

@bot.message_handler(commands=["ping"]) #Создаем команду
def start(message):
	try: #Заворачиваем все в try
		bot.send_message(message.chat.id, "<b>PONG!</b>" , parse_mode="HTML") 
		bot.forward_message(config.owner, message.chat.id, message.message_id)
	except:
		bot.send_message(config.owner, 'Что-то пошло не так!') #Данная система (оборачивание в try и except позволит продолжить выполнение кода, даже если будут ошибки)


@bot.message_handler(commands=["start"])
def start(message):
	bot.send_message(message.chat.id,  'Привет, ' + str(message.from_user.first_name) +'!\n' 'Напиши /help для просмотра возможностей бота.')
	bot.forward_message(config.owner, message.chat.id, message.message_id)	
	if int(message.chat.id) == int(config.blacklist):
			pass

@bot.message_handler(commands=['send'])
def process_start(message):
	if int(message.chat.id) == config.owner:
		try:
			bot.send_message(message.chat.id, 'Для отправки сообщения сделай реплей')
			bot.forward_message(config.owner, message.chat.id, message.message_id)
			bot.register_next_step_handler(message, process_mind)
		except:
			bot.send_message(message.chat.id, "Что-то пошло не так! Ошибка возникла в блоке кода:\n<code>@bot.message_handler(commands=['send_message'])</code>", parse_mode='HTML')
	else:
		bot.send_message(message.chat.id, 'Вы не являетесь администратором для выполнения этой команды!')


def process_mind(message):
	if int(message.chat.id) == config.owner:
		try:
			text = 'Сообщение было отправлено пользователю ' + str(message.reply_to_message.forward_from.first_name)
			bot.forward_message(message.reply_to_message.forward_from.id, config.owner, message.message_id)
			bot.send_message(config.owner, text)
		except:
			bot.send_message(message.chat.id, 'Что-то пошло не так! Бот продолжил свою работу.' + ' Ошибка произошла в блоке кода:\n\n <code>def process_mind(message)</code>', parse_mode='HTML')
	else:
		bot.send_message(message.chat.id, 'Вы не являетесь администратором для выполнения этой команды!')




@bot.message_handler(commands=['id'])
def process_start(message):
	bot.send_message(message.chat.id, "Твой ID: " + str(message.from_user.id), parse_mode = 'HTML')
	bot.forward_message(config.owner, message.chat.id, message.message_id)


@bot.message_handler(commands=["help"])
def start(message):
	bot.send_message(message.chat.id, 'Приветствую, я бот-ассистент под покровительством компании "Адей". Тут вы можете обратиться за обратной связью к нашим работникам, приобрести необходимые продукты, для разработки на 1С, а также оставить заявку на вызов специалиста с почасовой оплатой труда. А ещё этот бот создан для обратной связи с нашими работниками. Для этого просто напишите сообщение, я его получу и отвечу. Дополнительные команды:\n\n/ping — проверяет работоспособность бота\n/id — показывает твой ID' )
	bot.send_message(config.owner,'Привет, хозяин! ' + str(message.from_user.first_name) + ' использовал команду /help')
	bot.forward_message(config.owner, message.chat.id, message.message_id)

@bot.message_handler(content_types=["text"])
def messages(message):
	if int(message.chat.id) == config.owner:
		try:
			bot.send_message(message.chat.id, 'Сообщение от администратора было получено')
		except:
			bot.send_message(config.owner, 'Что-то пошло не так! Бот продолжил свою работу.' + ' Ошибка произошла в блоке кода:\n\n <code>@bot.message_handler(content_types=["text"])</code>', parse_mode='HTML')
	else:
		pass
		try:
			bot.forward_message(config.owner, message.chat.id, message.message_id)
			bot.send_message(message.chat.id, str(message.from_user.first_name) + ',' +' я получил сообщение и очень скоро на него отвечу :)')
		except:
			bot.send_message(config.owner, 'Что-то пошло не так! Бот продолжил свою работу.')
		
		

@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text
    if message.text.lower() == 'обратная связь':
        bot.send_message(id, "Используйте команду /feedback, для того, чтобы оставить сообщение разработчику")
    elif msg == 'Покупка услуг':
        bot.send_message(id, 'Для покупки продуктов и вызова специалиста воспользуйтесь нашим сайтом https://adey.ru/magazin , чтобы избежать неприятностей с оплатой и дальнейшим получением купленного продукта')
    else:
        bot.send_message(id, 'Не понимаю вас, я не искусственый интеллект, пожалуйста, воспользуйся командами /start; /info;')
	

bot.send_message(config.owner, 'Скрипт полностью запущен, бот функционирует! Используй /send для отправки сообщения :)')

if __name__ == '__main__':
        bot.polling(none_stop = True)

    
       