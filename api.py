import datetime
from distutils.debug import DEBUG
from distutils.log import ERROR
import json
import logging
from plistlib import UID
from unittest import result
import uuid
import requests
import os
from configparser import ConfigParser
import time
from datetime import date, datetime, time
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from logging import Logger
import dateutil

#logging.basicConfig(level=logging.INFO)
#logging.getLogger('apscheduler').setLevel(logging.DEBUG)
#logger=Logger("Bruno")
sched = BlockingScheduler()

class Pmclient(object):
    
    __username = None
    __password = None
    __uuid = None
    __session = None
    now = datetime.now()
    data_atual = now.strftime("%m/%d/%Y, %H:%M:%S")
    
    
    def __init__(self):
        
        self.__username = os.getenv("PMUSERNAME", "")
        self.__password = os.getenv("PMPASSWORD", "")
        self.__address = os.getenv("address", "R. do Rocio, 220 - Vila Olimpia, São Paulo - SP, 04552-000, Brasil")
        self.__latitude = os.getenv("latitude", "-23.593910069905398")
        self.__longitude = os.getenv("longitude", "-46.68620730511535")
        self.__uuid = str(uuid.uuid1())
        self.__session = requests.Session()
        self.BASE_URL = "https://api.pontomais.com.br"
        self.login_endpoint = f"{self.BASE_URL}/api/auth/sign_in"
        self.register_endpoint = f"{self.BASE_URL}/api/time_cards/register"
        self.workday_url = f"{self.BASE_URL}/api/time_card_control/current/work_days/"

    def __get_header(self) -> dict:
        return {
            "Host": self.BASE_URL.replace("https://", ""),
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://app.pontomaisweb.com.br",
            "Referer": "https://app.pontomaisweb.com.br//",
            "uid": self.__username,
            "uuid": self.__uuid,
            "access-token": self.__token,
            "token-type": "Bearer",
            "expiry": self.__expiry,
            "Api-Version": "2",
            "client": self.__client,
            "content-type": "application/json",
        }
        
    def login(self) -> bool:

        token = None
        client = None
        expiry = None
        authenticated = False

        auth_url =  self.login_endpoint
        credentials = {"login": self.__username, "password": self.__password}
        response = self.__session.post(auth_url, data=credentials)
        print(f"iniciando login: {response}")
        if response.content and response.status_code == 201:
            authenticated = True
            response_json = response.json()
            token = response_json.get("token")
            client = response_json.get("client_id")
            expiry = response_json.get("expiry")
            self.__token = token
            self.__client = client
            self.__expiry = expiry
            print(f"autenticado: {response_json}")
        

        print(f"login: {authenticated}")
        return authenticated
    
    def register(self) -> dict:
        
        payload = {
            "time_card": {
                "latitude": self.__latitude,
                "longitude": self.__longitude,
                "address": self.__address,
                "reference_id": None,
                "original_latitude": self.__latitude,
                "original_longitude": self.__longitude,
                "original_address": self.__address,
                "location_edited": True,
            },
            "_path": "/meu_ponto/registro_de_ponto",
            "_device": {
                "browser": {
                    "name": "Firefox",
                    "version": "86.0",
                    "versionSearchString": "Firefox",
                },
            },
            "_appVersion": "0.10.32",
        }
        print(f"fazendo registro: {payload}")
        response = self.__session.post(
            self.register_endpoint, headers=self.__get_header(), data=json.dumps(payload)
        )
        print(f"Registrando Resposta: {response}")
        return response.json()

    
    def handle_reg(self):
        
        try:
            x = Pmclient()
            auth = x.login()
        except Exception as error:
            print(f"<error de login>{error}</error de login>\n")
            while auth == False:
                print("tentando login novamente...")
                auth = x.login()    
            return
      
        if auth:
            confirmed = True
            if confirmed:
                response = x.register()
                if "success" in response:
                    print("<info>Registrado!</info>")
                    print(f"Ip: {response['meta']['ip']}")
                    print(f"Receipt: {response['receipt']}\n")
            return

        print("<error>Checa esse Login Porra!</error>\n")
    
    def note(self, data: datetime):
        fi = open("./note.txt", "a")
        fi.write(f"Registro de ponto efetuado em {data}\n")
        fi.close()

x = Pmclient()
print(f"--------- Login ----------- : {x.login()}")

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7, minute=45, jitter=900)
def scheduled_job():         
    print(f'Ponto de almoço as {datetime.now()}')
    x.handle_reg()
    x.note(f"{datetime.now()}")
    print("-------------------------------------")
    
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=12, minute=15, jitter=900)
def scheduled_job():  
    print(f'Ponto de almoço as {datetime.now()}')
    x.handle_reg()
    x.note(f"{datetime.now()}")
    print("-------------------------------------")

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=15, jitter=900)
def scheduled_job():  
    print(f'Ponto de almoço as {datetime.now()}'),
    x.handle_reg()
    x.note(f"{datetime.now()}")
    print("-------------------------------------")
    
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=18, minute=15, jitter=900)
def scheduled_job():
    print(f'Ponto de saida as {datetime.now()}')
    x.handle_reg()
    x.note(f"{datetime.now()}")
    print("-------------------------------------")


sched.start()
