import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Функция для чтения слов из файла
def load_words(filename='words.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            words = file.read().splitlines()  # Чтение строк и удаление лишних символов
        return words
    except FileNotFoundError:
        return []

# Рисунок человечка
HANGMAN_PICS = [
    '''
     -----
     |   |
         |
         |
         |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
         |
         |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
     |   |
         |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
    /|   |
         |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
    /|\\  |
         |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
    /|\\  |
    /    |
         |
    -----''', 
    '''
     -----
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    -----'''
]

# Функция для начала игры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот для игры в Hangman. Введи команду /word для начала игры.")

# Функция для старта игры с случайным словом
async def word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    words = load_words()
    
    if words:
        random_word = random.choice(words)  # Выбираем случайное слово
        context.user_data['word'] = random_word  # Сохраняем слово для текущего игрока
        context.user_data['guesses'] = set()  # Храним уже угаданные буквы
        context.user_data['wrong_guesses'] = 0  # Счетчик неверных попыток
        current_display = '_' * len(random_word)
        context.user_data['current_display'] = current_display
        
        await update.message.reply_text(f"Слово для игры: {current_display}\nПопробуй угадать букву!")
        await update.message.reply_text(HANGMAN_PICS[context.user_data['wrong_guesses']])
    else:
        await update.message.reply_text("Ошибка: не удалось загрузить слова.")

# Функция для обновления текущего отображения слова
def get_current_display(word, guessed_letters):
    return ''.join([letter if letter in guessed_letters else '_' for letter in word])

# Функция для обработки сообщений с буквами
async def guess_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    word = context.user_data.get('word', '')
    guessed_letters = context.user_data.get('guesses', set())
    wrong_guesses = context.user_data.get('wrong_guesses', 0)
    current_display = context.user_data.get('current_display', '')
    
    letter = update.message.text.lower()
    
    # Проверка, что введено одно слово и это буква
    if len(letter) == 1 and letter.isalpha():
        if letter in guessed_letters:
            await update.message.reply_text(f"Ты уже пытался угадать букву '{letter}'. Попробуй другую!")
        else:
            guessed_letters.add(letter)
            context.user_data['guesses'] = guessed_letters

            if letter in word:
                current_display = get_current_display(word, guessed_letters)
                context.user_data['current_display'] = current_display
                await update.message.reply_text(f"Правильно! {current_display}")
            else:
                wrong_guesses += 1
                context.user_data['wrong_guesses'] = wrong_guesses
                await update.message.reply_text(f"Неверно! Попробуй еще раз.\n{HANGMAN_PICS[wrong_guesses]}")
                
            # Проверка на завершение игры
            if wrong_guesses >= 6:
                await update.message.reply_text(f"Ты проиграл! Загаданное слово: {word}")
                await update.message.reply_text("Игра закончена. Чтобы начать новую игру, введи /word.")
            elif '_' not in current_display:
                await update.message.reply_text(f"Поздравляю! Ты выиграл! Слово: {word}")
                await update.message.reply_text("Игра закончена. Чтобы начать новую игру, введи /word.")
            else:
                await update.message.reply_text(f"Текущее состояние слова: {current_display}")
    else:
        await update.message.reply_text("Пожалуйста, вводи только одну букву.")

# Основная функция для запуска бота
def main():
    application = Application.builder().token('8165289320:AAGPSpLBWVYRb5rV54vXGwnWkGk8kcMcYas').build()
    
    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("word", word))
    
    # Добавление обработчика для букв
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_letter))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
