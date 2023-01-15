# Tikhomirov Mikhail, 2023
# github.com/miguelf0x

import os
import telebot
import sqlite3
from telebot import types
from dotenv import load_dotenv

# Get API key from .env and create bot with it
load_dotenv()
bot = telebot.TeleBot(os.environ['TELEBOT_API_KEY'])

db = sqlite3.connect('tes.db', check_same_thread=False)
cur = db.cursor()

# Init
cur.execute("CREATE TABLE IF NOT EXISTS steps(uid integer, step integer, cpu_kvm intege, cpu_count integer, "
            "ram_size integer, drive_size integer, server_hdd integer, server_ssd integer, "
            "realtek_drivers integer)")


# Greet
@bot.message_handler(commands=['start'])
def start(message):
    btn1 = types.InlineKeyboardButton(text="Начать", callback_data='10')
    btn2 = types.InlineKeyboardButton(text="Отмена", callback_data='0')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Добрый день! Экспертная система для подбора конфигурации сервера ЛВС к вашим услугам. "
                          "Нажмите кнопку \'Начать\' для продолжения или кнопку \'Остановить\' для завершения "
                          "работы".format(
                           message.from_user),
                     reply_markup=markup)
    cur.execute("DELETE FROM steps WHERE uid = ?", (message.chat.id,))
    cur.execute("INSERT INTO steps (uid, step) VALUES(?, 1)", (message.chat.id,))
    db.commit()


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    steppy = int(call.data)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    match steppy:

        case 0:
            bot.send_message(call.message.chat.id,
                             text="Завершаю работу...".format(call.from_user),
                             reply_markup=None)
            cur.execute("DELETE FROM steps WHERE uid = ?", (call.message.chat.id,))

        case 10:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 10", (call.message.chat.id,))
            cur.execute("INSERT INTO steps (uid, step) VALUES(?, 10)", (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn3 = types.InlineKeyboardButton("Да", callback_data='20')
            btn4 = types.InlineKeyboardButton("Нет", callback_data='21')
            btn5 = types.InlineKeyboardButton("Что это?", callback_data='1000')

            markup.add(btn3, btn4, btn5)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 1. Будет ли использоваться гипервизор?".format(call.from_user),
                             reply_markup=markup)

        case 1000:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_ok = types.InlineKeyboardButton("Вернуться", callback_data='10')
            markup.add(btn_ok)
            bot.send_message(call.message.chat.id,
                             text="Гипервизор - программа, обеспечивающая одновременное, параллельное выполнение"
                                  " нескольких операционных систем на одном и том же хост-компьютере. Наиболее"
                                  " известными примерами являются VMware ESXi, Xen, Proxmox. Если Вы не планируете"
                                  " использовать гипервизор, то следует выбрать вариант ответа 'Нет'".format(
                                   call.from_user),
                             reply_markup=markup)

        case 20:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 20", (call.message.chat.id,))
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            cur.execute("INSERT INTO steps (uid, step, cpu_kvm) VALUES(?, 20, 1)", (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn6 = types.InlineKeyboardButton("VMWare ESXi", callback_data='310')
            btn7 = types.InlineKeyboardButton("Xen", callback_data='320')
            btn8 = types.InlineKeyboardButton("Proxmox VE", callback_data='330')
            btn9 = types.InlineKeyboardButton("Я не знаю", callback_data='2000')
            btn10 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn6, btn7, btn8, btn9, btn10)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 2. Какой гипервизор будет использоваться?".format(call.from_user),
                             reply_markup=markup)

        case 2000:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_ok = types.InlineKeyboardButton("Вернуться", callback_data='20')
            markup.add(btn_ok)
            bot.send_message(call.message.chat.id,
                             text="VMWare ESXi является платным ПО и не поддерживает сетевые карты Realtek в"
                                  " современных релизах. Xen распространяется бесплатно на условиях лицензии GPL."
                                  " Proxmox VE распространяется бесплатно, но имеет четыре варианта платных подписок,"
                                  " предоставляющих расширенную поддержку".format(
                                   call.from_user), reply_markup=markup)

        # NoVirt
        case 21:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 21", (call.message.chat.id,))
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, realtek_drivers) VALUES(?, 21,"
                " 0, 0, 0, 0, 1)",
                (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn11 = types.InlineKeyboardButton("Windows Server", callback_data='410')
            btn12 = types.InlineKeyboardButton("Linux", callback_data='420')
            btn13 = types.InlineKeyboardButton("Я не знаю", callback_data='3000')
            btn14 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn11, btn12, btn13, btn14)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 2. Какая операционная система будет использоваться на сервере?".format(
                                 call.from_user),
                             reply_markup=markup)

        # ESXi
        case 310:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 310", (call.message.chat.id,))
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, realtek_drivers) VALUES(?, 310"
                ", 1, 2, 4096, 32, 0)",
                (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn11 = types.InlineKeyboardButton("Windows Server", callback_data='410')
            btn12 = types.InlineKeyboardButton("Linux", callback_data='420')
            btn13 = types.InlineKeyboardButton("Я не знаю", callback_data='3000')
            btn14 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn11, btn12, btn13, btn14)
            bot.send_message(call.message.chat.id,
                             text="Обратите Ваше внимание на то, что начиная с 6 релиза ESX сетевые карты Realtek"
                                  " больше не поддерживаются. Я напомню Вам об этом при получении рекомендаций".format(
                                   call.from_user))
            bot.send_message(call.message.chat.id,
                             text="Вопрос 3. Какая операционная система будет использоваться на первой виртуальной"
                                  " машине?".format(
                                   call.from_user),
                             reply_markup=markup)

        # Xen
        case 320:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 320", (call.message.chat.id,))
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, realtek_drivers) VALUES(?,"
                " 320, 1, 2, 4096, 46, 1)",
                (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn11 = types.InlineKeyboardButton("Windows Server", callback_data='410')
            btn12 = types.InlineKeyboardButton("Linux", callback_data='420')
            btn13 = types.InlineKeyboardButton("Я не знаю", callback_data='3000')
            btn14 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn11, btn12, btn13, btn14)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 3. Какая операционная система будет использоваться на первой виртуальной"
                                  " машине?".format(
                                   call.from_user),
                             reply_markup=markup)

        # PVE
        case 330:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 330", (call.message.chat.id,))
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, realtek_drivers) VALUES(?,"
                " 330, 1, 2, 2048, 16, 1)",
                (call.message.chat.id,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn11 = types.InlineKeyboardButton("Windows Server", callback_data='410')
            btn12 = types.InlineKeyboardButton("Linux", callback_data='420')
            btn13 = types.InlineKeyboardButton("Я не знаю", callback_data='3000')
            btn14 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn11, btn12, btn13, btn14)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 3. Какая операционная система будет использоваться на первой виртуальной"
                                  " машине?".format(
                                   call.from_user),
                             reply_markup=markup)

        case 3000:
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_ok = types.InlineKeyboardButton("Вернуться", callback_data=str(max_step))
            markup.add(btn_ok)
            bot.send_message(call.message.chat.id,
                             text="В случае, если у Вас в локальной сети используются ПК на ОС Windows, то для создания"
                                  " цельной инфраструктуры предпочтительно выбрать Windows Server. Если у Вас имеются"
                                  " навыки администрирования ОС Linux или они используются в Вашей локальной сети,"
                                  " следует выбрать OC Linux".format(
                                   call.from_user),
                             reply_markup=markup)

        # Windows Server
        case 410:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 410", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[4] += 2048
            data[3] += 2
            data[5] += 48
            data[1] = 410
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn15 = types.InlineKeyboardButton("Да", callback_data='510')
            btn16 = types.InlineKeyboardButton("Нет", callback_data='520')
            btn17 = types.InlineKeyboardButton("Я не знаю", callback_data='4000')
            btn18 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn15, btn16, btn17, btn18)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 4. Будет ли сервер использоваться для хостинга БД?".format(
                                 call.from_user),
                             reply_markup=markup)

        # Linux
        case 420:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 420", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[4] += 2048
            data[3] += 2
            data[5] += 32
            data[1] = 420
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn15 = types.InlineKeyboardButton("Да", callback_data='510')
            btn16 = types.InlineKeyboardButton("Нет", callback_data='520')
            btn17 = types.InlineKeyboardButton("Я не знаю", callback_data='4000')
            btn18 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn15, btn16, btn17, btn18)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 4. Будет ли сервер использоваться для хостинга БД?".format(
                                 call.from_user),
                             reply_markup=markup)

        case 4000:
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_ok = types.InlineKeyboardButton("Вернуться", callback_data=str(max_step))
            markup.add(btn_ok)
            bot.send_message(call.message.chat.id,
                             text="Если вы не знаете, что такое БД, то выберите 'Нет'".format(call.from_user),
                             reply_markup=markup)

        # DB
        case 510:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 510", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[4] += 2048
            data[3] += 2
            data[5] += 32
            data[6] = 0
            data[7] = 1
            data[1] = 510
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn15 = types.InlineKeyboardButton("Да", callback_data='610')
            btn16 = types.InlineKeyboardButton("Нет", callback_data='620')
            btn17 = types.InlineKeyboardButton("Я не знаю", callback_data='5000')
            btn18 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn15, btn16, btn17, btn18)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 5. Будет ли сервер использоваться как веб-сервер?".format(
                                 call.from_user),
                             reply_markup=markup)

        # Not DB
        case 520:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 520", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps WHERE"
                               " uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[4] += 2048
            data[3] += 2
            data[5] += 32
            data[6] = 1
            data[7] = 0
            data[1] = 520
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn15 = types.InlineKeyboardButton("Да", callback_data='610')
            btn16 = types.InlineKeyboardButton("Нет", callback_data='620')
            btn17 = types.InlineKeyboardButton("Я не знаю", callback_data='5000')
            btn18 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn15, btn16, btn17, btn18)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 5. Будет ли сервер использоваться как веб-сервер?".format(
                                 call.from_user),
                             reply_markup=markup)

        # Help
        case 5000:
            max_step = cur.execute("SELECT MAX(step) FROM steps WHERE uid = ?", (call.message.chat.id,)).fetchone()[0]
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_ok = types.InlineKeyboardButton("Вернуться", callback_data=str(max_step))
            markup.add(btn_ok)
            bot.send_message(call.message.chat.id,
                             text="Если вы не планируете создавать публичные сайты (с большим количеством обращений),"
                                  " то выберите 'Нет'".format(
                                   call.from_user),
                             reply_markup=markup)

        # WebSrv
        case 610:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 610", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[4] += 2048
            data[5] += 8
            data[1] = 610
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn19 = types.InlineKeyboardButton("Результат", callback_data='700')
            btn20 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn19, btn20)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 6. Получить результат?".format(
                                 call.from_user),
                             reply_markup=markup)

        # not WebSrv
        case 620:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 620", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            max_step = data[1]
            data[1] = 620
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn19 = types.InlineKeyboardButton("Результат", callback_data='700')
            btn20 = types.InlineKeyboardButton("Отмена", callback_data=str(max_step))
            markup.add(btn19, btn20)
            bot.send_message(call.message.chat.id,
                             text="Вопрос 6. Получить результат?".format(
                                 call.from_user),
                             reply_markup=markup)

        # Results
        case 700:
            cur.execute("DELETE FROM steps WHERE uid = ? AND step > 700", (call.message.chat.id,))
            data = cur.execute("SELECT * FROM steps WHERE uid = ? AND step = (SELECT MAX(step) FROM steps"
                               " WHERE uid = ?)",
                               (call.message.chat.id, call.message.chat.id)).fetchall()[0]
            data = list(data)
            data[1] = 700
            cur.execute(
                "INSERT INTO steps (uid, step, cpu_kvm, cpu_count, ram_size, drive_size, server_hdd, server_ssd,"
                " realtek_drivers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*data,))
            db.commit()
            if data[2] == 1:
                cpu_kvm = "Процессор с поддержкой KVM (обязательно)"
            else:
                cpu_kvm = "Процессор с поддержкой KVM (опционально)"

            if data[7] == 1:
                drive_type = "SSD серверного класса"
            elif data[6] == 1 and data[7] == 0:
                drive_type = "HDD серверного класса"
            else:
                drive_type = "HDD любого класса"

            if data[8] == 1:
                network_card = "Любая\n"
            else:
                network_card = "Не Realtek (отсутствует официальная поддержка)\n"

            results = "Требования к оборудованию: \n" + str(cpu_kvm) + \
                      "\nЧисло ядер процессора: " + str(data[3]) + \
                      "\nОбъём оперативной памяти не менее " + str(data[4]) + " Мб" + \
                      "\nОбъём дискового пространства не менее " + str(data[5]) + " Гб на " + drive_type + \
                      "\nСетевая карта: " + network_card
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn21 = types.InlineKeyboardButton("Главное меню", callback_data='10')
            btn22 = types.InlineKeyboardButton("Завершить работу", callback_data='0')
            markup.add(btn21, btn22)
            bot.send_message(call.message.chat.id,
                             text=results.format(
                                 call.from_user))
            bot.send_message(call.message.chat.id,
                             text="Выйти в главное меню или завершить работу?".format(
                                 call.from_user),
                             reply_markup=markup)


bot.polling(none_stop=True)
