import telegram
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import QuranicVerse as quran
import json

Token = ''

updater = telegram.ext.Updater('',use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    update.message.reply_text("Hello! Welcome to Roses of Madinah Bot. Find out about our classes and our latest class updates.")
    update.message.reply_text(
        """
        /start -> Welcome to the channel
        /Class Updates -> View updates of our current projects.
        /Project Updates -> View updates on our current projects.
        /help ->   This particular message
        /ContactInfomation -> Contact Details for any Queries
        /GiveMeAQuranicVerse -> Generates a verse from the Quran and send it to individuals as a daily reminder and source of inspiration.
        /LearnADua ->Learn important du'as and send it to your loved ones
        /LearnAHadith -> Learn important hadiths from the Prophet Muhammad(s.a.w)ﷺ 
        /IslamicQuote -> Get Islamic gems of advice from scholars and predecessors
        /GratitudeTracker -> Write down something you are grateful for today and at this moment.
        /IslamicQuiz ->  Quiz yourself on Islamic Knowledge(Starting from Elementary Level to Advanced Level Questions.)
        /GoodDeedReminder -> Remind yourself of small good deeds they you can perform throughout the day, such as saying "Assalamu Alaikum" to a stranger, or holding the door open for someone.
        /FindMyQibla  -> Show where the qibla is at your area
        """
    )



def help(update,context):
    update.message.reply_text(
        """
        /start -> Welcome to the channel
        /help ->   This particular message
        /ContactInfomation -> Contact Details for any Queries
        /Terawhere - >  Find latest Terawih prayer details
        /Halalfoodwhere - > Find the latest Halal food locations around.
        /GiveMeAQuranicVerse -> Generates a verse from the Quran and send it to individuals as a daily reminder and source of inspiration.
        /LearnADua ->Learn important du'as and send it to your loved ones
        /LearnAHadith -> Learn important hadiths from the Prophet Muhammad(s.a.w)ﷺ 
        /IslamicQuote -> Get Islamic gems of advice from scholars and predecessors
        /GratitudeTracker -> Write down something you are grateful for today and at this moment.
        /IslamicQuiz ->  Quiz yourself on Islamic Knowledge(Starting from Elementary Level to Advanced Level Questions.)
        /GoodDeedReminder -> Remind yourself of small good deeds that you can perform throughout the day, such as saying "Assalamu Alaikum" to a stranger, or holding the door open for someone.
        /FindMyQibla  -> Show where the qibla is at your area
        """
    )

# Web Scraping done from


def open_link(update, context):
    query = update.callback_query
    bot = context.bot
    bot.answer_callback_query(query.id)
    bot.send_message(chat_id=query.message.chat_id, text='<a href="https://qiblafinder.withgoogle.com/intl/en/desktop"></a>', parse_mode=telegram.ParseMode.HTML)

def ContactInformation(update,context):
    update.message.reply_text("Contact Information: Telegram: @rosemadinah Instagram: @rosemadinah ")


def GiveMeAQuranicVerse(update,context):
    update.message.reply_text(quran.printQuranicverse())


def LearnADua(update,context):
    update.message.reply_text("http://ayatalquran.com/random")

def LearnAHadith(update,context):
    update.message.reply_text("tutorial link: ")

def IslamicQuote(update,context):
    update.message.reply_text("smile")

def GratituteTracker(update,context):
    update.message.reply_text("Bismillah")

def IslamicQuiz(update,context):
    update.message.reply_text("Lets goo")

def FindMyQibla(update,context):
    button = [
        [
            InlineKeyboardButton("Find \Qibla", callback_data="open_link")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(button)
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=reply_markup)
#text="Click the button to open the link:",

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(open_link, pattern='open_link'))
dispatcher.add_handler(CommandHandler("GiveMeAQuranicVerse",GiveMeAQuranicVerse))
dispatcher.add_handler(CommandHandler("LearnADua",LearnADua))
dispatcher.add_handler(CommandHandler("LearnAHadith",LearnAHadith))
dispatcher.add_handler(CommandHandler("IslamicQuote",IslamicQuote))
dispatcher.add_handler(CommandHandler("LearnAHadith",LearnAHadith))
dispatcher.add_handler(CommandHandler("IslamicQuiz",IslamicQuiz))
dispatcher.add_handler(CommandHandler("FindMyQibla",FindMyQibla))
dispatcher.add_handler(CommandHandler("help", help))

updater.start_polling()
updater.idle()

