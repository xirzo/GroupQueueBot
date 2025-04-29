import telebot, requests
from telebot import types
import urllib.parse

from dotenv import dotenv_values

CONFIG = dotenv_values(".env")
TOKEN = CONFIG['TOKEN']
BACKEND_URL = CONFIG['BACKEND_URL']

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def show_menu(message):
    show_lists = types.InlineKeyboardButton('📋 Показать списки', callback_data='show_lists')
    group = types.InlineKeyboardButton('👥 Отобразить группу', callback_data='show_all_users')
    add_list = types.InlineKeyboardButton('➕ Добавить список', callback_data='add_list')
    remove_list = types.InlineKeyboardButton('🗑️ Удалить список', callback_data='remove_list')

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(show_lists)
    keyboard.add(group)
    keyboard.add(add_list)
    keyboard.add(remove_list)

    bot.send_message(
        message.chat.id, 
        '👋 Привет, это *Group Queue Bot!* Выбери команду', 
        reply_markup=keyboard, 
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_router(callback):
    if callback.data == 'show_lists':
        handle_show_lists(callback)

    elif callback.data == 'show_all_users':
        handle_show_all_users(callback)
    
    elif callback.data == 'add_list':
        handle_add_list(callback)

    elif callback.data == 'remove_list':
        handle_remove_list(callback)
    
    elif callback.data == 'back_to_main':
        handle_back_to_main(callback)

    elif callback.data == 'back_to_show_lists':
        handle_back_to_show_lists(callback)

    elif callback.data == 'back_to_remove_lists':
        handle_back_to_remove_lists(callback)
    
    elif callback.data.startswith('show_list_'):
        handle_show_list_details(callback)

    elif callback.data.startswith('remove_list_'):
        handle_remove_list_details(callback)


def handle_show_lists(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '📭 Списков нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '📭 Списков нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        text = '📋 Списки:\n\n'
        
        for list_item in lists:
            decoded_name = urllib.parse.unquote(list_item['name'])
            text += f"{list_item['list_id']}. {decoded_name}\n"

        keyboard = types.InlineKeyboardMarkup()
        
        for list_item in lists:
            decoded_name = urllib.parse.unquote(list_item['name'])
            show_list_button = types.InlineKeyboardButton(
                f"👁️ Показать {decoded_name}", 
                callback_data=f"show_list_{list_item['list_id']}"
            )
            keyboard.add(show_list_button)
        
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        error_message = f"❌ Ошибка при получении списков: {str(e)}"
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, "📭 Списков нет или произошла ошибка при их получении. Вы можете добавить новый список.", reply_markup=keyboard)

def handle_show_all_users(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_users')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '👤 Участников группы нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '👤 Участников группы нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        text = '👥 Участники:\n\n'
        
        counter = 1

        for user in lists:
            text += f"{str(counter)}. {user['surname']} {user['first_name']} {user['second_name']}\n"
            counter += 1

        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        error_message = f"❌ Ошибка при получении участников: {str(e)}"
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, "👤 Участников нет или произошла ошибка при их получении.", reply_markup=keyboard)

def handle_add_list(callback):
    chat_id = callback.message.chat.id
    user_states[chat_id] = 'adding_list'
    bot.send_message(chat_id, "✏️ Введите название нового списка:")


def handle_remove_list(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '📭 Нет списков для удаления.'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '📭 Нет списков для удаления'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        keyboard = types.InlineKeyboardMarkup()
        
        for list_item in lists:
            decoded_name = urllib.parse.unquote(list_item['name'])
            remove_list_button = types.InlineKeyboardButton(
                f"🗑️ Удалить {decoded_name}", 
                callback_data=f"remove_list_{list_item['list_id']}"
            )
            keyboard.add(remove_list_button)
        
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)

        text = '❓ Выберите список для удаления'

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        error_message = f"❌ Ошибка при получении списков: {str(e)}"
        print(error_message)  
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, "📭 Нет списков для удаления или произошла ошибка при их получении.", reply_markup=keyboard)

def handle_back_to_main(callback):
    show_menu(callback.message)

def handle_back_to_show_lists(callback):
    handle_show_lists(callback)

def handle_back_to_remove_lists(callback):
    handle_remove_list(callback)

def handle_show_list_details(callback):
    try:
        list_id = callback.data.replace('show_list_', '')
        
        list_user_resp = requests.get(f'{BACKEND_URL}/get_list_users/{list_id}')
        list_user_resp.raise_for_status()
        list_users = list_user_resp.json()

        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()

        text = "👥 Участники списка:\n\n"
        counter = 1

        user_dict = {str(user['user_id']): user for user in users}
        
        sorted_list_users = sorted(list_users, key=lambda x: x.get('list_user_order', counter))

        for list_user in sorted_list_users:
            user_id = str(list_user['user_id'])
            if user_id in user_dict:
                user = user_dict[user_id]
                text += f"{counter}. {user['surname']} {user['first_name']} {user.get('second_name', '')}\n"
                counter += 1

        if counter == 1:
            text += "📭 Список пуст."

        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_show_lists")
        keyboard.add(back_button)

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        bot.send_message(callback.message.chat.id, f"❌ Ошибка при получении данных списка: {e}")


def handle_remove_list_details(callback):
    try:
        list_id = callback.data.replace('remove_list_', '')
        
        resp = requests.delete(f'{BACKEND_URL}/remove_list/{list_id}')
        resp.raise_for_status()

        text = f'✅ Список успешно удален!'

        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_remove_lists")
        keyboard.add(back_button)

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        bot.send_message(callback.message.chat.id, f"❌ Ошибка при удалении списка: {e}")

user_states = {}

@bot.message_handler(func=lambda message: True)
def handle_text_input(message):
    chat_id = message.chat.id
    
    current_state = user_states.get(chat_id)
    
    if current_state == 'adding_list':
        list_name = message.text.strip()
        
        if not list_name:
            bot.send_message(chat_id, "⚠️ Название списка не может быть пустым. Попробуйте еще раз:")
            return
        
        try:
            response = requests.post(f'{BACKEND_URL}/add_list/{list_name}')
            response.raise_for_status()
            
            bot.send_message(chat_id, f"✅ Список '{list_name}' успешно добавлен!")
            
            user_states.pop(chat_id, None)
            
            show_menu(message)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при добавлении списка: {e}")
            user_states.pop(chat_id, None)
            show_menu(message)
    else:
        bot.send_message(chat_id, "ℹ️ Используйте кнопки меню для взаимодействия с ботом.")
        show_menu(message)

if __name__ == "__main__":
    bot.infinity_polling()
