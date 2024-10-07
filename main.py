import telebot
from telebot import types

API_TOKEN = '7746127828:AAFwul9QLWwtqGTjS2v6KV257NryUSzEc58'  # Замените на ваш токен
ADMIN_CHAT_ID = '6672719813'

bot = telebot.TeleBot(API_TOKEN)

# Структура для хранения данных заявки
request_data = {}
user_data = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    # Приветствие пользователя
    user_name = message.from_user.first_name  # Получаем имя пользователя
    user_data[message.chat.id] = user_name  # Сохраняем имя пользователя в словаре
    bot.send_message(message.chat.id, f"Привет, {user_name}! Я - бот команды Этажи.Ремонт. С моей помощью можно передать заявку на ремонт, рассчитать комиссию, которую ты заработаешь и получить презентации для себя и клиента.")
 
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_request = types.KeyboardButton("Заявка на ремонт")
    commission_calculator = types.KeyboardButton("Комиссия")
    bonus_btn = types.KeyboardButton("Этажи Бонус партнёры")
    create_request_bonus_btn = types.KeyboardButton("заявка Этажи Бонус")


    # Добавляем кнопки на клавиатуре
    keyboard.add(create_request, commission_calculator, bonus_btn, create_request_bonus_btn)
    bot.send_message(message.chat.id, "Добро пожаловать в бота! Выберите действие:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Заявка на ремонт")
def initiate_request(message):
    bot.send_message(chat_id=message.chat.id, text="Пожалуйста, введите ваш код сотрудника:")
    bot.register_next_step_handler(message, get_realtor_code)

# Обработчик ввода кода риелтора
def get_realtor_code(message):
    request_data['realtor_code'] = message.text
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
    bot.send_message(chat_id=message.chat.id, text="Укажите адресс объекта:")
    bot.register_next_step_handler(message, get_region)

# Обработчик ввода района
def get_region(message):
    request_data['region'] = message.text
    bot.send_message(chat_id=message.chat.id, text="Какой ремонт нужен? Выберите вариант (укажите цифру):\n1 - Полный\n2 - Частичный")
    bot.register_next_step_handler(message, get_repair_type)

# Обработчик выбора типа ремонта
def get_repair_type(message):
    request_data['repair_type'] = "Полный" if message.text == "1" else "Частичный"
    # Выбор специалиста для заявки
    bot.send_message(chat_id=message.chat.id,
                     text="Выберите менеджера (укажите цифру):\n1 - Евгений\n2 - Наталья\n3 - Дарья\n4 - Павел")
    bot.register_next_step_handler(message, assign_specialist)

# Обработчик выбора специалиста
def assign_specialist(message):
    specialists = {"1": "Евгений", "2": "Наталья", "3": "Дарья", "4": "Павел"}
    request_data['specialist'] = specialists.get(message.text, "Неизвестный специалист")
    # Подтверждение данных
    confirmation_message = (
        "Привет, у нас новая заявка!\n\n"
        f"Риелтор: {request_data['realtor_code']} \n"
        f"Клиент: {request_data['client_name']} ({request_data['client_phone']})\n"
        f"Площадь квартиры: {request_data['square']} кв. м\n"
        f"Адрес: {request_data['region']}\n"
        f"Тип ремонта: {request_data['repair_type']}\n"
        f"Менеджер Этажи.Ремонт: {request_data['specialist']}"
    )

    bot.send_message(ADMIN_CHAT_ID, confirmation_message)  # Отправляем заявку админу
    bot.send_message(message.chat.id, "Ваша заявка успешно создана! С вашим клиентом свяжутся в ближайшее время")


@bot.message_handler(func=lambda message: message.text == "Комиссия")
def commission_calculator(message):
    bot.send_message(message.chat.id, "Комиссия риелтора рассчитывается от стоимости работ.  Сумма не может быть пустой. Пожалуйста, введите сумму ремонта:")
    bot.register_next_step_handler(message, calculate_commission)


def calculate_commission(message):
    try:
        if not message.text.strip():
            bot.send_message(message.chat.id, "Комиссия риелтора рассчитывается от стоимости работ. Для более точного расчета, уточните сумму работ у менеджера. Сумма не может быть пустой. Пожалуйста, введите сумму ремонта:")
            bot.register_next_step_handler(message, calculate_commission)
            return

        amount = float(message.text)  # Возьмем сумму ремонта
        commission = amount * 0.05  # 5% комиссия

        # Форматируем вывод
        if commission.is_integer():
            response = f"Ваша комиссия от сделки составит: {int(commission)} руб."
        else:
            response = f"Ваша комиссия от сделки составит: {commission:.2f} руб."

        bot.send_message(message.chat.id, response)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число.")


@bot.message_handler(func=lambda message: message.text == "Этажи Бонус партнёры")
def loyalty_card_handler(message):
    send_categories(message)

