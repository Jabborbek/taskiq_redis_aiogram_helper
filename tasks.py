import datetime

import taskiq_aiogram
from aiogram import Bot
from taskiq import TaskiqDepends
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker
from taskiq_redis import ListRedisScheduleSource

broker = ListQueueBroker("redis://localhost:6379/0")
redis_source = ListRedisScheduleSource("redis://localhost:6379/0")

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[redis_source],
)

taskiq_aiogram.init(
    broker,
    "loader:dp",
    "loader:bot",
)


@broker.task(task_name="my_task")
async def my_task(chat_id: int, bot: Bot = TaskiqDepends()):
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    await bot.send_message(chat_id, f"Task completed at: {now}")
