from telegram.ext import Updater
import logging


logger = False
tg_bot = False


class TokenError(BaseException):
    def __str__(self):
        return "File with token not found"


def get_logger():
    global logger
    if logger:
        return logger
    logger = logging.getLogger("Notifications_bot")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("log.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s.%(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def get_bot():
    global tg_bot
    if tg_bot:
        return tg_bot
    try:
        from .tg_token import TOKEN
    except ImportError:
        print('Файл с токеном не найден')
        raise TokenError
    else:
        updater = Updater(TOKEN, use_context=True)
        tg_bot = updater.bot
        return tg_bot


def notify(user, text):
    logger = get_logger()
    tg_bot = get_bot()
    try:
        if user.chat_id:
            tg_bot.send_message(user.chat_id, text)
            logger.info(f"{user.nickname} was just notified that {text}")
    except Exception as e:
        logger.error(f"{type(e)}: {str(e)}")
        tg_bot.send_message(888848705, f"{type(e)}: {str(e)}")


def disconnect(db, user):
    logger = get_logger()
    tg_bot = get_bot()
    chat_id = user.chat_id
    user.chat_id = ' '
    db.commit()
    tg_bot.send_message(chat_id, f"Аккаунт {user.nickname} успешно отвязан. Вы больше не будете получать уведомления")
    logger.info(f"{user.nickname} отвязал аккаунт")


def check_updates(db, User):
    logger = get_logger()
    tg_bot = get_bot()
    try:
        with open('last.txt', 'r') as f:
            update_id = int(f.read().strip()) + 1
    except FileNotFoundError:
        update_id = None
    updates = tg_bot.get_updates(offset=update_id)
    for update in updates:
        e = check_update(db, logger, User, update)
        if e:
            tg_bot.send_message(888848705, f"{type(e)}: {str(e)}")


def check_update(db, logger, User, update):
    code = update.message.text.strip().lower()
    user = db.query(User).filter(User.secret_code == code).first()
    chat_id = update.message.chat.id
    with open('last.txt', 'w') as f:
        f.write(str(update.update_id))
    if not user:
        logger.warning(f"Wrong code from {chat_id}")
        update.message.reply_text("Неверный код")
    else:
        try:
            user.chat_id = chat_id
            db.commit()
            update.message.reply_text(f"Аккаунт {user.nickname} привязан")
            logger.info(f"Аккаунт {user.nickname} привязан к {chat_id}")
        except Exception as e:
            logger.error(f"{type(e)}: {str(e)}")
            update.message.reply_text(f"Произошла ошибка")
            return e