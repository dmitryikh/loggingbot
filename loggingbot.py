#encoding: utf-8

import os
import logging
import uuid
import json
import StringIO

MAX_TELEGRAM_MESSAGE = 4096

class ToFolderHandler(logging.Handler):
    """
    Write log record to json-file with unique filename in directory `dir`

    Usage:
    logging.root.addHandler(ToFileHandler('~/.logmessages'))
    """
    def __init__(self, dir):
        """
        Initialize the handler.
        """
        self.dir = os.path.abspath(os.path.expanduser(dir))
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        if not os.path.isdir(self.dir):
            raise RuntimeError('{} is not a directory'.format(self.dir))
        logging.Handler.__init__(self)

    def emit(self, record):
        """
        Emit a record.

        """
        try:
            self.acquire()
            with open(os.path.join(self.dir, str(uuid.uuid4())), 'w') as fout:
                json.dump(record.__dict__, fout, indent=1)
                # pickle.Pickler(fout).save_dict(record.__dict__)
            self.release()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class TelegramBotHandler(logging.StreamHandler):
    """
    A handler class which writes formatted logging records to telegram bot.

    Usage:
    logging.root.addHandler(TelegramBotHandler('XXXXXXXXX:XXXXXXX-XXXXXXXXXX-XXXXXXXXX-XXXXXX',\
                            [XXXXXXXXX]))
    ...
    logging.warning('Hello world!', extra={'bot': True})

    """
    def __init__(self, botid, bot_users=[], encoding=None):

        logging.StreamHandler.__init__(self)
        self.stream = None
        self.botid = botid
        self.bot_users = bot_users
        self.encoding = encoding
        self.formatter = logging.Formatter(fmt=logging.BASIC_FORMAT)
        # try to init bot
        try:
            import telebot
            self._bot = telebot.TeleBot(botid)
        except:
            self._bot = None

    def close(self):
        """
        Closes the bot.
        """
        self.acquire()
        self._bot = None
        self.release()

    def emit(self, record):
        """
        Emit a record.
        """
        if ('bot' in record.__dict__) and record.__dict__['bot']:
            self.stream = StringIO.StringIO()
            logging.StreamHandler.emit(self, record)
            # Truncate message to Telegram's max length
            message = self.stream.getvalue()[:MAX_TELEGRAM_MESSAGE]
            self.stream.close()
            self.stream = None
            try:
                if self._bot:
                    for id in self.bot_users:
                        self._bot.send_message(id, message)
            except:
                self.handleError(record)
