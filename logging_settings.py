import logging
import sys

# networking logger
logging.addLevelName(5, 'network')

network_logger = logging.getLogger('')
network_logger.setLevel(5)

file_handler = logging.FileHandler('network_log.log', mode='w')
file_handler.setLevel('network')
network_logger.addHandler(file_handler)


# info logger
info_logger = logging.getLogger('Image Generation')
info_logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
stdout_handler.setFormatter(formatter)

info_logger.addHandler(stdout_handler)

info_logger.setLevel(logging.INFO)




