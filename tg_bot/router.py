from aiogram.fsm.context import FSMContext

from keyboard import main_menu, queue, admin, start
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from defs import get_timetable, check_lesson, add_queue, add_person_to_queue, fetch_queues


class Form(StatesGroup):
    laba_input_waiting = State()
    laba_queueadd_waiting = State()


router = Router()

#start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Нажимая кнопку <b>«Приступить»</b> ты соглашаешься с <a href='https://u.to/H_XuIA '>условиями пользования</a>.",
        reply_markup=start(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

#main menu window
@router.callback_query(F.data == "back_to_main")
async def show_queue_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выберите интересующий пункт меню:",
        reply_markup=main_menu(),
        )

#контакт старосты, кнопка "написать старосте"
@router.callback_query(F.data == "andrew")
async def show_queue_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Контакт: @kolbje",
        reply_markup=admin()
    )

#schedule view
@router.callback_query(F.data == "show_schedule")
async def show_schedule_menu(callback: CallbackQuery):
    timetable = get_timetable()
    print(type(timetable))
    result_message = "Расписание:\n"
    for item in timetable:
        print(type(item))
        result_message += (f"День: {item['day_of_week']}\n"
                           f"Тип занятия: {item['lesson_type_abbrev']}\n"
                           f"Предмет: {item['subject']}\n"
                           f"Подгруппа: {item['numsubgroup']}\n"
                           f"Время начала: {item['start_time']}\n\n")
    await callback.message.edit_text(
        text = result_message,
        reply_markup = admin()
    )
#queue view
@router.callback_query(F.data == "show_exist_queue")
async def show_queue(callback:CallbackQuery):
    queues= fetch_queues()
    print(queues)
    is_recording = False
    result_message = "Имеющиеся очереди:\n"
    for item in queues:
        if 'table_name' in item:
            # Если встречаем новую таблицу, сбрасываем флаг
            result_message += f"\nПредмет: {item['table_name']}\n"  # Выводим название предмета
            is_recording = True  # Начинаем запись данных
        elif is_recording:
            # Если находимся в записи, добавляем данные в результат
            result_message += (f"Позиция: {item['id']}\n"
                f"Ник занявшего: @{item['username']}\n")


    await callback.message.edit_text(
        text=result_message,
        reply_markup=admin()
    )
#меню кнопки "редактировать очередь"
@router.callback_query(F.data == "queue")
async def show_queue_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите интересующий пункт:",
        reply_markup=queue(),
        )

#добавление очереди в бд
@router.callback_query(F.data == "add_queue")
async def add_queue_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите название предмета и номер лабы по счету(чувствителен к регистру)", reply_markup = admin()
    )
    await state.set_state(Form.laba_input_waiting)
#продолжение функции добавления в бд
@router.message(Form.laba_input_waiting)
async def input_laby(message: Message, state: FSMContext) -> None:
    words = message.text.split()
    if len(words) == 2:
        lesson, num = words
        checker = check_lesson(lesson)
        if checker:
            temp_check = add_queue(message.text)
            if temp_check == "200":
                await message.reply("Очередь успешно создана!", reply_markup = admin())
                await state.clear()
            else:
                await message.reply("Очередь уже существует, записывайтесь:)", reply_markup = admin())
        else:
            await message.reply("Предмет с таким названием не найден", reply_markup = admin())
    else:
        await message.reply("Пожалуйста, введите ровно два слова через пробел.", reply_markup = admin())

#запись в очередь
@router.callback_query(F.data == "add_to_queue")
async def add_to_queue(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите название предмета, номер лабы и позицию в очереди", reply_markup=admin()
    )
    await state.set_state(Form.laba_queueadd_waiting)
#continue
@router.message(Form.laba_queueadd_waiting)
async def input_to_queue(message: Message) -> None:
    words = message.text.split()
    if len(words) == 3:
        lesson, num, pos = words
        checker = check_lesson(lesson)
        if checker:
            second_check = add_person_to_queue(lesson + " " + num, pos, message.from_user.username)
            if second_check == "200":
                await message.reply(f"Вы добавлены в очередь на {pos} позицию.", reply_markup=admin())
            elif second_check == "Alr in queue":
                await message.reply("Вы уже заняли очередь", reply_markup=admin())
            elif second_check == "place_holded":
                await message.reply("Место занято, выберите другое(введите то же сообщение но измените позицию).", reply_markup=admin())
        else:
            await message.reply("Предмет с таким названием не найден", reply_markup=admin())
    else:
        await message.reply("Пожалуйста, введите ровно три слова через пробел.", reply_markup=admin())





#trash
@router.message()
async def trash(message: Message) -> None:
    await message.answer("Неуместно в данном контексте. Вы точно имели ввиду рабочую команду"
                         " или в процессе редактирования очереди?")
