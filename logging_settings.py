import logging
import sys

# network logger
network_logger = logging.getLogger('request-logger')

file_handler = logging.FileHandler('network-log.log', mode='w')

network_formatter = logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S')
file_handler.setFormatter(network_formatter)

network_logger.addHandler(file_handler)

network_logger.setLevel(logging.INFO)


# info logger
info_logger = logging.getLogger('Image Generation')

stdout_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
stdout_handler.setFormatter(formatter)

info_logger.addHandler(stdout_handler)

info_logger.setLevel(logging.INFO)




