import telebot

# Замените на свой токен бота
BOT_TOKEN = '7746127828:AAFwul9QLWwtqGTjS2v6KV257NryUSzEc58'

ADMIN_CHAT_ID = '6672719813'

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения данных клиента и риелтора
request_data = {}

# Сообщение приветствия
welcome_message = (
    "Привет! Спасибо за обращение в компанию Этажи. Мы рады приветствовать вас!\n"
    "Вы можете ознакомиться с нашими работами в нашей группе: [Группа Этажи](https://example.com) (замените на реальную ссылку).\n"
    "Средний доход риелтора составляет 35.000 рублей за заявку. Мы поможем вам передать клиента на ремонт."
)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text=welcome_message, parse_mode='Markdown')
    bot.send_message(chat_id=message.chat.id, text="Пожалуйста, введите код вашего сотрудника:")
    bot.register_next_step_handler(message, get_realtor_code)

# Обработчик ввода кода риелтора
def get_realtor_code(message):
    request_data['realtor_code'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите ваш телефон:")
    bot.register_next_step_handler(message, get_realtor_phone)

# Обработчик ввода телефона риелтора
def get_realtor_phone(message):
    request_data['realtor_phone'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите ваше ФИО:")
    bot.register_next_step_handler(message, get_realtor_name)

# Обработчик ввода ФИО риелтора
def get_realtor_name(message):
    request_data['realtor_name'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите ФИО клиента:")
    bot.register_next_step_handler(message, get_client_name)

# Обработчик ввода ФИО клиента
def get_client_name(message):
    request_data['client_name'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите телефон клиента:")
    bot.register_next_step_handler(message, get_client_phone)

# Обработчик ввода телефона клиента
def get_client_phone(message):
    request_data['client_phone'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Введите площадь квартиры (кв. м):")
    bot.register_next_step_handler(message, get_square)

# Обработчик ввода площади квартиры
def get_square(message):
    request_data['square'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Укажите район:")
    bot.register_next_step_handler(message, get_region)

# Обработчик ввода района
def get_region(message):
    request_data['region'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Какой ремонт нужен? Выберите вариант (укажите цифру):\n1 - Полный\n2 - Частичный")
    bot.register_next_step_handler(message, get_repair_type)

# Обработчик выбора типа ремонта
def get_repair_type(message):
    request_data['repair_type'] = "Полный" if message.text == "1" else "Частичный"

    # Выбор сотрудника для заявки
    bot.send_message(chat_id=message.chat.id,
                     text="Выберите специалиста (укажите цифру):\n1 - Евгений\n2 - Наталья\n3 - Дарья\n4 - Павел")
    bot.register_next_step_handler(message, assign_specialist)

# Обработчик выбора специалиста
def assign_specialist(message):
    specialists = {"1": "Евгений", "2": "Наталья", "3": "Дарья", "4": "Павел"}
    request_data['specialist'] = specialists.get(message.text, "Неизвестный специалист")

    # Подтверждение данных
    confirmation_message = (
        "Спасибо за предоставленные данные!\n\n" 
        f"Риелтор: {request_data['realtor_name']} ({request_data['realtor_phone']})\n" 
        f"Клиент: {request_data['client_name']} ({request_data['client_phone']})\n"
        f"Площадь квартиры: {request_data['square']} кв. м\n"
        f"Район: {request_data['region']}\n"
        f"Тип ремонта: {request_data['repair_type']}\n"
        f"Специалист: {request_data['specialist']}"
    )

    # Отправка сообщения администратору
    bot.send_message(chat_id=ADMIN_CHAT_ID, text=confirmation_message)

    # Сообщение риелтору, что с клиентом свяжутся
    bot.send_message(chat_id=message.chat.id,
                     text="Спасибо за вашу заявку! С вами свяжется наш специалист в ближайшее время.")


# Запускаем бота
bot.polling()