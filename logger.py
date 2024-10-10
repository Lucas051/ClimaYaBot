import logging

# Logger config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  

# Handler (utf-8 encode for emojis support)
file_handler = logging.FileHandler('bot.log', encoding='utf-8', errors='replace')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(file_handler)

logger.propagate = False
