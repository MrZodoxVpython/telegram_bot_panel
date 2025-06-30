#from __init__ import *
from xolpanel import *
from importlib import import_module
from telegram_bot_panel.modules import ALL_MODULES
for module_name in ALL_MODULES:
        imported_module = import_module("telegram_bot_panel.modules." + module_name)
bot.run_until_disconnected()

