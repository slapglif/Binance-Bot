import logging
from concurrent.futures import ThreadPoolExecutor
from config import Config as config
from app.bot.runner import PumpDumpBot

logging.basicConfig(filename='logs/run.log', encoding='utf-8', level=logging.DEBUG)

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        bot = PumpDumpBot()
        future = executor.map(bot.run_loop, config.symbols)
        for result in future:
            logging.info(result)
