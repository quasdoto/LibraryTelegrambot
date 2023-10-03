import telebot
from telebot import types
import json
import os

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))  
books = load_json(os.path.join(BASE_PATH, 'books.json'))

def get_books_by_genre(genre):
    return [book for book in books if book['genre'] == genre]

def get_book_by_id(id):
    for book in books:
        if book['id'] == id:
            return book
    return None

bot = telebot.TeleBot('your_token')

buttons_genre = {'💻IT':'IT', '💼Бизнес':'Business', '📈Трейдинг':'Trading', '🧠Саморазвитие':'Self Improvement', '📖Психология':'Psychology'}

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in buttons_genre:
        markup.add(types.KeyboardButton(btn))
        
    bot.send_message(message.chat.id, "Привет👋, {0.first_name}!\nЯ - <b>{1.first_name}</b>, я храню в себе множество книг, темы(жанры) которых ты видишь на кнопочках ниже на панели, нажми на нее и тебе предложат список".format(message.from_user, bot.get_me()),
    parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def msg(message):
    if message.text in buttons_genre:
        genre = buttons_genre[message.text]
        markup = types.InlineKeyboardMarkup(row_width=2)
        genre_books = get_books_by_genre(genre)
        if not genre_books:
            bot.send_message(message.chat.id, 'К сожалению, в настоящее время нет книг, относящихся к этому жанру.')
            return 
        for book in genre_books:
            markup.add(types.InlineKeyboardButton(book['title'], callback_data ='book_' + book['id']))
        bot.send_message(message.chat.id, 'Ниже представлены все книги на тему {}'.format(genre), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith('book_'):
        data = call.data.split('_')
        book_id = data[1]

        if len(data) == 3:
            part_id = int(data[2])
            book = get_book_by_id(book_id)
            if book and 0 < part_id <= len(book['parts']):
                text = book['parts'][part_id - 1]
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(types.InlineKeyboardButton('⬅️Вернуться к описанию', callback_data='book_' + book_id))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)
                return

        book = get_book_by_id(book_id)
        if book:
            text = book['description'] + '\n\nГод выпуска: ' + book['year'] + '\n\nСтатус: ' + book['status']
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton('⬅️Вернуться к списку', callback_data='back_' + book_id))
            for i in range(len(book['parts'])):
                markup.add(types.InlineKeyboardButton(str(i + 1), callback_data='book_' + book_id + '_' + str(i + 1)))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Sorry, can't find the book!")
    elif call.data.startswith('back_'):
        book_id = call.data.split('_')[1]
        genre = get_book_by_id(book_id)['genre']
        markup = types.InlineKeyboardMarkup(row_width=2)
        genre_books = get_books_by_genre(genre)
        for book in genre_books:
            markup.add(types.InlineKeyboardButton(book['title'], callback_data='book_' + book['id']))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Ниже представлены все книги на тему {}'.format(genre), reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Sorry, can't find the book!")

bot.polling(none_stop=True)
