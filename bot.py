from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ParseMode
import requests
import logging
import re
import random
import datetime
import numpy as np
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

KOM = 0

API_key = os.getenv('API_key')

def wetter(update, context):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Freudenstadt,DE&appid=0bc532c546f93f5a78c999d5b5362485')
    temp = int(round(r.json()['main']['temp'] - 273.15))
    message = 'In dr Fraidestadt hots {:d} Grad.'.format(temp)
    description = r.json()['weather'][0]['description']
    logger.info("Weather description: %s", description)
    if description =='light rain':
        message += ' Onds regnet a bissle.'
    elif description == "overcast clouds":
        message += ' Onds isch bedeckt.'
    elif description == "clear sky":
        message += ' Koi Welkle am Hemmel.'
    elif description == "few clouds":
        message += ' Onds hot faschd koine wolke.'
    elif description == "scattered clouds":
        message += ' Onds hot a bar wölkle.'
    elif description == "broken clouds":
        message += ' Es isch wechselnd bewölkt.'
    update.message.reply_text(message)

def witz(update, context):
    try:
        r = requests.get('https://saechla.de/schwabenwitze/')
        pattern = "<blockquote><p>(.*)</p></blockquote>"
        witze = re.findall(pattern, r.text)
        witz = random.choice(witze)
    except:
        witz = "Mir fällt grad koiner ei :("
    context.bot.send_message(update.message.chat_id, text=witz, parse_mode = ParseMode.HTML)

def start(update, context):
    update.message.reply_text("Hallöle, i be dr Schwarzwald Bot!\n\n"
    "Des kenned ihr med mir macha:\n"
    "/wetter - s'wetter in dr Fraidastadt\n"
    "/schwaetz - no schwaetz i mit\n"
    "/witz - no vrzehl i en witz\n"
    "/hond - no schick i's bildle von em hond\n"
    "/katz - no schick i's bildle vorer katz\n")


def deilapp(update, context):
    """Echo the user message."""
    update.message.reply_text("isch ja gut...")

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

def hond(update, context):
    url = get_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)

def katz(update, context):
    gruss_list = ['Hallöle!', 'Servus!', 'Grüess di!', 'Daag!', 'Heiligs Blechle!', 'Du kosch mir mol de Schue uffblosa!']
    url = "https://cataas.com/cat/says/"+random.choice(gruss_list)
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)

def tscholl(update, context):
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo="/app/images/tscholl.jpg", caption="Hallöle!")

def grischi(update, context):
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo="/app/images/grischi.jpg", caption="Servus!")

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Leude, es isch acht uhr achtzehn! 🤖')

def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    set_time = datetime.time(6, 18, 0)
    # Add job to queue and stop current one if there is a timer already
    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        old_job.schedule_removal()
    new_job = context.job_queue.run_daily(alarm, set_time, days = tuple(range(7)),  context=chat_id)
    context.chat_data['job'] = new_job

def schwaetz(update, context):
    update.message.reply_text(
        "OK, I schwätz jetzt mit!\n"
        "Wenn's zviel isch, schreibsch oifach /deilapp.")

    return KOM

def kommentar(update, context):
    user = update.message.from_user
    kommentare = [
        user.first_name+', was labersch du?',
        "Des glaub i ned...",
        "Heiligs Blechle!",
        "Heidenei!",
        "Du kosch mer mol de Schue uffblosa!",
        "Sel isch richtig!",
        "So isch grad!",
        "Was de ned sagsch...",
        user.first_name+", du bisch so domm!",
        user.first_name+", du bisch selda bleed!"
    ]
    antworten = [
        "Wois i ned.",
        "Koi Ahnung.",
        "Des würd mi au inderessiere...",
        "Woher soll i des wisse?",
        "Frog mi was leichderes..."
    ]
    if "?" in update.message.text:
        update.message.reply_text(random.choice(antworten))
    else:
        update.message.reply_text(random.choice(kommentare))
        
    return KOM


def deilapp(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Isch ja gud...')

    return ConversationHandler.END



def main():
    updater = Updater(API_key, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('schwaetz', schwaetz)],

        states={
            KOM: [MessageHandler(Filters.text & ~Filters.command, kommentar)]
        },

        fallbacks=[CommandHandler('deilapp', deilapp)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('witz', witz))
    dp.add_handler(CommandHandler('hond', hond))
    dp.add_handler(CommandHandler('katz', katz))
    dp.add_handler(CommandHandler('tscholl', tscholl))
    dp.add_handler(CommandHandler('grischi', grischi))
    dp.add_handler(CommandHandler('wetter', wetter))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_key)
    updater.bot.setWebhook('https://schwarzwald-bot.herokuapp.com/' + API_key)

    updater.idle()
    
if __name__ == '__main__':
    main()
