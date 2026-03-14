#############################################################################################################################                                                                                                                    
#           ,,                                                            ,,                               ,,               #
#         `7MM                                                           *MM                             `7MM               #
#           MM                                                            MM                               MM               #
#      ,M""bMM  ,pW"Wq.   .P"Ybmmm ,pW"Wq.`7M'   `MF',pW"Wq.`7Mb,od8      MM,dMMb.`7M'   `MF'     ,pW"Wq.  MM  `7Mb,od8     # 
#    ,AP    MM 6W'   `Wb :MI  I8  6W'   `Wb VA   ,V 6W'   `Wb MM' "'      MM    `Mb VA   ,V      6W'   `Wb MM    MM' "'     #
#    8MI    MM 8M     M8  WmmmP"  8M     M8  VA ,V  8M     M8 MM          MM     M8  VA ,V       8M     M8 MM    MM         #
#    `Mb    MM YA.   ,A9 8M       YA.   ,A9   VVV   YA.   ,A9 MM          MM.   ,M9   VVV        YA.   ,A9 MM    MM         #
#     `Wbmd"MML.`Ybmd9'   YMMMMMb  `Ybmd9'     W     `Ybmd9'.JMML.        P^YbmdP'    ,V          `Ybmd9'.JMML..JMML.       #
#                        6'     dP                                                   ,V                                     #
#                        Ybmmmd'                                                  OOb"                                      #
#                                                                                                                           #
#############################################################################################################################
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from docx import Document

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Продолжить", callback_data="next")] #это мы добавляем кнопку по которой можно жать и перейдём в другое меню
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Чтобы загрузить новые файлы нажмите продолжить"
    context.bot.send_message( #здесь мы отправляем сообщение человеку
        chat_id = update.effective_chat.id,
        text = text,
        reply_markup = reply_markup)

def main():
    TOKEN = '7393184999:AAHL2ybVhjGXqnDWjStuFp-YJQLaKde-7pc'
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(next, pattern='^next$')) 
    dispatcher.add_handler(CallbackQueryHandler(obrabotka, pattern='^obrabotka$')) 
    dispatcher.add_handler(CallbackQueryHandler(start, pattern='^start$')) 
    dispatcher.add_handler(CallbackQueryHandler(file_choice, pattern="^(word|excel)$"))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()