def send_categories(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_remont = types.KeyboardButton("Ремонт")
    btn_materials = types.KeyboardButton("Строительные и отделочные материалы")
    btn_furniture = types.KeyboardButton("Мебель")
    btn_landscaping = types.KeyboardButton("Благоустройство квартиры")
    back_btn = types.KeyboardButton("Назад")  # Кнопка "Назад"
    markup.add(btn_remont, btn_materials, btn_furniture, btn_landscaping, back_btn)

    bot.send_message(message.chat.id, "В этом разделе ты сможешь ознакомиться с партнёрами, которые предоставляют скидки.", reply_markup=markup)
    bot.register_next_step_handler(message, handle_category)

def handle_category(message):
    if message.text == "Ремонт":
        response = "Этажи.Ремонт: Скидка 3% на услуги ремонта.\nУсловия: Минимальная сумма заказа 500,000 руб.\nСредняя комиссия риелтора за услугу 35,000 рублей\n\n" \
                   "Партнер 2: Скидка 15% на комплексные услуги.\nУсловия: Заказ на получение услуг через нашего менеджера.\n\n" \
                   "Партнер 3: Скидка 5% на любые работы.\nУсловия: Оплата наличными."
    elif message.text == "Строительные и отделочные материалы":
        response = "Партнер 1: Скидка 8% на все материалы.\nУсловия: Заказ от 5,000 руб.\n\n" \
                   "Партнер 2: Скидка 12% на определенные товары.\nУсловия: Условия акции меняются каждую неделю.\n\n" \
                   "Партнер 3: Скидка 7% на определенные категории материалов.\nУсловия: Предоставить сертификат лояльности."
    elif message.text == "Мебель":
        response = "Партнер 1: Скидка 20% на всю мебель.\nУсловия: Действует только на предзаказы.\n\n" \
                   "Партнер 2: Скидка 15% на мягкую мебель.\nУсловия: При покупке двух и более предметов.\n\n" \
                   "Партнер 3: Скидка 10% на офисную мебель.\nУсловия: Доставка бесплатно при заказе от 30,000 руб."
    elif message.text == "Благоустройство квартиры":
        response = "Дрим клининг: Комиссия риелтора 10% от суммы сделки.\nУслуги: Гениральная уборка, уборка послестроительная, косметическая уборка.\n\n" \
                   "Партнер 2: Скидка 10% на услуги по благоустройству.\nУсловия: Услуга доступна только в выходные.\n\n" \
                   "Партнер 3: Скидка 5% на услуги ландшафтного дизайна.\nУсловия: Предоставить документы на предыдущие заказы."
    elif message.text == "Назад":
        send_categories(message)
        return
    else:
        response = "Пожалуйста, выберите одну из предложенных категорий."

       # Отправляем ответ по выбранной категории
    bot.send_message(message.chat.id, response, reply_markup=markup)
    bot.register_next_step_handler(message, handle_back)

# Обработка команды, чтобы начать меню
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите 'Этажи Бонус' для получения скидок.")


@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_loyalty_card = types.KeyboardButton("Этажи Бонус")
    markup.add(btn_loyalty_card)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите опцию:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "заявка Этажи Бонус")
def loyalty_card_handler(message):
    send_partners(message)


def send_partners(message):
    # Здесь можно добавить список партнеров
    partners = ["Партнер 1", "Партнер 2", "Партнер 3"]  # Пример списка
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Кнопки для партнеров
    for partner in partners:
        markup.add(types.KeyboardButton(partner))

    btn_back = types.KeyboardButton("Назад")
    markup.add(btn_back)

    bot.send_message(message.chat.id, "Выберите партнера:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_partner_selection)


def handle_partner_selection(message):
    selected_partner = message.text  # Сохраняем выбранного партнера
    bot.send_message(message.chat.id, "Введите ваш код риелтора:")

    # Регистрация следующего шага
    bot.register_next_step_handler(message, lambda msg: handle_realtor_code(msg, selected_partner))


def handle_realtor_code(message, selected_partner):
    realtor_code = message.text  # Сохраняем код риелтора
    bot.send_message(message.chat.id, "Введите ФИО клиента:")

    # Регистрация следующего шага
    bot.register_next_step_handler(message, lambda msg: handle_client_name(msg, selected_partner, realtor_code))


def handle_client_name(message, selected_partner, realtor_code):
    client_name = message.text  # Сохраняем ФИО клиента
    bot.send_message(message.chat.id, "Введите номер телефона клиента:")

    # Регистрация следующего шага
    bot.register_next_step_handler(message,
                                   lambda msg: handle_client_phone(msg, selected_partner, realtor_code, client_name))


def handle_client_phone(message, selected_partner, realtor_code, client_name):
    client_phone = message.text  # Сохраняем номер телефона клиента
    bot.send_message(message.chat.id,
                     "Вы уверены, что хотите отправить заявку? (Ответьте 'да' для подтверждения или 'нет' для отмены)")

    # Храним информацию в контексте, чтобы отправить администратору позже
    bot.register_next_step_handler(message,
                                   lambda msg: confirm_request(msg, selected_partner, realtor_code, client_name,
                                                               client_phone))


def confirm_request(message, selected_partner, realtor_code, client_name, client_phone):
    if message.text.lower() == 'да':
        # Формируем сообщение для отправки администратору
        request_info = (f"Новая заявка Этажи Бонус:\n"
                        f"Партнер: {selected_partner}\n"
                        f"Код риелтора: {realtor_code}\n"
                        f"ФИО клиента: {client_name}\n"
                        f"Телефон клиента: {client_phone}")

        bot.send_message(ADMIN_CHAT_ID, request_info)
        bot.send_message(message.chat.id, "Ваша заявка успешно отправлена.")
    else:
        bot.send_message(message.chat.id, "Заявка отменена. Пожалуйста, начните процесс заново.")
        send_partners(message)

bot.polling(none_stop=True)
