#encoding: utf-8

import os
import logging
import uuid
import json
import StringIO
from io import BytesIO


class TelegramBotHandler(logging.StreamHandler):
    """
    A handler class which writes formatted logging records to telegram bot.

    Usage:
    logging.root.addHandler(TelegramBotHandler('XXXXXXXXX:XXXXXXX-XXXXXXXXXX-XXXXXXXXX-XXXXXX',\
                            [XXXXXXXXX]))
    ...
    logging.warning('Hello world!', extra={'bot': True})

    """
    def __init__(self, botid, bot_users=[]):

        logging.StreamHandler.__init__(self)
        self.stream = None
        self.botid = botid
        self.bot_users = bot_users
        self.formatter = logging.Formatter(fmt=logging.BASIC_FORMAT)
        self.figure_width = 800
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

        if not self._bot:
            return

        if ('bot' in record.__dict__) and (record.__dict__['bot']):
            if len(record.msg) > 0:
                self.stream = StringIO.StringIO()
                logging.StreamHandler.emit(self, record)
                try:
                    for id in self.bot_users:
                        self._bot.send_message(id, self.stream.getvalue())
                except:
                    self.handleError(record)
            if 'figure' in record.__dict__:
                fig = record.__dict__['figure']
                import matplotlib
                from matplotlib import rcParams
                if isinstance(fig, matplotlib.figure.Figure):
                    kw = dict( format='png'
                             , facecolor=fig.get_facecolor()
                             , edgecolor=fig.get_edgecolor()
                             # , dpi=rcParams['savefig.dpi']
                             , dpi=self._adjust_dpi(fig)
                             , bbox_inches='tight'
                             )
                    bytes_io = BytesIO()
                    fig.canvas.print_figure(bytes_io, **kw)
                    try:
                        for id in self.bot_users:
                            bytes_io.seek(0)
                            self._bot.send_photo(id, bytes_io)
                    except:
                        self.handleError(record)
            if 'image' in record.__dict__:
                image = record.__dict__['image']
                if isinstance(image, basestring):
                    try:
                        image = open(os.path.expanduser(image), 'rb')
                    except:
                        return
                try:
                    for id in self.bot_users:
                        image.seek(0)
                        self._bot.send_photo(id, image)
                except:
                    self.handleError(record)
            if 'file' in record.__dict__:
                _file = record.__dict__['file']
                if isinstance(_file, basestring):
                    try:
                        _file = open(os.path.expanduser(_file), 'rb')
                    except:
                        return
                try:
                    for id in self.bot_users:
                        _file.seek(0)
                        self._bot.send_document(id, _file)
                except:
                    self.handleError(record)

    def _adjust_dpi(self, f):
        w, h = f.get_size_inches()
        return self.figure_width / w * 1.065
