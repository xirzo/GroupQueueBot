import telebot, requests
from telebot import types
import urllib.parse
import uuid
from datetime import datetime, timedelta
import threading
import time

from dotenv import dotenv_values

CONFIG = dotenv_values(".env")
TOKEN = CONFIG['TOKEN']
BACKEND_URL = CONFIG['BACKEND_URL']

bot = telebot.TeleBot(TOKEN)

user_states = {}
swap_state = {}
user_id_map = {}
pending_swaps = {}

@bot.message_handler(commands=['start'])
def show_menu(message):
    show_lists = types.InlineKeyboardButton('📋 Показать списки', callback_data='show_lists')
    group = types.InlineKeyboardButton('👥 Отобразить группу', callback_data='show_all_users')
    add_list = types.InlineKeyboardButton('➕ Добавить список', callback_data='add_list')
    remove_list = types.InlineKeyboardButton('🗑️ Удалить список', callback_data='remove_list')
    swap = types.InlineKeyboardButton('🔄 Предложить обмен', callback_data='swap')

    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    keyboard.add(show_lists)
    keyboard.add(swap)
    keyboard.add(group)
    keyboard.add(add_list)
    keyboard.add(remove_list)

    bot.send_message(
        message.chat.id, 
        'Привет, это *Group Queue Bot!* Выбери команду', 
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

    elif callback.data == 'swap':
        handle_swap(callback)
    
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

    elif callback.data.startswith('swap_list_'):
        handle_swap_list_selection(callback)
    
    elif callback.data.startswith('swap_first_user_'):
        handle_swap_first_user_selection(callback)
    
    elif callback.data.startswith('swap_second_user_'):
        handle_swap_second_user_selection(callback)
    
    elif callback.data.startswith('confirm_swap_'):
        handle_confirm_swap(callback)
        
    elif callback.data.startswith('accept_swap_'):
        handle_accept_swap(callback)
    
    elif callback.data.startswith('reject_swap_'):
        handle_reject_swap(callback)
    
    elif callback.data.startswith('cancel_swap_'):
        handle_cancel_swap(callback)


def handle_show_lists(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '📋 Списков нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '📋 Списков нет'
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
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, "📋 Списков нет или произошла ошибка при их получении. Вы можете добавить новый список.", reply_markup=keyboard)

def handle_show_all_users(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_users')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '👥 Участников группы нет'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '👥 Участников группы нет'
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
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, "👥 Участников нет или произошла ошибка при их получении. Вы можете добавить новый список.", reply_markup=keyboard)

def handle_add_list(callback):
    chat_id = callback.message.chat.id
    user_states[chat_id] = 'adding_list'
    bot.send_message(chat_id, "✏️ Введите название нового списка:")


def handle_remove_list(callback):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        
        if not resp.text or resp.text.strip() == '':
            text = '🗑️ Нет списков для удаления.'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        lists = resp.json()
        
        if not lists:
            text = '🗑️ Нет списков для удаления'
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

        text = '🗑️ Выберите список для удаления'

        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, "🗑️ Нет списков для удаления или произошла ошибка при их получении.", reply_markup=keyboard)


def handle_swap(callback):
    try:
        telegram_id = callback.from_user.id
        
        sender_resp = requests.get(f'{BACKEND_URL}/get_user_by_telegram_id/{telegram_id}')
        sender_resp.raise_for_status()
        sender_data = sender_resp.json()
        
        sender_id = str(sender_data['user_id'])
        
        swap_state[callback.message.chat.id] = {
            'sender_id': sender_id,
            'sender_name': f"{sender_data['surname']} {sender_data['first_name']}"
        }
        
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        list_data = resp.json()
        
        if not list_data:
            text = '🔄 Нет доступных списков для обмена'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        text = '🔄 Выберите список для обмена:\n\n'
        keyboard = types.InlineKeyboardMarkup()
        
        for list_item in list_data:
            decoded_name = urllib.parse.unquote(list_item['name'])
            list_button = types.InlineKeyboardButton(
                f"{decoded_name}", 
                callback_data=f"swap_list_{list_item['list_id']}"
            )
            keyboard.add(list_button)
            
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=keyboard)

