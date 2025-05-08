import os
import sys
from dataprocess import dataprocessing as hd

#from settings import *
import src.dataprocessing as dp
from src.webscrapping import MyBot
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def download_56():  
    with MyBot() as mybot:
        mybot.init_browser(
            headless=True,
            browser="chrome"
        )
        mybot.open(
            "https://sistema.ssw.inf.br/bin/ssw0422"
        )
        mybot.login()
        mybot.post_56()
        mybot.filtro_56()
        first_name, second_name = mybot.generate_56()
        mybot.download_56(first_name, second_name)    


def processamento():
    
    dp.processamento()
    
def to_db():
    
    table = dp.ler_arquivo()
    dp.to_db(table)    


if __name__=='__main__':
    download_56()
    processamento()
    to_db()
    