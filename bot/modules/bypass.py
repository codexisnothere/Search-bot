import json
import multiprocessing
import re
import time

import requests
import requests as rq
from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage
from bs4 import BeautifulSoup as bt
from telegram.ext import CommandHandler

msg_txt = """
<b>Source Link</b> : {}

<b>Bypassed Link</b> : {}
"""


def lv_bypass(update,context):
    try:
        link = update.message.text.split(' ',maxsplit=1)[1]
        extra_domains = ["linkvertise.com" , "link-to.net" , "direct-link.net" , "up-to-down.net" , "filemedia.net" , "file-link.net"]
        if 'linkvertise' not in link:
            for i in extra_domains:
                if i in link:
                    link = link.replace(i, "linkvertise.net")
        LOGGER.info(f"Bypassing Link Vertise: {link}")
        reply = sendMessage(f'<b>Bypassing {link} .....</b>\n\n<i>Please Wait For Some Time!</i>', context.bot, update)
        _apiurl = f"https://bypass.bot.nu/bypass2?url={link}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
        try:
            resp = requests.get(_apiurl, headers=headers)
            if resp.status_code == 200:
                jresp = resp.json()
                src = f"{link}"
                grpmsg = editMessage(msg_txt.format(src, jresp["destination"]), reply)
            elif resp.status_code in [415, 422]:
                grpmsg = editMessage("Invalid Source URL", reply)
            elif resp.status_code == 404:
                jresp = resp.json()
                msg = "{}\n\nPlugin : {}"
                grpmsg = editMessage(msg.format(jresp["msg"], jresp["plugin"]), reply)
            else:
                msg = "API Status Code {}"
                grpmsg = editMessage(msg.format(str(resp.status_code)), reply)
        except BaseException as e:
            grpmsg = editMessage(f'Error : {e}', reply)
    except IndexError:
        sendMessage('Send A Linkvertise Link Along With Command', context.bot, update)

class gp:
      def __init__(self, url):
          self.url = url
          self.apv = ''
          self.h = ''
          self.c = ''
          self.p = ''
          self.ref = ''
          self.r = r'\bhttps?://.*gplink\S+'

      def req(i, h, c, p, bot, update):
          time.sleep(10)
          rpt = rq.post("%s/links/go"%(i.rsplit("/",1)[0]), headers=h, cookies=c, data=p).json()
          msg = f"<b>Source Link</b> : {i}\n\n<b>Bypassed Link</b> : {rpt['url']}"
          grpmsg = sendMessage(msg ,bot, update)
          return

      def parse(self, bot, update):
          r = re.findall(self.r,self.url)
          if not r:
              sendMessage("<b>The Link You Provided Is Invalid</b>", bot, update)
          else:
              ps = []
              for i in r:
                  try:
                      rh = rq.head(i).headers
                      rg = re.findall(r"(?:AppSession|app_visitor|__cf_bm)\S+;",rh['set-cookie'])
                      st = " ".join(rg).replace("=",": ",3).replace(";",",")
                      rg1 = re.sub(r"([a-zA-Z_0-9.%+/=-]+)",r'"\1"','{%s __viCookieActive: true, __cfduid: dca0c83db7d849cdce8d82d043f5347bd1617421634}'%st)
                      jd = json.loads(rg1)
                      self.c = jd
                      self.apv = jd["AppSession"]
                      self.ref = rh["location"]
                      self.h = {"app_visitor": self.apv,
                                "user-agent": "Mozilla/5.0 (Symbian/3; Series60/5.2 NokiaN8-00/012.002; Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/533.4 (KHTML, like Gecko) NokiaBrowser/7.3.0 Mobile Safari/533.4 3gpp-gba",
                                "upgrade-insecure-requests": "1",
                                "referer": self.ref}
                      rget = rq.get(i, cookies=self.c, headers=self.h).content
                      bs4 = bt(rget, 'html.parser', from_encoding="iso-8859-1")
                      fin = bs4.find_all('input')
                      dic = {g.get('name'): g.get('value') for g in fin}
                      self.p = dic
                      self.c = {"AppSession": jd["AppSession"], "csrfToken": dic["_csrfToken"]}
                      self.h = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "accept": "application/json, text/javascript, */*; q=0.01", "x-requested-with": "XMLHttpRequest"}
                      p = multiprocessing.Process(target=gp.req, args=[i, self.h, self.c, self.p, bot, update])
                      p.start()
                      ps.append(p)
                  except Exception as e:
                      msg = f'<b>Source URL</b> : {i}\n\n<b>Error While Bypassing</b> : {e}'
                      sendMessage(msg, bot, update)
                      LOGGER.info('Error Occured : ' + str(e))
              for p in ps:
                  p.join()


def gparse(update, context):
    bot = context.bot
    try:
        args = update.message.text.split(" ", maxsplit=1)
        if len(args) > 1:
           link = args[1:]
           url = link
           j = '\n'.join('\n'.join(url).split())
           r = '\n'.join(re.split(r'(?=https:\/\/)', j)[1:])
           p = gp(r).parse(bot, update)
        else:
            sendMessage('Provide A GPlink Along With command', bot, update)
    except Exception as e:
        sendMessage('<b>Something Went Wrong</b>', bot, update)
        LOGGER.info('Error Occured : ' + str(e))
        return



lv_handler = CommandHandler(BotCommands.BypassCommand, lv_bypass,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,run_async=True)
gp_handler = CommandHandler(BotCommands.GPCommand, gparse, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,run_async=True)
dispatcher.add_handler(gp_handler)
dispatcher.add_handler(lv_handler)

cmds = [
    (f'{BotCommands.GPCommand}', 'For Bypassing GPlinks'),
    (f'{BotCommands.BypassCommand}', 'For Bypassing Linkvertise'),
]
