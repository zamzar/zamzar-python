import logging

from zamzar import ZamzarClient

# The Zamzar Python client uses `urllib3` for HTTP requests
# To log HTTP requests, configure a `urllib3` logger, as shown below

# Configure logging as needed. Here we configure a simple console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the logging level for the console handler
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Enable logging for urllib3 to see HTTP requests
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.DEBUG)

# Make a request to the Zamzar API
zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")
zamzar.account.get()
