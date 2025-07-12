from aiogram.types import BotCommand

commands = [
    BotCommand(command='/games', description='Каталог игр'),
    BotCommand(command='/my_rents', description='Мои аренды'),
    BotCommand(command='/my_rents_history', description='История моих аренд'),
    BotCommand(command='/balance', description='Баланс'),
    BotCommand(command='/add_balance', description='Пополнить баланс'),
    BotCommand(command='/extend_rent', description='Продлить аренду'),
]