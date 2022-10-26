import re, requests, zipfile, io, os, csv, telebot
from os.path import isfile
from datetime import datetime
from colorama import Fore
from auth_data import token

# todo: скачать архив по ссылке, разархивировать, сохранить в папке, проверить скачивался ли файл ранее
host = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
link = requests.get(f"{host}?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/").text
zip_links = re.findall(r'<Key>(.*?)</Key>', link)
link = requests.get(f"{host}?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/&marker={zip_links[-1]}").text
zip_links = re.findall(r'<Key>(.*?).zip', link)
link_zip = requests.get(f"{host}/{zip_links[-1]}.zip")
file = str(zip_links[-1]).removeprefix("data/spot/daily/klines/BTCBUSD/1m/")
DATA_PATH = 'zip_files/csv_files/'
fds = sorted(os.listdir(DATA_PATH))

if not isfile(f"{DATA_PATH}{file}.csv"):
    print("Файла не было! Скачал новый!")
    z = zipfile.ZipFile(io.BytesIO(link_zip.content))
    z.extractall(DATA_PATH)


# todo: создать telegram бота

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start", "description"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет, друг! Выбери команду в меню!")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if message.text.lower() == "/price":
            bot.send_message(message.chat.id, "Подожди минуту, идет рассчет данных...")
            try:
                with open(f"{DATA_PATH}{file}.csv", "r") as f:
                    reader = csv.reader(f)
                    max_high = 0
                    min_low = 99999
                    sr_close = 0
                    amp_sum = 0
                    max_amp = 0
                    min_amp = 99999
                    i = 0
                    for line in reader:
                        i += 1
                        open_time = line[0][:10]
                        open1, high, low, close, volume = [round(float(x), 2) for x in line[1:6]]
                        date_time = datetime.fromtimestamp(int(open_time))
                        max_high = max(max_high, high)
                        min_low = min(min_low, low)
                        sr_close = (sr_close + close)
                        amp = abs((high - low) / open1 * 100)
                        max_amp = max(max_amp, amp)
                        min_amp = min(min_amp, amp)
                        amp_sum = amp_sum + amp
                        color = Fore.RED if open1 > close else Fore.GREEN

                        print(color + f"{i:5d}: {date_time: %d.%m %H:%M}  {open1:7.2f}  {high:7.2f}  {low:7.2f}  "
                                      f"{close:7.2f}  {volume:7.2f}  {amp:.3f}  ")

                bot.send_message(
                    message.chat.id,
                    f"Price to: {date_time: %d.%m.%Y %H:%M}\n\n"
                    f"Max: {max_high}\n"
                    f"Min: {min_low}\n"
                    f"AvgMM: {round(sr_close / i, 2)}\n"
                    f"Avg: {(min_low + max_high) / 2:.2f}\n"
                    f"Max Amp: {max_amp:.3f} %\n"
                    f"Min Amp: {min_amp:.3f} %\n"
                    f"Amp: {amp_sum / i:.3f} %"
                )
                # print(Fore.WHITE + f"Max: {max_high}\n"
                #                    f"Min: {min_low}\n"
                #                    f"AvgMM: {round(sr_close / i, 2)}\n"
                #                    f"Avg: {(min_low + max_high) / 2:.2f}\n"
                #                    f"Max Amp: {max_amp:.3f} %\n"
                #                    f"Min Amp: {min_amp:.3f} %\n"
                #                    f"Amp: {amp_sum / i:.3f} %\n"
                #       )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Damn... Something was wrong..."
                )
        # todo: выдать данные за 7 дней
        elif message.text.lower() == "/price7days":
            bot.send_message(message.chat.id, "Ебать колотить!!! Я Бот - я работаю!!! Щас выдам инфу за 7 дней! Минуту")
            try:
                max_high7 = 0
                min_low7 = 99999
                sr_close7 = 0
                amp_sum7 = 0
                max_amp7 = 0
                min_amp7 = 99999
                for i in fds[:-8:-1]:
                    with open(f"{DATA_PATH}{i}", "r") as f:
                        reader = csv.reader(f)
                        max_high = 0
                        min_low = 99999
                        sr_close = 0
                        amp_sum = 0
                        max_amp = 0
                        min_amp = 99999

                        i = 0
                        for line in reader:
                            i += 1
                            open_time = line[0][:10]
                            open1, high, low, close, volume = [round(float(x), 2) for x in line[1:6]]
                            date_time = datetime.fromtimestamp(int(open_time))
                            max_high = max(max_high, high)
                            min_low = min(min_low, low)
                            sr_close = (sr_close + close)
                            amp = abs((high - low) / open1 * 100)
                            max_amp = max(max_amp, amp)
                            min_amp = min(min_amp, amp)
                            amp_sum = amp_sum + amp
                            color = Fore.RED if open1 > close else Fore.GREEN

                            print(color + f"{i:5d}: {date_time: %d.%m %H:%M}  {open1:7.2f}  {high:7.2f}  {low:7.2f}  "
                                          f"{close:7.2f}  {volume:7.2f}  {amp:.3f}  ")

                    bot.send_message(
                        message.chat.id,
                        f"Price to: {date_time: %d.%m.%Y %H:%M}\n\n"
                        f"Max: {max_high}\n"
                        f"Min: {min_low}\n"
                        f"AvgMM: {round(sr_close / i, 2)}\n"
                        f"Avg: {(min_low + max_high) / 2:.2f}\n"
                        f"Max Amp: {max_amp:.3f} %\n"
                        f"Min Amp: {min_amp:.3f} %\n"
                        f"Amp: {amp_sum / i:.3f} %"
                    )

                    # print(Fore.WHITE + f"Max: {max_high}\n"
                    #                    f"Min: {min_low}\n"
                    #                    f"AvgMM: {round(sr_close / i, 2)}\n"
                    #                    f"Avg: {(min_low + max_high) / 2:.2f}\n"
                    #                    f"Max Amp: {max_amp:.3f} %\n"
                    #                    f"Min Amp: {min_amp:.3f} %\n"
                    #                    f"Amp: {amp_sum / i:.3f} %\n"
                    #       )

                    max_high7 = max(max_high7, max_high)
                    min_low7 = min(min_low7, min_low)
                    sr_close7 = (sr_close7 + sr_close)
                    max_amp7 = max(max_amp7, max_amp)
                    min_amp7 = min(min_amp7, min_amp)
                    amp_sum7 = amp_sum7 + amp_sum

                bot.send_message(
                    message.chat.id,
                    f"А вот сводные данные за предыдущие 7 дней: \n\n"
                    f"Max: {max_high7:_>30.2f}\n"
                    f"Min: {min_low7:_>31.2f}\n"
                    f"AvgMM: {sr_close7 / (7*i):_>27.2f}\n"
                    f"Avg: {(min_low7 + max_high7) / 2:_>31.2f}\n"
                    f"Max Amp: {max_amp7:_>22.3f}\n"
                    f"Min Amp: {min_amp7:_>23.3f}\n"
                    f"Amp: {amp_sum7 / (7*i):_>27.3f}\n"
                )
                # print(f"Max for 7 days: {max_high7:.2f}"
                #       f"Min for 7 days: {min_low7:.2f}"
                #       f"AvgMM for 7 days: {sr_close7 / (7 * i):.2f}"
                #       f"Avg for 7 days: {(min_low7 + max_high7) / 2:.2f}"
                #       f"Max Amp for 7 days: {max_amp7:.3f}"
                #       f"Min Amp for 7 days: {min_amp7:.3f}"
                #       f"Amp for 7 days: {amp_sum7 / (7 * i):.3f}")

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Damn... Something was wrong..."
                )

        # todo: выдать данные за 30 дней
        elif message.text.lower() == "/price30days":
            bot.send_message(message.chat.id, "Ебать колотить!!! Я Бот - я работаю!!! Щас выдам инфу за 7 дней! Минуту")
            try:
                max_high7 = 0
                min_low7 = 99999
                sr_close7 = 0
                amp_sum7 = 0
                max_amp7 = 0
                min_amp7 = 99999
                for i in fds[:-30:-1]:
                    with open(f"{DATA_PATH}{i}", "r") as f:
                        reader = csv.reader(f)
                        max_high = 0
                        min_low = 99999
                        sr_close = 0
                        amp_sum = 0
                        max_amp = 0
                        min_amp = 99999

                        i = 0
                        for line in reader:
                            i += 1
                            open_time = line[0][:10]
                            open1, high, low, close, volume = [round(float(x), 2) for x in line[1:6]]
                            date_time = datetime.fromtimestamp(int(open_time))
                            max_high = max(max_high, high)
                            min_low = min(min_low, low)
                            sr_close = (sr_close + close)
                            amp = abs((high - low) / open1 * 100)
                            max_amp = max(max_amp, amp)
                            min_amp = min(min_amp, amp)
                            amp_sum = amp_sum + amp
                            color = Fore.RED if open1 > close else Fore.GREEN

                            print(
                                color + f"{i:5d}: {date_time: %d.%m %H:%M}  {open1:7.2f}  {high:7.2f}  {low:7.2f}  "
                                        f"{close:7.2f}  {volume:7.2f}  {amp:.3f}  ")

                    # bot.send_message(
                    #     message.chat.id,
                    #     f"Price to: {date_time: %d.%m.%Y %H:%M}\n\n"
                    #     f"Max: {max_high}\n"
                    #     f"Min: {min_low}\n"
                    #     f"AvgMM: {round(sr_close / i, 2)}\n"
                    #     f"Avg: {(min_low + max_high) / 2:.2f}\n"
                    #     f"Max Amp: {max_amp:.3f} %\n"
                    #     f"Min Amp: {min_amp:.3f} %\n"
                    #     f"Amp: {amp_sum / i:.3f} %"
                    # )

                    # print(Fore.WHITE + f"Max: {max_high}\n"
                    #                    f"Min: {min_low}\n"
                    #                    f"AvgMM: {round(sr_close / i, 2)}\n"
                    #                    f"Avg: {(min_low + max_high) / 2:.2f}\n"
                    #                    f"Max Amp: {max_amp:.3f} %\n"
                    #                    f"Min Amp: {min_amp:.3f} %\n"
                    #                    f"Amp: {amp_sum / i:.3f} %\n"
                    #       )

                    max_high7 = max(max_high7, max_high)
                    min_low7 = min(min_low7, min_low)
                    sr_close7 = (sr_close7 + sr_close)
                    max_amp7 = max(max_amp7, max_amp)
                    min_amp7 = min(min_amp7, min_amp)
                    amp_sum7 = amp_sum7 + amp_sum

                bot.send_message(
                    message.chat.id,
                    f"А вот сводные данные за предыдущие 30 дней: \n\n"
                    f"Max: {max_high7:_>30.2f}\n"
                    f"Min: {min_low7:_>31.2f}\n"
                    f"AvgMM: {sr_close7 / (30 * i):_>27.2f}\n"
                    f"Avg: {(min_low7 + max_high7) / 2:_>31.2f}\n"
                    f"Max Amp: {max_amp7:_>22.3f}\n"
                    f"Min Amp: {min_amp7:_>22.3f}\n"
                    f"Amp: {amp_sum7 / (30 * i):_>27.3f}\n"
                )
                # print(f"Max for 30 days: {max_high7:.2f}"
                #       f"Min for 30 days: {min_low7:.2f}"
                #       f"AvgMM for 30 days: {sr_close7 / (30 * i):.2f}"
                #       f"Avg for 30 days: {(min_low7 + max_high7) / 2:.2f}"
                #       f"Max Amp for 30 days: {max_amp7:.3f}"
                #       f"Min Amp for 30 days: {min_amp7:.3f}"
                #       f"Amp for 30 days: {amp_sum7 / (30 * i):.3f}")

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Damn... Something was wrong..."
                )

        else:
            bot.send_message(message.chat.id, "Чтооооо??? Выбери команду из выпадающего списка по кнопке 'Меню'!")

    bot.polling()


telegram_bot(token)

























# todo: скачать все zip архивы и разархивировать их в 1 папку в csv формате
"""
link = requests.get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/").text
zip_links = re.findall(r'<Key>(.*?)</Key>', link)

i = 0
while i <= len(zip_links):
    i += 2
    link_zip = requests.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/{zip_links[i]}")
    z = zipfile.ZipFile(io.BytesIO(link_zip.content))
    z.extractall("/home/vadimafonievich/Документы/PycharmProjects/Zadacha4/zip_files/csv_files/")

link = requests.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/&marker={zip_links[-1]}").text
zip_links = re.findall(r'<Key>(.*?)</Key>', link)

i = 0
while i <= len(zip_links):
    i += 2
    link_zip = requests.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/{zip_links[i]}")
    z = zipfile.ZipFile(io.BytesIO(link_zip.content))
    z.extractall("/home/vadimafonievich/Документы/PycharmProjects/Zadacha4/zip_files/csv_files/")
"""
