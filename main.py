import requests
import csv
import requests, zipfile, io
import re
import os.path
import telebot
from datetime import datetime
from colorama import Fore
from auth_data import token

link = requests.get(
    "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/").text
zip_links = re.findall(r'<Key>(.*?)</Key>', link)

# todo: скачать архив по ссылке, разархивировать, сохранить в папке, проверить скачивался ли файл ранее

link = requests.get(
    f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/BTCBUSD/1m/&marker={zip_links[-1]}").text
zip_links = re.findall(r'<Key>(.*?).zip', link)
link_zip = requests.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/{zip_links[-1]}.zip")
file = str(zip_links[-1]).removeprefix("data/spot/daily/klines/BTCBUSD/1m/")
check_file = os.path.isfile(f"/home/vadimafonievich/Документы/PycharmProjects/Zadacha4/zip_files/csv_files/{file}.csv")

if check_file == False:
    print("Файла не было! Скачал новый!")
    z = zipfile.ZipFile(io.BytesIO(link_zip.content))
    z.extractall("/home/vadimafonievich/Документы/PycharmProjects/Zadacha4/zip_files/csv_files/")

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

# todo: создать telegram бота

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Hello friend! Write the 'price'!")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if message.text.lower() == "/price":
            bot.send_message(message.chat.id, "Wait a minute, counting in progress...")
            try:
                with open(f"/home/vadimafonievich/Документы/PycharmProjects/Zadacha4/zip_files/csv_files/{file}.csv", "r") as f:
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
                        # if i == 11:
                        #     break
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

                        if open1 > close:
                            print(
                                Fore.RED + f"{i:5d}: {date_time: %d.%m %H:%M}  {open1:7.2f}  {high:7.2f}  {low:7.2f}  {close:7.2f}  {volume:7.2f}  {amp:.3f}  ")
                        else:
                            print(
                                Fore.GREEN + f"{i:5d}: {date_time: %d.%m %H:%M}  {open1:7.2f}  {high:7.2f}  {low:7.2f}  {close:7.2f}  {volume:7.2f}  {amp:.3f}  ")

                    print(Fore.WHITE + f"Max: {max_high}")
                    print(Fore.WHITE + f"Min: {min_low}")
                    print(Fore.WHITE + f"AvgMM: {round(sr_close / i, 2)}")
                    print(Fore.WHITE + f"Avg: {(min_low + max_high) / 2:.2f}")
                    print(Fore.WHITE + f"Max Amp: {max_amp:.3f} %")
                    print(Fore.WHITE + f"Min Amp: {min_amp:.3f} %")
                    print(Fore.WHITE + f"Amp: {amp_sum / i:.3f} %")

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
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Damn... Something was wrong..."
                )
        else:
            bot.send_message(message.chat.id, "Whaaat??? Check the command dude!")

    bot.polling()

telegram_bot(token)


