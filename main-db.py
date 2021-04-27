# -*- coding: utf8 -*-
import telebot
import random
from telebot import types
import config
import threading
import psycopg2
import os
import time
#DATABASE_URL = os.environ['DATABASE_URL']
global db
global sql
db = psycopg2.connect(database='d6ipfqeahpii9', user='tualpgdacfdowa', port="5432", password='415217eb3e4acb039e30c4ff760b49c478935253484832ffe9e16467eb9007f3', host='ec2-52-23-45-36.compute-1.amazonaws.com', sslmode='require')
sql=db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS players (chatid TEXT, username TEXT, cash INT, inbank INT, total INT, job_blocked TEXT)""")
db.commit()
sql.execute("""CREATE TABLE IF NOT EXISTS developers (chatid TEXT)""")
db.commit()
sql.execute("""CREATE TABLE IF NOT EXISTS referals (refchatid TEXT, refusername TEXT, tochatid TEXT, tousername TEXT, reftotal INT)""")
db.commit()
sql.execute("DROP TABLE IF EXISTS rollcoop")
db.commit()
sql.execute("""CREATE TABLE IF NOT EXISTS rollcoop (fchatid TEXT, schatid TEXT, fscore INT, sscore INT, wincash INT)""")
db.commit()



global coop_roll_bet
coop_roll_bet=random.choice([500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])

bot=telebot.TeleBot(config.TOKEN)


def starting_unblocking():
    sql.execute(f"SELECT chatid FROM players WHERE job_blocked = 'blocked'")
    rows=sql.fetchall()
    for row in rows:
        sql.execute(f"UPDATE players SET job_blocked = 'unblocked' WHERE chatid = '{row[0]}'")
        db.commit()

starting_unblocking()

@bot.message_handler(commands=['start'])
def welcome(message):
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res is None:
        choose_nickname=bot.send_message(message.from_user.id, "Напишите ваш никнейм для игры (в дальнейшем его можно изменить)")
        bot.register_next_step_handler(choose_nickname, creating_account)

@bot.message_handler(commands=['delacc'])
def choosing_deleting_acc(message):
    adding_keyboard()
    sql.execute(f"SELECT * FROM developers WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res!=None:
        delete_acc=bot.send_message(message.from_user.id, 'Введите имя пользователя, аккаунт которого хотите удалить', reply_markup=markup_reply)
        bot.register_next_step_handler(delete_acc, deleting_acc)
    else:
        return time.sleep(0.5) 

def deleting_acc(message):
    adding_keyboard()
    sql.execute(f"SELECT * FROM players WHERE username = '{message.text}'")
    if sql.fetchone()!=None:
        del_answer_reply = types.InlineKeyboardMarkup()
        del_answer_reply.add(types.InlineKeyboardButton('✅ Да, удалите этот аккаунт', callback_data=f'delete_acc{message.text}'))
        del_answer_reply.add(types.InlineKeyboardButton('❌ Нет, пока не надо', callback_data='no_del_acc'))
        bot.send_message(message.from_user.id, f"Вы уверены, что хотите удалить аккаунт <b>{message.text}</b> со всеми его данными?", parse_mode='html', reply_markup=del_answer_reply)
    else:
        return bot.reply_to(message, f"⚠️ Пользователь не найден. Повторите попытку", reply_markup=markup_reply)


@bot.message_handler(commands=['send'])
def login(message):
    sql.execute(f"SELECT * FROM developers WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res!=None:
        cancel_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_reply.add(types.KeyboardButton('❌ Отменить действие'))
        do_send=bot.send_message(message.from_user.id, "Что будете отправлять пользователям?", reply_markup=cancel_reply)
        bot.register_next_step_handler(do_send, sending)
    else:
        return time.sleep(0.5)

def sending(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    mes=message.text
    sql.execute("SELECT chatid FROM players")
    rows = sql.fetchall()
    for row in rows:
        try:
            #bot.unpin_chat_message(row[0])
            bot.send_message(row[0], mes, parse_mode='html', reply_markup=markup_reply)
            #bot.pin_chat_message(row[0], for_pin.message_id, disable_notification=True)
        except:
            pass
    time.sleep(0.5)

@bot.message_handler(commands=['clear'])
def welcome(message):
    sql.execute(f"SELECT * FROM developers WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res!=None:
        do_clear=bot.send_message(message.from_user.id, 'Введите имя пользователя, аккаунт которого хотите удалить', reply_markup=markup_reply)
        bot.register_next_step_handler(do_clear, clearing)
    else:
        return time.sleep(0.5)

def clearing(message):
    adding_keyboard()
    sql.execute(f"SELECT * FROM players WHERE username = '{message.text}'")
    if sql.fetchone()!=None:
        del_answer_reply = types.InlineKeyboardMarkup()
        del_answer_reply.add(types.InlineKeyboardButton('✅ Да, очистите баланс этого аккаунта', callback_data=f'clear_acc{message.text}'))
        del_answer_reply.add(types.InlineKeyboardButton('❌ Нет, пока не надо', callback_data='no_del_acc'))
        bot.send_message(message.from_user.id, f"Вы уверены, что хотите очистить баланс аккаунта <b>{message.text}</b>?", parse_mode='html', reply_markup=del_answer_reply)
    else:
        return bot.reply_to(message, f"⚠️ Пользователь не найден. Повторите попытку", reply_markup=markup_reply)

@bot.message_handler(commands=['setbank'])
def set_bank(message):
    adding_all()
    sql.execute(f"SELECT * FROM developers WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res!=None:
        choose_user=bot.send_message(message.from_user.id, 'Введите пользователя (или же нажмите на кнопку внизу), которому хотите перечислить деньги', reply_markup=all_reply)
        bot.register_next_step_handler(choose_user, choosing_user)
    else:
        return time.sleep(0.5)    
def choosing_user(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_all()
    touser=message.text
    sql.execute(f"SELECT username FROM players WHERE username = '{touser}'")
    if sql.fetchone() is None and touser.lower()!='все' and touser.lower()!='всем': 
        return
    send_money=bot.send_message(message.from_user.id, 'Какую сумму вы хотите перевести?')
    bot.register_next_step_handler(send_money, sending_money, touser)

def sending_money(message, touser):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    try:
        sending_amount=int(message.text)
        if sending_amount<1:
            return bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с {amount} 💸', reply_markup=markup_reply)
    except:
        return
    if touser.lower()=='все' or touser.lower()=='всем' or touser=='Все 💸':
        sql.execute(f"SELECT chatid, username FROM players")
        rows=sql.fetchall()
        for row in rows:
            sql.execute(f"UPDATE players SET inbank = inbank + {sending_amount}, total = total + {sending_amount} WHERE chatid = '{row[0]}'")
            db.commit()
            try:
                bot.send_message(int(row[0]), f"<b>Уважаемый(ая) {row[1]}</b>! По решению студенческого совета на ваш банковский счёт было перечислено <b>{true_numbers(sending_amount)}</b> 💸", parse_mode='html', reply_markup=markup_reply)
            except:
                pass
    else:
        sql.execute(f"UPDATE players SET inbank = inbank + {sending_amount}, total = total + {sending_amount} WHERE username = '{touser}'")
        db.commit()
        sql.execute(f"SELECT chatid FROM players WHERE username='{touser}'")
        row = int(sql.fetchone()[0])
        try:
            bot.send_message(row, f"<b>Уважаемый(ая) {touser}</b>! По решению студенческого совета на ваш банковский счёт было перечислено <b>{true_numbers(sending_amount)}</b> 💸", parse_mode='html', reply_markup=markup_reply)
        except:
            pass

@bot.message_handler(content_types=['text'])
def chatting(message):
    global coop_roll_bet
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res is None:
        return bot.reply_to(message, "⚠️ Вам не доступна эта команда, так как вы не зарегистрированы в базе данных академии Хяккао. Для регистрации воспользуйтесь командой /start", reply_markup=None)
    global choosing_cash
    adding_keyboard()
    adding_all()
    if message.text=='🎲 Играть в кости':
        choosing_cash=bot.send_message(message.from_user.id, "На какую сумму хотите сыграть? Вы также можете сыграть на все ваши наличные, нажав на кнопку ниже", reply_markup=all_reply)
        bot.register_next_step_handler(choosing_cash, roll_win)
    elif f'🎲 Кости 1 на 1 (Ставка:' in message.text:
        sql.execute(f"SELECT * FROM rollcoop")
        res=sql.fetchone()
        dice_reply=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        dice_reply.add(types.KeyboardButton('❌ Отменить действие'))
        if res==None:
            bot.send_dice(message.from_user.id, emoji='🎲')
            send_dice=bot.send_message(message.from_user.id, f'Ваша очередь бросать игральную кость! (Отправьте этот эмодзи - 🎲, либо нажмите на игральную кость выше)\n<b>Действующая ставка:</b> {true_numbers(coop_roll_bet)} 💸', parse_mode='html', reply_markup=dice_reply)
            bot.register_next_step_handler(send_dice, sending_dice_new)
        else:
            sql.execute(f"SELECT * FROM rollcoop WHERE fchatid = '{message.from_user.id}'")
            res=sql.fetchone()
            if res!=None:
                del_dice_reply = types.InlineKeyboardMarkup()
                del_dice_reply.add(types.InlineKeyboardButton('❌ Отказаться от ставки', callback_data=f'del_dice{str(message.from_user.id)}'))
                bot.send_message(message.chat.id, "⚠️ Вы уже принимаете участие в одной из игр, но пока что мы не нашли вам противника. Если хотите отказаться от ставки, нажмите на кнопку ниже", reply_markup=del_dice_reply)
                return
            bot.send_dice(message.from_user.id, emoji='🎲')
            send_dice=bot.send_message(message.from_user.id, f'Ваша очередь бросать игральную кость! (Отправьте этот эмодзи - 🎲, либо нажмите на игральную кость ниже)\n<b>Действующая ставка:</b> {true_numbers(coop_roll_bet)} 💸', parse_mode='html', reply_markup=dice_reply)
            bot.register_next_step_handler(send_dice, sending_dice_existed)
    elif message.text=='🎰 Играть в рулетку':
        adding_all()
        set_cash=bot.send_message(message.from_user.id, "На какую сумму хотите сыграть? Вы также можете сыграть на все ваши наличные, нажав на кнопку ниже", reply_markup=all_reply)
        bot.register_next_step_handler(set_cash, choosing_roll)
    elif message.text == '🗡 Жизнь или смерть':
        choosing_cash=bot.send_message(message.from_user.id, "На какую сумму хотите сыграть? Вы также можете сыграть на все ваши наличные, нажав на кнопку ниже", reply_markup=all_reply)
        bot.register_next_step_handler(choosing_cash, lord_amount)
    elif message.text=='🏦 Перевести игроку':
        transfer_choose_name=bot.send_message(message.from_user.id, "Укажите никнейм пользователя, которому хотите перевести деньги с вашего банковского счёта?", reply_markup=markup_reply)
        bot.register_next_step_handler(transfer_choose_name, transfer_choosing_name)
    elif message.text=='💰 Баланс':
        sql.execute(f"SELECT * FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        msg= f"💰 <b>Ваш баланс ({res[1]})</b> 💰\n\n👋 Наличные: {true_numbers(res[2])} 💸\n🏦 В банке: {true_numbers(res[3])} 💸\n⚖️ Всего: {true_numbers(res[4])} 💸"
        bot.send_message(message.from_user.id, msg, parse_mode='html', reply_markup=markup_reply)
    elif message.text=='💼 Работать':
        sql.execute(f"SELECT job_blocked FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        if res[0]!='blocked':
            fee = random.randint(100,500)
            sql.execute(f"UPDATE players SET inbank = inbank + {fee}, total = total + {fee} WHERE chatid = '{message.from_user.id}'")
            db.commit()
            sql.execute(f"UPDATE players SET job_blocked = 'blocked' WHERE chatid = '{message.from_user.id}'")
            db.commit()
            bot.send_message(message.from_user.id, f'Спасибо, что заменили нашего дилера в этот раз. <b>{fee}</b> 💸 были переведены на ваш банковский счёт! Данная работа временно вам не доступна. Ожидайте 5 минут.', parse_mode='html', reply_markup=markup_reply)
            print(f"{message.from_user.username} заработал {fee}")
            import check_work_db
            user_id=str(message.from_user.id)
            check_work_db.t = threading.Timer(300.0, check_work_db.block_work, args=(user_id,))
            check_work_db.t.start()
        else:
            bot.send_message(message.from_user.id, 'К сожалению, ещё длится перерыв. Подождите, пожалуйста!', reply_markup=markup_reply)
    elif message.text=='💵 Положить на банковский счёт':
        user_cash=bot.send_message(message.from_user.id, "Какую сумму хотите положить на банковский счёт? Вы также можете выбрать все наличные, нажав на кнопку ниже", reply_markup=all_reply)
        bot.register_next_step_handler(user_cash, to_bank)
    elif message.text=='🏦 Снять с банковского счёта':
        user_inbank=bot.send_message(message.from_user.id, "Какую сумму хотите снять? Вы также можете выбрать все деньги на банковском счету, нажав на кнопку ниже", reply_markup=all_reply)
        bot.register_next_step_handler(user_inbank, from_bank)
    elif message.text=='🏆 Список лидеров':
        counter = 0
        sql.execute(f"SELECT username FROM players")
        rows = sql.fetchall()
        msg = f'🏆 <b>Список самых богатых игроков</b> 🏆\n(Всего игроков: <b>{len(rows)}</b>)\n\n'
        no_repeat=False
        sql.execute("SELECT username, total, chatid FROM players ORDER BY total DESC LIMIT 10")
        rows = sql.fetchall()
        for row in rows:
            if row[2]==str(message.from_user.id):
                no_repeat=True
                counter += 1
                msg = f"{msg}<b><u>#{counter}</u> | {row[0]} (Вы)</b> - {true_numbers(row[1])} 💸\n"
            else:
                counter += 1
                msg = f"{msg}<b><u>#{counter}</u> | {row[0]}</b> - {true_numbers(row[1])} 💸\n"
        if no_repeat!=True:
            counter = 0
            sql.execute(f"SELECT username, total, chatid FROM players ORDER BY total")
            rows = sql.fetchall()
            for row in rows:
                counter += 1
                if row[2]==str(message.from_user.id):
                    continue
            msg=f"{msg}\nВы занимаете <b>{counter}-ое</b> место, но ваше место в таблице лидеров не за горами!"
        bot.send_message(message.from_user.id, msg, parse_mode='html', reply_markup=markup_reply)
    elif message.text=='📩 Реферальная программа':
        sql.execute(f"SELECT * FROM referals WHERE tochatid = '{message.from_user.id}' ORDER BY reftotal")
        rows=sql.fetchall()
        if rows==[]:
            return bot.reply_to(message, f'⚠️ Вы не принимали участие в реферальной программе. Для этого нужно, чтобы хотя бы один из новых пользователей указал ваш никнейм при регистрации', reply_markup=markup_reply)
        msg = f'📩 <b>Ваш заработок</b> 📩\n\n'
        counter = 0
        reftotal=0
        for row in rows:
            counter += 1
            reftotal=reftotal+row[4]
            msg = f"{msg}<b><u>#{counter}</u> | {row[1]}</b> - {true_numbers(row[4])} 💸\n"        
        msg=f"{msg}\n<b>Всего:</b> {true_numbers(reftotal)} 💸"
        bot.send_message(message.from_user.id, msg, parse_mode='html', reply_markup=markup_reply)
    elif message.text==f'👤 Изменить никнейм (Цена: {str(change_username_price)} 💸)':
        sql.execute(f"SELECT username FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        if res!=None:
            cancel_change_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_change_reply.add(types.KeyboardButton('❌ Отказаться от смены никнейма'))
            change_username=bot.send_message(message.from_user.id, f'Напишите ваш новый никнейм для игры. <b>Цена услуги:</b> {change_username_price} 💸. Если хотите отказаться, нажмите на кнопку ниже', parse_mode='html', reply_markup=cancel_change_reply)
            bot.register_next_step_handler(change_username, changing_username)
        else:
            return bot.reply_to(message, f'⚠️ Вы не являетесь игроком. Для начала игры используйте /start', reply_markup=markup_reply)
    elif message.text=='/rollhelp':
        roll_link='https://telegra.ph/FAQ---Ruletka-04-01'
        roll_link_reply = types.InlineKeyboardMarkup()
        roll_link_reply.add(types.InlineKeyboardButton('🌐 FAQ - Рулетка', url=roll_link))
        bot.send_message(message.from_user.id, text='Если Вы хотите играть не только ради удовольствия, но постоянно выигрывать в рулетку, Вам необходимы базовые знания о типах ставок и выплатах в этой игре. Помните, чем точнее будет Ваш выбор, тем большей окажется Ваша выплата в случае выигрыша', reply_markup=roll_link_reply)
    elif message.text=='/lordhelp':
        life_or_death_link='https://telegra.ph/FAQ---ZHizn-ili-smert-04-04'
        life_or_death_link_reply = types.InlineKeyboardMarkup()
        life_or_death_link_reply.add(types.InlineKeyboardButton('🌐 FAQ - Жизнь или смерть', url=life_or_death_link))
        bot.send_message(message.from_user.id, text='"Жизнь или смерть" - одна из опаснейших игр академии Хяккао. Рекомендуем вам ознакомиться с правилами, чтобы не потерять все свои сбережения', reply_markup=life_or_death_link_reply)
    elif message.text=='/reset':
        sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        if res!=None:
            bot.send_message(message.from_user.id, '✅ Клавиатура восстановлена', reply_markup=markup_reply)
    time.sleep(0.5)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data=='no_del_acc':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Хорошо! Оставим это на потом")
            bot.send_sticker(call.message.chat.id, 'CAACAgUAAxkBAAECIwpgZwgM31EvZgFLqJQXHXWW6J8zHQACLwIAAjhkuguZVDReJ8Ig8R4E')
        elif 'del_dice' in call.data:
            user_id=call.data.replace('del_dice', '')
            adding_keyboard()
            sql.execute(f"DELETE FROM rollcoop WHERE fchatid = '{user_id}'")
            db.commit()
            bot.edit_message_text('✅ Поиск игроков отменён', call.message.chat.id, call.message.message_id, reply_markup=None)
        elif 'delete_acc' in call.data:
            username=call.data.replace('delete_acc', '')
            bot.delete_message(call.message.chat.id, call.message.message_id)
            sql.execute(f"DELETE FROM players WHERE username = '{username}'")
            db.commit()
            sql.execute(f"DELETE FROM referals WHERE refusername = '{username}'")
            db.commit()
            sql.execute(f"DELETE FROM referals WHERE tousername = '{username}'")
            db.commit()
            bot.send_message(call.message.chat.id, "Аккаунт пользователя был успешно удалён")
            print(f"Аккаунт пользователя {username} был удалён")
        elif 'clear_acc' in call.data:
            username=call.data.replace('clear_acc', '')
            bot.delete_message(call.message.chat.id, call.message.message_id)
            sql.execute(f"UPDATE players SET cash = {0}, inbank = {0}, total = {0} WHERE username = '{username}'")
            db.commit()
            bot.send_message(call.message.chat.id, "Баланс аккаунта пользователя был успешно обнулён")
            print(f"Баланс аккаунта пользователя {username} был успешно обнулён")
        


def sending_dice_new(message):
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res[0]>=coop_roll_bet and coop_roll_bet>=1:
        pass
    elif res[0]==0:
        return bot.reply_to(message, f'Недостаточно наличных для игры', reply_markup=markup_reply)
    else:
        msg=f'Ваших наличных недостаточно для ставки на сумму <b>{true_numbers(coop_roll_bet)}</b> 💸. Снимите с банковского счёта ещё <b>{true_numbers(coop_roll_bet-res[0])}</b> 💸'
        return bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    adding_keyboard()
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    try:
        if message.dice.emoji!='🎲':
            return bot.reply_to(message, "⚠️ Вы не отправили игральную кость", reply_markup=markup_reply)
    except:
        return bot.reply_to(message, "⚠️ Вы не отправили игральную кость", reply_markup=markup_reply)
    sql.execute("INSERT INTO rollcoop VALUES (%s, %s, %s, %s, %s)", (message.from_user.id, 'None', message.dice.value, 0, coop_roll_bet))
    db.commit()
    wincash=coop_roll_bet
    bot.send_message(message.from_user.id, f"Угу...на верхней части кубика - <b>{message.dice.value}</b>. Довольно неплохо! Как только другой игрок бросит свой кубик, вы узнаете результат игры", parse_mode='html', reply_markup=markup_reply)

def sending_dice_existed(message):
    global coop_roll_bet
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res[0]>=coop_roll_bet and coop_roll_bet>=1:
        pass
    elif res[0]==0:
        return bot.reply_to(message, f'Недостаточно наличных для игры', reply_markup=markup_reply)
    else:
        msg=f'Ваших наличных недостаточно для ставки на сумму <b>{true_numbers(coop_roll_bet)}</b> 💸. Снимите с банковского счёта ещё <b>{true_numbers(coop_roll_bet-res[0])}</b> 💸'
        return bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    adding_keyboard()
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    try:
        if message.dice.emoji!='🎲':
            return bot.reply_to(message, "⚠️ Вы не отправили игральную кость", reply_markup=markup_reply)
    except:
        return bot.reply_to(message, "⚠️ Вы не отправили игральную кость", reply_markup=markup_reply)
    
    sql.execute(f"UPDATE rollcoop SET schatid = {message.from_user.id}, sscore = {message.dice.value} WHERE wincash = {coop_roll_bet}")
    db.commit()
    sql.execute(f"SELECT * FROM rollcoop WHERE schatid = '{message.from_user.id}'")
    res=sql.fetchone()

    sql.execute(f"SELECT username FROM players WHERE chatid = '{res[0]}'")
    fusername=sql.fetchone()
    sql.execute(f"SELECT username FROM players WHERE chatid = '{res[1]}'")
    susername=sql.fetchone()
    wincash=res[4]
    if res[2]>res[3]:
        winner_id=res[0]
        loser_id=res[1]
        winner_score=res[2]
        loser_score=res[3]
        winnner_username=fusername[0]
        loser_username=susername[0]

        winner_msg=f'Игрок <b>{loser_username}</b> присоединился к вашей игровой комнате\n'
        loser_msg=f'Вы вошли в игровую комнату, созданную игроком <b>{winnner_username}</b>\n'
    elif res[2]==res[3]:
        msg = f'Игрок <b>{susername[0]}</b> присоединился к вашей игровой комнате. На верхней части его кубика выпало такое же число, как и у вас. Объявляется ничья, а ваши <b>{true_numbers(wincash)}</b> 💸 вернутся к вам на счёт'
        bot.send_message(res[0], msg, parse_mode='html', reply_markup=markup_reply)
        
        msg=f'Вы вошли в игровую комнату, созданную игроком <b>{fusername[0]}</b>. На верхней части его кубика выпало такое же число, как и у вас. Объявляется ничья, а ваши <b>{true_numbers(wincash)}</b> 💸 вернутся к вам на счёт'
        bot.send_message(res[1], msg, parse_mode='html', reply_markup=markup_reply)
        
        sql.execute(f"DELETE FROM rollcoop WHERE schatid = '{message.from_user.id}'")
        db.commit()
        return
    else:
        winner_id=res[1]
        loser_id=res[0]
        winner_score=res[3]
        loser_score=res[2]
        loser_username=fusername[0]
        winnner_username=susername[0]

        loser_msg=f'Игрок <b>{winnner_username}</b> присоединился к вашей игровой комнате\n'
        winner_msg=f'Вы вошли в игровую комнату, созданную игроком <b>{loser_username}</b>\n'
    
    difference=res[2]-res[3]
    if difference<0:
        difference=-difference
    sql.execute(f"UPDATE players SET cash = cash + {wincash}, total = total + {wincash} WHERE chatid = '{winner_id}'")
    db.commit()
    sql.execute(f"UPDATE players SET cash = cash - {wincash}, total = total - {wincash} WHERE chatid = '{loser_id}'")
    db.commit()
    ref_profit(message, wincash, loser_id)

    coop_roll_bet=random.choice([500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
    adding_keyboard()

    winner_msg = f'{winner_msg}\n<b>Очков на вашем кубике:</b> {winner_score}\n<b>Очков на кубике {loser_username}:</b> {loser_score}\n<b>Разница:</b> {difference}\n\nПобеда за вами!\n<b>Сумма выигрыша:</b> {true_numbers(wincash)} 💸'
    bot.send_message(winner_id, winner_msg, parse_mode='html', reply_markup=markup_reply)
    loser_msg= f'{loser_msg}\n<b>Очков на вашем кубике:</b> {loser_score}\n<b>Очков на кубике {winnner_username}:</b> {winner_score}\n<b>Разница:</b> {difference}\n\nК сожалению, вы проиграли\n<b>Сумма проигрыша:</b> {true_numbers(wincash)} 💸'
    bot.send_message(loser_id, loser_msg, parse_mode='html', reply_markup=markup_reply)
    print(f'{winnner_username} выиграл у {loser_username} в "Кости" (Сумма выигрыша: {true_numbers(wincash)})')
    sql.execute(f"DELETE FROM rollcoop WHERE schatid = '{message.from_user.id}'")
    db.commit()




def lord_amount(message):
    adding_keyboard()
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    try:
        amount=int(message.text)
    except:
        amount=message.text
        if amount!='Все 💸':
            return
        else:
            amount=res[0]
    if res[0]>=amount and amount>=1 and res[0]>=amount*30:
        set_number=bot.send_message(message.from_user.id, "Какой номер ячейки (от 1 до 30) вы выберете?")
        bot.register_next_step_handler(set_number, lord_results, amount)
    elif amount<=0 and amount!=res[0]:
        bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с <b>{amount}</b> 💸', reply_markup=markup_reply)
    elif res[0]==0:
        bot.reply_to(message, f'Недостаточно наличных для игры', reply_markup=markup_reply)
    else:
        msg=f'Ваших наличных недостаточно для ставки на сумму <b>{true_numbers(amount)}</b> 💸. Снимите с банковского счёта ещё <b>{true_numbers((amount*30)-res[0])}</b> 💸, чтобы выполнить ставку'
        bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    


def lord_results(message, amount):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    try:
        user_number=int(message.text)
        if user_number<1 or user_number>30:
            return bot.reply_to(message, f'⚠️ Можно выбрать число только от 1 до 30', reply_markup=markup_reply)
    except:
        return bot.reply_to(message, f'⚠️ Можно выбрать только числовое значение от 1 до 30', reply_markup=markup_reply)
    numbers={}
    for row in range(10):
        drop_or_not=bool(random.getrandbits(1))
        if drop_or_not==True:
            number=random.randint(1,30)
            up_or_down=random.choice(["вверх", "вниз"])
            if number not in numbers:
                numbers.update({number:up_or_down})
    if user_number in numbers:
        main_amount=amount*30
        if numbers.get(user_number)=="вниз":
            sql.execute(f"UPDATE players SET cash = cash - {main_amount}, total = total - {main_amount} WHERE chatid = '{message.from_user.id}'")
            db.commit()
            ref_profit(message, main_amount)
            msg=f'Клинок вонзился в отверстие с выбранным вами номером лезвием вниз\nК сожалению, ваша ставка <b>{true_numbers(amount)}</b> 💸 на число <b>{user_number}</b> проигрывает\n<b>Сумма проигрыша:</b> {true_numbers(main_amount)} 💸'
        else:
            sql.execute(f"UPDATE players SET cash = cash + {main_amount}, total = total + {main_amount} WHERE chatid = '{message.from_user.id}'")
            db.commit()
            msg=f'Клинок вонзился в отверстие с выбранным вами номером лезвием вверх\nВаша ставка <b>{true_numbers(amount)}</b> 💸 на число <b>{user_number}</b> выигрывает!\n<b>Сумма выигрыша:</b> {true_numbers(main_amount)} 💸'
    else:
        msg=f'Ни один клинок не вонзился в отверстие с выбранным вами номером\nВаши <b>{true_numbers(amount)}</b> 💸 вернутся к вам на счёт'   
    bot.send_message(message.from_user.id, msg, parse_mode='html', reply_markup=markup_reply)


def choosing_roll(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    try:
        sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        try:
            amount=int(message.text)
        except:
            amount=message.text
            if amount!='Все 💸':
                return bot.reply_to(message, f'⚠️ Вы неправильно указали сумму ставки', reply_markup=markup_reply)
            else:
                amount=res[0]
        if res[0]>=amount and amount>=1:
            roll_reply=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            roll_reply.add(types.KeyboardButton('🔴 RED'), types.KeyboardButton('⚫️ BLACK'))
            roll_reply.add(types.KeyboardButton('EVEN'), types.KeyboardButton('ODD'))
            roll_reply.add(types.KeyboardButton('⬆️ 2 to 1 (верхний столбец)'))
            roll_reply.add(types.KeyboardButton('2 to 1 (средний столбец)'))
            roll_reply.add(types.KeyboardButton('⬇️ 2 to 1 (нижний столбец)'))
            roll_reply.add(types.KeyboardButton('1st 12'), types.KeyboardButton('2nd 12'), types.KeyboardButton('3rd 12'))
            roll_reply.add(types.KeyboardButton('1 to 18'), types.KeyboardButton('19 to 36'))
            roll_reply.add(types.KeyboardButton('❌ Отменить действие'))
            set_bet = bot.send_message(message.from_user.id, f"На что будете ставить? Для выбора используйте меню ниже либо укажите число.\nЧтобы ознакомиться с правилами игры, используйте /rollhelp", reply_markup=roll_reply) 
            bot.register_next_step_handler(set_bet, setting_bet, amount)
        elif amount<=0 and amount!=res[0]:
            bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с {amount} 💸', reply_markup=markup_reply)
        elif res[0]==0:
            bot.reply_to(message, f'Недостаточно наличных для игры', reply_markup=markup_reply)
        else:
            msg=f'Ваших наличных недостаточно для ставки на сумму <b>{true_numbers(amount)}</b> 💸. Снимите с банковского счёта ещё <b>{true_numbers(amount-res[0])}</b> 💸'
            bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    except:
        return


def setting_bet(message, amount):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    win_number = random.randint(0, 36)
    setting_bet=message.text
    red_list=[1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    if setting_bet=='🔴 RED':
        q=2
        amount=-amount
        for row in red_list:
            if win_number==row:
                amount=-amount
                break
    elif setting_bet=='⚫️ BLACK':
        q=2
        for row in red_list:
            amount=-amount
            if win_number==row:
                break
            else:
                amount=-amount
    elif setting_bet=='EVEN':
        q=2
        if win_number%2 != 0 and win_number!=0:
            amount=-amount
    elif setting_bet=='ODD':
        q=2
        if win_number%2 == 0 and win_number!=0:
            amount=-amount
    elif setting_bet=='⬆️ 2 to 1 (верхний столбец)':
        q=2
        column=[]
        for i in range(3,39,3):
            column.append(i)
        amount=-amount
        for row in column:
            if win_number==row:
                amount=-amount
                break
    elif setting_bet=='2 to 1 (средний столбец)':
        q=2
        column=[]
        for i in range(2,38,3):
            column.append(i)
        amount=-amount
        for row in column:
            if win_number==row:
                amount=-amount
                break
    elif setting_bet=='⬇️ 2 to 1 (нижний столбец)':
        q=2
        column=[]
        for i in range(1,37,3):
            column.append(i)
        amount=-amount
        for row in column:
            if win_number==row:
                amount=-amount
                break
    elif setting_bet=='1st 12':
        q=3
        amount=-amount
        if win_number>=1 and win_number<=12:
            amount=-amount
    elif setting_bet=='2nd 12':
        q=3
        amount=-amount
        if win_number>=13 and win_number<=24:
            amount=-amount
    elif setting_bet=='3rd 12':
        q=3
        amount=-amount
        if win_number>=25 and win_number<=36:
            amount=-amount
    elif setting_bet=='1 to 18':
        q=2
        amount=-amount
        if win_number>=1 and win_number<=18:
            amount=-amount
    elif setting_bet=='19 to 36':
        q=2
        amount=-amount
        if win_number>=19 and win_number<=36:
            amount=-amount
    else:
        q = 35
        try:
            setting_bet=int(setting_bet)
        except:
            return bot.reply_to(message, f'⚠️ Вы неправильно указали ставку. В следующий раз воспользуйтесь меню или числами от 0 до 36', reply_markup=markup_reply)
        if setting_bet>=0 and setting_bet<=36:
            if setting_bet!=win_number:
                amount=-amount
        else:
            return bot.reply_to(message, f'⚠️ В данной игре можно сделать ставку на числа от 0 до 36', reply_markup=markup_reply)
    if amount>0: 
        sql.execute(f"UPDATE players SET cash = cash + {amount*q}, total = total + {amount*q} WHERE chatid = '{message.from_user.id}'")
        db.commit()
        bot.send_message(message.from_user.id, f"Шарик в рулетке остановился на номере <b>{win_number}</b>\nВаша ставка на <b>{setting_bet}</b> выиграла!\nКоэффициент выигрыша - <b>{q}:1</b>\n<b>Сумма выигрыша:</b> {true_numbers(amount*q)} 💸", parse_mode='html', reply_markup=markup_reply)
        print(f'{message.from_user.username} выиграл {true_numbers(amount*q)} в рулетке (выпало число: {win_number}, ставка: {true_numbers(setting_bet)}, коэффициент выигрыша: {q}:1)')
    else:
        amount=-amount
        sql.execute(f"UPDATE players SET cash = cash - {amount}, total = total - {amount} WHERE chatid = '{message.from_user.id}'")
        db.commit()
        bot.send_message(message.from_user.id, f"Шарик в рулетке остановился на номере <b>{win_number}</b>\nК сожалению, Ваша ставка на <b>{setting_bet}</b> проиграла\n<b>Сумма проигрыша:</b> {true_numbers(amount)} 💸", parse_mode='html', reply_markup=markup_reply)
        ref_profit(message, amount)
        print(f'{message.from_user.username} проиграл {true_numbers(amount)} в рулетке (выпало число: {win_number}, ставка: {true_numbers(setting_bet)}, коэффициент выигрыша: {q}:1)')
    time.sleep(0.5)


def changing_username(message):
    adding_keyboard()
    sql.execute(f"SELECT username FROM players WHERE username = '{message.text}'")
    if sql.fetchone() is None and len(message.text)>=1 and len(message.text)<=15 and message.text!='❌ Отказаться от смены никнейма':
        username=message.text
    elif message.text=='❌ Отказаться от смены никнейма':
        bot.reply_to(message, f"Хорошо. Как только будете готовы изменить никнейм, используйте меню 😉", reply_markup=markup_reply)
        return
    elif len(message.text)>15:
        bot.reply_to(message, f"Ваш никнейм состоит из более 15 символов. Используйте другой и начните заново, используя меню", reply_markup=markup_reply)
        return
    else:
        bot.reply_to(message, f"Ваш никнейм состоит из более 15 символов. Используйте другой и начните заново, используя меню", reply_markup=markup_reply)
        return
    sql.execute(f"SELECT username, cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res[1]>=change_username_price:
        sql.execute(f"UPDATE players SET cash = cash - {change_username_price}, total = total - {change_username_price}, username = '{username}' WHERE chatid = '{message.from_user.id}'")
        db.commit()
        bot.send_message(message.from_user.id, f'Поздравляю! Ваш никнейм был успешно изменён на <b>{username}</b>', parse_mode='html',reply_markup=markup_reply)
    else:
        return bot.reply_to(message, f'Ваших наличных недостаточно для изменения никнейма', reply_markup=markup_reply)


def transfer_choosing_name(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    username=message.text
    sql.execute(f"SELECT inbank FROM players WHERE username = '{username}'")
    res = sql.fetchone()
    if res is None:
        return bot.send_message(message.from_user.id, f"Пользователь <b>{username}</b> не найден", parse_mode='html', reply_markup=markup_reply)
    cancel_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_reply.add(types.KeyboardButton('Все 💸'))
    cancel_reply.add(types.KeyboardButton('❌ Отменить действие'))
    make_caption=bot.send_message(message.from_user.id, 'Какую сумму вы хотите перевести?', reply_markup=cancel_reply)
    bot.register_next_step_handler(make_caption, making_caption, username)

def making_caption(message, to_user):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    adding_nocaption()
    try:
        sending_amount=int(message.text)
        if sending_amount<1:
            return bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с {amount} 💸', reply_markup=markup_reply)
    except:
        return
    transfer=bot.send_message(message.from_user.id, 'Комментарий к отправке (до 120 символов)?', reply_markup=nocaption_reply)
    bot.register_next_step_handler(transfer, transfering, to_user, sending_amount)

def transfering(message, to_user, sending_amount):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    caption = message.text
    sql.execute(f"SELECT inbank, username FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    if res[0]>=sending_amount:
        sql.execute(f"UPDATE players SET inbank = inbank + {sending_amount}, total = total + {sending_amount} WHERE username = '{to_user}'")
        db.commit()
        sql.execute(f"UPDATE players SET inbank = inbank - {sending_amount}, total = total - {sending_amount} WHERE chatid = '{message.from_user.id}'")
        db.commit()
        mes_recipient= f'<b>Уважаемый(ая) {to_user}</b>! Пользователь {res[1]} перевёл {sending_amount} 💸 вам на банковский счёт.'
        if caption!='❌ Не добавлять комментарий' and len(caption)<=120:
            mes_recipient = f'{mes_recipient}\n<b>Комментарий:</b> {caption}'
        elif caption!='❌ Не добавлять комментарий' and len(caption)>120:
            bot.reply_to(message, f'⚠️ Комментарий может содержать не больше 120. У вас - <b>{len(caption)}</b>', parse_mode='html', reply_markup=markup_reply)
            return
        bot.send_message(message.from_user.id, f'Вы перевели <b>{true_numbers(sending_amount)}</b> 💸 с вашего банковского счёта на счёт пользователя <b>{to_user}</b>!', parse_mode='html', reply_markup=markup_reply)
        sql.execute(f"SELECT chatid FROM players WHERE username = '{to_user}'")
        to_chatid = sql.fetchone()
        bot.send_message(to_chatid[0], mes_recipient, parse_mode='html', reply_markup=markup_reply)
        print(f'{message.from_user.username} перевёл {true_numbers(sending_amount)} со своего банковского счёта на счёт пользователя {to_user}')
    else:
        msg=f'Недостаточно денег на банковском счету для перевода <b>{true_numbers(sending_amount)}</b> 💸. Пополните счёт на <b>{true_numbers(sending_amount-res[0])}</b> 💸 для совершения данной операции'
        bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    
    
#Проверка на ставку
def roll_win(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    try:
        sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
        res=sql.fetchone()
        try:
            amount=int(message.text)
        except:
            amount=message.text
            if amount!='Все 💸':
                return
            else:
                amount=res[0]
        if res[0]>=amount and amount>=1:
            bot_dice = bot.send_dice(message.from_user.id, emoji='🎲')
            bot.send_message(message.from_user.id, 'Ваша очередь бросать игральную кость! (Отправьте этот эмодзи - 🎲, либо нажмите на кость выше)')
            bot.register_next_step_handler(bot_dice, user_dice, bot_dice.dice.value, amount, message.from_user.id)
        elif amount<=0 and amount!=res[0]:
            bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с <b>{amount}</b> 💸', parse_mode='html', reply_markup=markup_reply)
        elif res[0]==0:
            bot.reply_to(message, f'Недостаточно наличных для игры', reply_markup=markup_reply)
        else:
            msg=f'Ваших наличных недостаточно для ставки на сумму <b>{true_numbers(amount)}</b> 💸. Снимите с банковского счёта ещё <b>{true_numbers(amount-res[0])}</b> 💸'
            bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    except:
        return
    time.sleep(0.5)
#Проверка на выигрыш в кости
def user_dice(message, bot_dice_value, amount, userid):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    try:
        if message.dice.emoji=='🎲' and userid == message.from_user.id:
            if bot_dice_value>message.dice.value:
                bot.send_message(message.from_user.id, f'К сожалению, вы проиграли. \n<b>Сумма проигрыша:</b> {true_numbers(amount)} 💸', parse_mode='html', reply_markup=markup_reply)
                sql.execute(f"UPDATE players SET cash = cash - {amount}, total = total - {amount} WHERE chatid = '{message.from_user.id}'")
                db.commit()
                ref_profit(message, amount)
                print(f'{message.from_user.username} проиграл {true_numbers(amount)} в игре "Кости"')
            elif bot_dice_value==message.dice.value:
                bot.send_message(message.from_user.id, f'В этот раз - ничья. Ваши <b>{true_numbers(amount)}</b> 💸 вернутся к вам на счёт', parse_mode='html', reply_markup=markup_reply)
            else:
                sql.execute(f"UPDATE players SET cash = cash + {amount}, total = total + {amount} WHERE chatid = '{message.from_user.id}'")
                db.commit()
                bot.send_message(message.from_user.id, f'Поздравляю! Вы выиграли <b>{true_numbers(amount)}</b> 💸', parse_mode='html', reply_markup=markup_reply)
                print(f'{message.from_user.username} выиграл {true_numbers(amount)} в игре "Кости"')
        time.sleep(1)
    except:
        return


#Перевод на банковский счёт
def to_bank(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    try:
        amount=int(message.text)
    except:
        amount=message.text
        if amount!='Все 💸':
            return
        else:
            amount=res[0]
    if res[0]>=amount and amount>=1:
        sql.execute(f"UPDATE players SET inbank = inbank + {amount}, cash = cash - {amount}, total = inbank + cash WHERE chatid = '{message.from_user.id}'")
        db.commit()
        bot.send_message(message.from_user.id, f'<b>{true_numbers(amount)}</b> 💸 были отправлены на ваш банковский счёт!', parse_mode='html', reply_markup=markup_reply)
        print(f'{message.from_user.username} положил {true_numbers(amount)} на банковский счёт')
    elif amount<=0 and amount!=res[0]:
        bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с <b>{amount}</b> 💸', parse_mode='html', reply_markup=markup_reply)
    elif res[0]==0:
        bot.reply_to(message, f'Недостаточно наличных для перевода', reply_markup=markup_reply)
    else:
        msg=f'Ваших наличных недостаточно для перевода на сумму <b>{true_numbers(amount)}</b> 💸. У вас на руках не хватает <b>{true_numbers(amount-res[0])}</b> 💸 для совершения данной операции'
        bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    time.sleep(0.5)

#Снятие наличных
def from_bank(message):
    if message.text=='❌ Отменить действие':
        return bot.reply_to(message, "✅ Действие отменено", reply_markup=markup_reply)
    adding_keyboard()
    sql.execute(f"SELECT inbank FROM players WHERE chatid = '{message.from_user.id}'")
    res=sql.fetchone()
    try:
        amount=int(message.text)
    except:
        amount=message.text
        if amount!='Все 💸':
            return
        else:
            amount=res[0]
    if res[0]>=amount and amount>=1:
        sql.execute(f"UPDATE players SET cash = cash + {amount}, inbank = inbank - {amount}, total = cash + inbank WHERE chatid = '{message.from_user.id}'")
        db.commit()
        bot.send_message(message.from_user.id, f'Вы сняли <b>{true_numbers(amount)}</b> 💸 с вашего банковского счёта!', parse_mode='html',  reply_markup=markup_reply)
        print(f'{message.from_user.username} списал {true_numbers(amount)} с банковского счёта')
    elif amount<=0 and amount!=res[0]:
        bot.reply_to(message, f'⚠️ Нельзя совершить эту операцию с <b>{amount}</b> 💸', parse_mode='html', reply_markup=markup_reply)
    elif res[0]==0:
        bot.reply_to(message, f'Недостаточно денег на банковском счету для снятия', reply_markup=markup_reply)
    else:
        msg=f'Недостаточно денег на банковском счету для снятия <b>{true_numbers(amount)}</b> 💸. На вашем счету должно быть ещё <b>{true_numbers(amount-res[0])}</b> 💸 для совершения данной операции'
        bot.reply_to(message, msg, parse_mode='html', reply_markup=markup_reply)
    time.sleep(0.5)

#Проверка на реферальную систему
def checking_ref(message, username):
    adding_keyboard()
    ref_amount=0
    sql.execute(f"SELECT chatid FROM players WHERE username = '{message.text}'")
    row=sql.fetchone()
    if row is None and message.text!='❌ Отказаться от реферальной программы':
        return bot.send_message(message.from_user.id, f'Пользователь с ником <b>{message.text}</b> не найден. Вы можете попробовать ещё раз, используя /start', parse_mode='html')
    elif message.text!='❌ Отказаться от реферальной программы':
        ref_amount=500
        ref_username=message.text
    start_cash=150
    start_bank=0
    mes=f'<b>Добро пожаловать в игровой мир, {username}!</b> Вы - ученик частной академии Хяккао – места, где учится так называемая элита. Успехи в учебе, спортивные достижения… здесь это никого не интересует. Насколько ты хорош в азартных играх – вот признак успешности. Выигрывай, и учеба покажется тебе раем\n\n<b>Сейчас у вас на руках:</b> {start_cash} 💸'
    if ref_amount!=0:
        start_bank=start_bank+ref_amount
        mes=f'{mes}\n<b>На банковском счету:</b> {start_bank} 💸 (за участие в реферальной программе)'
        sql.execute(f"UPDATE players SET inbank = inbank + {ref_amount}, total = total + {ref_amount} WHERE username = '{ref_username}'")
        db.commit()
        try:
            bot.send_message(row[0], f'Новый пользователь <b>{username}</b> указал ваш никнейм при регистрации. Бонус от академии в размере {ref_amount} 💸 был перечислен на ваш банковский счёт. Вы также будете получать {ref_percents}% с каждого проигрыша этого пользователя', parse_mode='html', reply_markup=markup_reply)
        except:
            pass
    total=start_cash+start_bank
    sql.execute("INSERT INTO players VALUES (%s, %s, %s, %s, %s, %s)", (message.from_user.id, username, start_cash, start_bank, total, 'unblocked'))
    db.commit()
    if row!=None:
        sql.execute("INSERT INTO referals VALUES (%s, %s, %s, %s, %s)", (message.from_user.id, username, row[0], ref_username, ref_amount))
        db.commit()
    mes=mes+'\nВнизу появилось ваше меню для игры. Используя меню, вы можете работать, играть, проводить банковские операции и не только.\n\nСтаньте <u>самым богатым</u> среди остальных игроков! (Следите за списком лидеров)'
    bot.send_message(message.from_user.id, mes, reply_markup=markup_reply, parse_mode='html')
    bot.send_sticker(message.from_user.id, 'CAACAgIAAxkBAAEBD05gX7Z7x5kCc1iqEBF0HeFaRzXH3gACAwEAAladvQoC5dF4h-X6Tx4E')
    if row!=None:
        print(f'Новый пользователь Casinogg Bot - {username}. Воспользовался реферальной программой пользователя {ref_username}')
    else:
        print(f'Новый пользователь Casinogg Bot - {username}')
    

#Создание аккаунта
def creating_account(message):
    sql.execute(f"SELECT username FROM players WHERE username = '{message.text}'")
    if sql.fetchone() is None and len(message.text)>=1 and len(message.text)<=15:
        username=message.text
    elif len(message.text)>15:
        bot.reply_to(message, f"⚠️ Ваш никнейм состоит из более 15 символов. Используйте другой и начните заново - /start")
        return
    elif message.text=='❌ Отказаться от реферальной программы':
        bot.reply_to(message, f"⚠️ Нельзя использовать данный никнейм. Используйте другой и начните заново - /start")
        return
    else:
        bot.reply_to(message, f"⚠️ Этот никнейм занят. Используйте другой и начните заново, используя команду /start")
        return
    no_ref_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
    no_ref_reply.add(types.KeyboardButton('❌ Отказаться от реферальной программы'))
    check_ref=bot.send_message(message.from_user.id, f'Если кто-то из ваших друзей уже является игроком, вы можете указать никнейм этого пользователя в качестве реферальной программы. Таким образом и Вы, и пользователь, никнейм которого вы укажите, получите вознаграждение в виде дополнительной игровой валюты.\nХотите воспользоваться данной возможностью? (Если нет, вопользуйтесь появившимся меню)', reply_markup=no_ref_reply)
    bot.register_next_step_handler(check_ref, checking_ref, username)
#Добавляем клавиатуру
def adding_keyboard():
    global markup_reply
    global change_username_price
    global ref_percents
    change_username_price=10000
    ref_percents=5
    markup_reply=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup_reply.add(types.KeyboardButton('🎲 Играть в кости'), types.KeyboardButton(f'🎲 Кости 1 на 1 (Ставка: {true_numbers(coop_roll_bet)} 💸)'))
    markup_reply.add(types.KeyboardButton('🎰 Играть в рулетку'))
    markup_reply.add(types.KeyboardButton('🗡 Жизнь или смерть'))
    markup_reply.add(types.KeyboardButton('💼 Работать'))
    markup_reply.add(types.KeyboardButton('💵 Положить на банковский счёт'), types.KeyboardButton('🏦 Снять с банковского счёта'), types.KeyboardButton('🏦 Перевести игроку'))
    markup_reply.add(types.KeyboardButton('💰 Баланс'))
    markup_reply.add(types.KeyboardButton('🏆 Список лидеров'))
    markup_reply.add(types.KeyboardButton('📩 Реферальная программа'))
    markup_reply.add(types.KeyboardButton(f'👤 Изменить никнейм (Цена: {true_numbers(change_username_price)} 💸)'))

#Добавляем клавиатуру для отмены комментария перевода
def adding_nocaption():
    global nocaption_reply
    nocaption_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
    nocaption_reply.add(types.KeyboardButton('❌ Не добавлять комментарий'))
    nocaption_reply.add(types.KeyboardButton('❌ Отменить действие'))
    

#Добавляем клавиатуру для выбора всех денег
def adding_all():
    global all_reply
    all_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
    all_reply.add(types.KeyboardButton('Все 💸'))
    all_reply.add(types.KeyboardButton('❌ Отменить действие'))

def ref_profit(message, amount, user_id=None):
    if user_id!=None:
        sql.execute(f"SELECT * FROM referals WHERE refchatid = '{user_id}'")
    else:
        sql.execute(f"SELECT * FROM referals WHERE refchatid = '{message.from_user.id}'")
    row=sql.fetchone()
    if row!=None:
        profit = int(round((amount*ref_percents)/100))
        sql.execute(f"UPDATE referals SET reftotal = reftotal + {profit} WHERE tochatid = '{row[2]}'")
        db.commit()
        sql.execute(f"UPDATE players SET inbank = inbank + {profit}, total = total + {profit} WHERE chatid = '{row[2]}'")
        db.commit()


def true_numbers(amount):
    amount=str(amount)
    if len(amount)<=3:
        true_amount=amount
        return true_amount
    if len(amount)%3!=0:
        not_manipulated=int(len(amount)%3)
    else:
        not_manipulated=3
    true_amount=amount[:not_manipulated]
    for row in range(not_manipulated, len(amount),3):
        true_amount=true_amount+','+amount[row:row+3]
    return true_amount




bot.polling(none_stop=True)