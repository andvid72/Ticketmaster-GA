import urllib3, threading
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from GA_telegram import *
from GA_main import *
#*********************************************** 
#Launch TelegramListener
threading.Thread(target=TelegramListener).start()
# threading.Thread(target=Scraper, args=(str(x))).start()

#Launch Main
threading.Thread(target=Scraper).start()