def handle_swap_list_selection(callback):
    list_id = callback.data.replace('swap_list_', '')
    
    if callback.message.chat.id in swap_state:
        swap_state[callback.message.chat.id]['list_id'] = list_id
    else:
        swap_state[callback.message.chat.id] = {
            'list_id': list_id
        }
    
    try:
        list_user_resp = requests.get(f'{BACKEND_URL}/get_list_users/{list_id}')
        list_user_resp.raise_for_status()
        list_users = list_user_resp.json()

        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()
        
        if not users or not list_users:
            text = '👥 В этом списке нет участников'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        user_dict = {str(user['user_id']): user for user in users}
        
        user_id_map[callback.message.chat.id] = user_dict
        
        sender_id = swap_state[callback.message.chat.id].get('sender_id')
        
        sender_in_list = any(str(user['user_id']) == sender_id for user in list_users)
        
        if not sender_in_list:
            text = '⚠️ Вы не являетесь участником этого списка и не можете выполнить обмен.'
            keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
            keyboard.add(back_button)
            bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
            return
            
        text = '👤 Выберите участника для обмена с вами:\n\n'
        keyboard = types.InlineKeyboardMarkup()
        
        sorted_list_users = sorted(list_users, key=lambda x: x.get('list_user_order', 0))
        
        for list_user in sorted_list_users:
            user_id = str(list_user['user_id'])
            
            if user_id == sender_id:
                continue
                
            if user_id in user_dict:
                user = user_dict[user_id]
                full_name = f"{user['surname']} {user['first_name']} {user.get('second_name', '')}"
                user_button = types.InlineKeyboardButton(
                    full_name, 
                    callback_data=f"swap_second_user_{list_id}_{sender_id}_{user_id}"
                )
                keyboard.add(user_button)
        
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=keyboard)

def handle_swap_first_user_selection(callback):
    parts = callback.data.split('_')
    
    list_id = parts[3]
    first_user_id = parts[4]
    
    print(f"Selected list_id: {list_id}, first_user_id: {first_user_id}")
    
    swap_state[callback.message.chat.id] = {
        'list_id': list_id,
        'first_user_id': first_user_id
    }
    
    try:
        list_user_resp = requests.get(f'{BACKEND_URL}/get_list_users/{list_id}')
        list_user_resp.raise_for_status()
        list_users = list_user_resp.json()
        
        user_dict = user_id_map.get(callback.message.chat.id, {})

        if not user_dict:
            users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
            users_resp.raise_for_status()
            users = users_resp.json()
            user_dict = {str(user['user_id']): user for user in users}
            user_id_map[callback.message.chat.id] = user_dict
        
        first_user = user_dict.get(first_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        first_user_name = f"{first_user['surname']} {first_user['first_name']}"
        
        text = f'👤 Вы выбрали: {first_user_name}\nТеперь выберите второго участника для обмена:\n\n'
        keyboard = types.InlineKeyboardMarkup()
        
        sorted_list_users = sorted(list_users, key=lambda x: x.get('list_user_order', 0))
        
        for list_user in sorted_list_users:
            user_id = str(list_user['user_id'])
            if user_id == first_user_id:
                continue
                
            if user_id in user_dict:
                user = user_dict[user_id]
                full_name = f"{user['surname']} {user['first_name']} {user.get('second_name', '')}"
                user_button = types.InlineKeyboardButton(
                    full_name, 
                    callback_data=f"swap_second_user_{list_id}_{first_user_id}_{user_id}"
                )
                keyboard.add(user_button)
        
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data=f"swap_list_{list_id}")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, "❌ Произошла ошибка при выборе участников.", reply_markup=keyboard)

