from telethon import *
import datetime as DT
from telethon import *
import requests,time,os,subprocess,re,sqlite3,sys,random
import logging
from telegram_bot_panel.text2png import text2png
logging.basicConfig(level=logging.INFO)
uptime = DT.datetime.now()

exec(open("telegram_bot_panel/var.txt","r").read())
bot = TelegramClient("Tokomard","6","eb06d4abfb49dc3eeb1aeb98ae0f581e").start(bot_token=BOT_TOKEN)
try:
	open("telegram_bot_panel/database.db")
except:
	x = sqlite3.connect("telegram_bot_panel/database.db")
	c = x.cursor()
	c.execute("CREATE TABLE admin (user_id)")
	c.execute("INSERT INTO admin (user_id) VALUES (?)",(ADMIN,))
	x.commit()

def get_db():
	x = sqlite3.connect("telegram_bot_panel/database.db")
	x.row_factory = sqlite3.Row
	return x

def valid(id):
	db = get_db()
	x = db.execute("SELECT user_id FROM admin").fetchall()
	a = [v[0] for v in x]
	if id in a:
		return "true"
	else:
		return "false"
