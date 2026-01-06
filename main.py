import asyncio
import logging
import sys

from aiogram import types
from aiogram.filters import Command, CommandObject

from loader import bot, dp
from tasks import broker
from tasks import my_task, redis_source
from config import CHAT_ID


@dp.startup()
async def on_startup():
    if not broker.is_worker_process:
        print(">>> SCHEDULER STARTED <<<")
        logging.info("Starting Taskiq broker")
        await broker.startup()
        logging.info("Bot started")
        await bot.send_message(chat_id=CHAT_ID, text="✅ Bot started")


@dp.shutdown()
async def on_shutdown():
    if not broker.is_worker_process:
        logging.info("Shutting down Taskiq broker")
        await broker.shutdown()
        logging.info("Bot stopped")
        await bot.send_message(chat_id=CHAT_ID, text="Bot stopped")


@dp.message(Command("task"))
async def task_handler(message: types.Message, command: CommandObject):
    cron = command.args
    print(f"Received cron: {cron}")
    # if cron is None:
    #     await message.answer("No cron supplied")
    #     return

    await my_task.schedule_by_cron(
        source=redis_source,
        cron="56 5 * * *",  # every hour at minute 56
        chat_id=message.chat.id,
    )

    await message.answer(
        "✅ Cron has been set\n"
        f"🕓 A task will be ran according to cron \"{cron}\""
    )


@dp.message(Command("clear"))
async def clear_schedules(message: types.Message):
    schedules = await redis_source.get_schedules()
    for schedule in schedules:
        await redis_source.delete_schedule(schedule.schedule_id)
    await message.answer("Scheduler's cleared")


async def main():
    logging.info("Bot polling started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())