def handle_swap_second_user_selection(callback):
    parts = callback.data.split('_')
    
    list_id = parts[3]
    first_user_id = parts[4]
    second_user_id = parts[5]
    
    print(f"Creating swap request in list {list_id}: user {first_user_id} with user {second_user_id}")
    
    try:
        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()
        
        user_dict = {str(user['user_id']): user for user in users}
        user_id_map[callback.message.chat.id] = user_dict
        
        first_user = user_dict.get(first_user_id)
        if not first_user:
            raise Exception(f"First user with ID {first_user_id} not found!")
            
        second_user = user_dict.get(second_user_id)
        if not second_user:
            raise Exception(f"Second user with ID {second_user_id} not found!")
        
        first_user_name = f"{first_user.get('surname', 'Unknown')} {first_user.get('first_name', 'User')}"
        second_user_name = f"{second_user.get('surname', 'Unknown')} {second_user.get('first_name', 'User')}"
        
        second_user_telegram_id = second_user.get('telegram_id')
        if not second_user_telegram_id:
            raise Exception(f"Telegram ID not found for user {second_user_name}")
        
        swap_id = str(uuid.uuid4())
        
        pending_swaps[swap_id] = {
            'list_id': list_id,
            'first_user_id': first_user_id,
            'second_user_id': second_user_id,
            'initiator_chat_id': callback.message.chat.id,
            'created_at': datetime.now(),
            'status': 'pending'
        }
        
        text = f'✅ Запрос на обмен отправлен!\n\nВы хотите поменяться местами с {second_user_name}\n\nОжидайте подтверждения...'
        keyboard = types.InlineKeyboardMarkup()
        cancel_button = types.InlineKeyboardButton(
            "❌ Отменить запрос", 
            callback_data=f"cancel_swap_{swap_id}"
        )
        keyboard.add(cancel_button)
        
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
        
        request_text = f'📩 Запрос на обмен!\n\n{first_user_name} хочет поменяться с вами местами в списке "{get_list_name(list_id)}".\n\nПринять запрос?'
        request_keyboard = types.InlineKeyboardMarkup()
        
        accept_button = types.InlineKeyboardButton(
            "✅ Принять", 
            callback_data=f"accept_swap_{swap_id}"
        )
        request_keyboard.add(accept_button)
        
        reject_button = types.InlineKeyboardButton(
            "❌ Отклонить", 
            callback_data=f"reject_swap_{swap_id}"
        )
        request_keyboard.add(reject_button)
        
        try:
            bot.send_message(second_user_telegram_id, request_text, reply_markup=request_keyboard)
        except Exception as e:
            bot.send_message(
                callback.message.chat.id, 
                f"⚠️ Не удалось отправить запрос пользователю {second_user_name}. Возможно, он не начал чат с ботом.",
                reply_markup=keyboard
            )
            print(f"Failed to send swap request: {e}")
    
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=keyboard)

def get_list_name(list_id):
    try:
        resp = requests.get(f'{BACKEND_URL}/get_all_lists')
        resp.raise_for_status()
        lists = resp.json()
        
        for list_item in lists:
            if str(list_item['list_id']) == str(list_id):
                return urllib.parse.unquote(list_item['name'])
        
        return "Неизвестный список"
    except Exception:
        return "Неизвестный список"

