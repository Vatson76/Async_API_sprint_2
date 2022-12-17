import asyncio
import logging

from etl.etl_loader import ESLoader
from etl.helpers import redis

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


async def main():
    await ESLoader().load_data()


if __name__ == '__main__':
    logger.info("Начало работы программы по переносу измененных данных из es в postgre")
    loop = asyncio.get_event_loop()
    errors_count = 0
    while True:
        try:
            logger.info("Запуск процесса переноса данных из es в postgre")
            loop.run_until_complete(main())
            logger.info("Перенос выполнен")
            loop.run_until_complete(asyncio.sleep(300))
        except Exception as e:
            errors_count += 1
            if errors_count == 5:
                logger.exception("Достигнуто критическое количество ошибок, сервис умирает ;(")
                loop.close()
                redis.close()
                break
            else:
                logger.exception("Во время работы сервиса возникла ошибка")
                loop.run_until_complete(asyncio.sleep(120))
