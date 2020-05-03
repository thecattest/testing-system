from telegram.ext import Updater
import logging


class TokenError(BaseException):
    def __str__(self):
        return "File with token not found"


def check_updates(db, User):
    logger = logging.getLogger("Notifications_bot")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("log.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s.%(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    try:
        from .tg_token import TOKEN
    except ImportError:
        print('Файл с токеном не найден')
        raise TokenError
    else:
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot
        try:
            with open('last.txt', 'r') as f:
                update_id = int(f.read().strip())
        except FileNotFoundError:
            update_id = None
        updates = bot.get_updates(offset=update_id)
        for update in updates:
            e = check_update(db, logger, User, update)
            if e:
                bot.send_message(888848705, f"{type(e)}: {str(e)}")


def check_update(db, logger, User, update):
    code = update.message.text.strip()
    user = db.query(User).filter(User.secret_code == code).first()
    chat_id = update.message.chat.id
    if not user:
        logger.warning(f"Wrong code from {chat_id}")
        update.message.reply_text("Неверный код")
    else:
        try:
            user.chat_id = chat_id
            db.commit()
            update.message.reply_text(f"Аккаунт {user.nickname} привязан")
            logger.info(f"Аккаунт {user.nickname} привязан к {chat_id}")
            with open('last.txt', 'w') as f:
                f.write(str(update.update_id))
        except Exception as e:
            logger.error(f"{type(e)}: {str(e)}")
            update.message.reply_text(f"Произошла ошибка")
            return e