def handle_accept_swap(callback):
    swap_id = callback.data.replace('accept_swap_', '')
    
    if swap_id not in pending_swaps:
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен больше не действителен.")
        return
    
    swap_data = pending_swaps[swap_id]
    
    if swap_data['status'] != 'pending':
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен уже был обработан.")
        return
    
    try:
        list_id = swap_data['list_id']
        first_user_id = swap_data['first_user_id']
        second_user_id = swap_data['second_user_id']
        initiator_chat_id = swap_data['initiator_chat_id']
        
        swap_response = requests.post(f'{BACKEND_URL}/swap/{list_id}/{first_user_id}/{second_user_id}')
        swap_response.raise_for_status()
        
        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()
        user_dict = {str(user['user_id']): user for user in users}
        
        first_user = user_dict.get(first_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        second_user = user_dict.get(second_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        
        first_user_name = f"{first_user['surname']} {first_user['first_name']}"
        second_user_name = f"{second_user['surname']} {second_user['first_name']}"
        
        pending_swaps[swap_id]['status'] = 'completed'
        
        text = f'✅ Обмен выполнен успешно!\n\nВы ({second_user_name}) поменялись местами с {first_user_name}'
        
        keyboard = types.InlineKeyboardMarkup()
        view_list_button = types.InlineKeyboardButton(
            "👁️ Посмотреть обновленный список", 
            callback_data=f"show_list_{list_id}"
        )
        keyboard.add(view_list_button)
        
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
        
        initiator_text = f'✅ {second_user_name} принял ваш запрос на обмен!\n\nВы ({first_user_name}) поменялись местами с {second_user_name}'
        
        initiator_keyboard = types.InlineKeyboardMarkup()
        initiator_view_button = types.InlineKeyboardButton(
            "👁️ Посмотреть обновленный список", 
            callback_data=f"show_list_{list_id}"
        )
        initiator_keyboard.add(initiator_view_button)
        
        initiator_back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        initiator_keyboard.add(initiator_back_button)
        
        bot.send_message(initiator_chat_id, initiator_text, reply_markup=initiator_keyboard)
        
    except Exception as e:
        print(f"Error accepting swap: {str(e)}")
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка при выполнении обмена: {str(e)}", reply_markup=keyboard)
        
        try:
            bot.send_message(
                initiator_chat_id, 
                f"⚠️ Произошла ошибка при обработке вашего запроса на обмен с {second_user_name}.",
                reply_markup=keyboard
            )
        except:
            pass

def handle_reject_swap(callback):
    swap_id = callback.data.replace('reject_swap_', '')
    
    if swap_id not in pending_swaps:
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен больше не действителен.")
        return
    
    swap_data = pending_swaps[swap_id]
    
    if swap_data['status'] != 'pending':
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен уже был обработан.")
        return
    
    try:
        list_id = swap_data['list_id']
        first_user_id = swap_data['first_user_id']
        second_user_id = swap_data['second_user_id']
        initiator_chat_id = swap_data['initiator_chat_id']
        
        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()
        user_dict = {str(user['user_id']): user for user in users}
        
        first_user = user_dict.get(first_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        second_user = user_dict.get(second_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        
        first_user_name = f"{first_user['surname']} {first_user['first_name']}"
        second_user_name = f"{second_user['surname']} {second_user['first_name']}"
        
        pending_swaps[swap_id]['status'] = 'rejected'
        
        text = f'❌ Вы отклонили запрос на обмен от {first_user_name}'
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
        
        initiator_text = f'❌ {second_user_name} отклонил ваш запрос на обмен.'
        
        initiator_keyboard = types.InlineKeyboardMarkup()
        new_swap_button = types.InlineKeyboardButton("🔄 Создать новый запрос", callback_data="swap")
        initiator_keyboard.add(new_swap_button)
        
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        initiator_keyboard.add(back_button)
        
        bot.send_message(initiator_chat_id, initiator_text, reply_markup=initiator_keyboard)
        
    except Exception as e:
        print(f"Error rejecting swap: {str(e)}")
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=keyboard)

def handle_cancel_swap(callback):
    swap_id = callback.data.replace('cancel_swap_', '')
    
    if swap_id not in pending_swaps:
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен больше не действителен.")
        return
    
    swap_data = pending_swaps[swap_id]
    
    if swap_data['status'] != 'pending':
        bot.send_message(callback.message.chat.id, "⚠️ Этот запрос на обмен уже был обработан.")
        return
    
    try:
        list_id = swap_data['list_id']
        first_user_id = swap_data['first_user_id']
        second_user_id = swap_data['second_user_id']
        
        users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
        users_resp.raise_for_status()
        users = users_resp.json()
        user_dict = {str(user['user_id']): user for user in users}
        
        first_user = user_dict.get(first_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        second_user = user_dict.get(second_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        
        second_user_name = f"{second_user['surname']} {second_user['first_name']}"
        
        second_user_telegram_id = second_user.get('telegram_id')
        
        pending_swaps[swap_id]['status'] = 'cancelled'
        
        text = f'❌ Вы отменили запрос на обмен с {second_user_name}'
        
        keyboard = types.InlineKeyboardMarkup()
        new_swap_button = types.InlineKeyboardButton("🔄 Создать новый запрос", callback_data="swap")
        keyboard.add(new_swap_button)
        
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
        
        if second_user_telegram_id:
            try:
                cancel_text = f'❌ Запрос на обмен с вами был отменен инициатором.'
                cancel_keyboard = types.InlineKeyboardMarkup()
                cancel_back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
                cancel_keyboard.add(cancel_back_button)
                
                bot.send_message(second_user_telegram_id, cancel_text, reply_markup=cancel_keyboard)
            except Exception as e:
                print(f"Failed to notify second user about cancellation: {e}")
        
    except Exception as e:
        print(f"Error cancelling swap: {str(e)}")
        
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {str(e)}", reply_markup=keyboard)

def handle_confirm_swap(callback):
    parts = callback.data.split('_')
    
    list_id = parts[2]
    first_user_id = parts[3]
    second_user_id = parts[4]
    
    print(f"Confirming swap in list {list_id}: user {first_user_id} with user {second_user_id}")
    
    try:
        swap_response = requests.post(f'{BACKEND_URL}/swap/{list_id}/{first_user_id}/{second_user_id}')
        swap_response.raise_for_status()
        
        user_dict = user_id_map.get(callback.message.chat.id, {})
        
        if not user_dict:
            users_resp = requests.get(f'{BACKEND_URL}/get_users/{list_id}')
            users_resp.raise_for_status()
            users = users_resp.json()
            user_dict = {str(user['user_id']): user for user in users}
        
        first_user = user_dict.get(first_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        second_user = user_dict.get(second_user_id, {'surname': 'Unknown', 'first_name': 'User'})
        
        first_user_name = f"{first_user['surname']} {first_user['first_name']}"
        second_user_name = f"{second_user['surname']} {second_user['first_name']}"
        
        if callback.message.chat.id in swap_state:
            del swap_state[callback.message.chat.id]
            
        if callback.message.chat.id in user_id_map:
            del user_id_map[callback.message.chat.id]
        
        text = f'✅ Обмен выполнен успешно!\nВы ({first_user_name}) ↔ {second_user_name}'
        
        keyboard = types.InlineKeyboardMarkup()
        view_list_button = types.InlineKeyboardButton(
            "👁️ Посмотреть обновленный список", 
            callback_data=f"show_list_{list_id}"
        )
        keyboard.add(view_list_button)
        
        back_button = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
        keyboard.add(back_button)
        
        bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Назад", callback_data="swap")
        keyboard.add(back_button)
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка при выполнении обмена: {str(e)}", reply_markup=keyboard)

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
            text += "Список пуст."

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
        bot.send_message(callback.message.chat.id, f"❌ Ошибка при получении данных списка: {e}")

def cleanup_old_swaps():
    expiration_time = datetime.now() - timedelta(days=1)
    
    expired_swap_ids = []
    for swap_id, swap_data in pending_swaps.items():
        if swap_data['status'] == 'pending' and swap_data['created_at'] < expiration_time:
            expired_swap_ids.append(swap_id)
    
    for swap_id in expired_swap_ids:
        pending_swaps[swap_id]['status'] = 'expired'
        
        try:
            initiator_chat_id = pending_swaps[swap_id]['initiator_chat_id']
            bot.send_message(
                initiator_chat_id, 
                "⏱ Ваш запрос на обмен истек, так как не был обработан в течение 24 часов."
            )
        except:
            pass

def background_cleanup():
    while True:
        time.sleep(3600)
        cleanup_old_swaps()

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
        bot.send_message(chat_id, "⚠️ Используйте кнопки меню для взаимодействия с ботом.")
        show_menu(message)

if __name__ == "__main__":
    cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
    cleanup_thread.start()
    bot.infinity_polling()
