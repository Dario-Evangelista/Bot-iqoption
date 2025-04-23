from ast import Return
from decimal import ROUND_HALF_DOWN
from operator import length_hint
from os import stat
from statistics import mode
from subprocess import call
from iqoptionapi.stable_api import IQ_Option
from time import sleep
import time
from datetime import datetime
from functools import reduce

import threading
import sys
import logging
import requests
import time
import json
import os

token = None
group = None
admin = None

try:
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.json"))
    with open(config_path, 'r') as file:
        data = json.load(file)
        token = data.get('token')
except Exception as e:
    print(e)

try:
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.json"))
    with open(config_path, 'r') as file:
        data = json.load(file)
        admin = data.get('admin')
except Exception as e:
    print(e)

try:
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.json"))
    with open(config_path, 'r') as file:
        data = json.load(file)
        group = data.get('group')
except Exception as e:
    print(e)


class Bot():
    def __init__(self,msg) -> None:
        self.url = f"https://api.telegram.org/bot{token}/"
        self.msg = msg
        self.send_message(msg)
        requests.post(self.url + 'sendmessage', {'chat_id': f'{admin}','text': str('Bot-On')})

    def send_message(self, msg):
        if msg == '':
            None
        else:
            requests.post(self.url + 'sendmessage', {'chat_id': f'{admin}','text': str(msg)})

    def send_message_group(self, msg):
        if msg == '':
            None
        else:
            requests.post(self.url + 'sendmessage', {'chat_id': f'{group}','text': str(msg)})
    
    def send_message1(self, moeda):
        if self.msg == f"Moeda com volatividade acima de 50% {moeda}":
            requests.post(self.url + 'sendmessage', {'chat_id': f'{admin}','text': str(self.msg)})
            time.sleep(30)    

    def delete_updates(self,data):
        requests.get(self.url + 'getUpdates', {'offset': data['update_id'] + 1})
    
    def get_message(self,data,command, msg):
        if data['message']['text'] == command:
            requests.get(self.url + 'SendMessage', {'chat_id': data['message']['chat']['id'], 'text' : str(msg)})

    def send_markup(self, data,command,keyboard,msg):
        reply_markup = keyboard
        if data['message']['text'] == command:
            requests.post(self.url + 'sendMessage', {  'text': msg, 
                                                                    'chat_id': data['message']['chat']['id'], 
                                                                    'reply_markup': json.dumps(reply_markup), 
                                                                    'disable_web_page_preview': 'true'})

class Login():
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self.balance_type="PRACTICE"
        self.par = 'EURUSD-OTC'
        self.timeframe = 5
        self.valor = 100
        self.quantia_velas = 7
        self.linha_superior = 10
        self.linha_inferior = -10
        self.porcentagem_entrada = 45
        self.limite_porcentagem_entrada = 101 #tradamento de médias
        self.mudanca_entrada = 1
        self.vitorias=0
        self.derrota=0
        self.derrota_t=0 
        self.media_put = 0
        self.media_calls = 0
        self.contador = 0 #entrada
        self.limite_contador = 40
        self.medias = True
        self.xx = 0
        self.yy = 0
        self.limite_volatilidade = 35
        self.negativo_limite = 10
        self.porcentagem_entrada_toleranca = 10
        self.contador_t = 0 #tempo limite
        self.limite_tempo = 200
        self.pares = [{'moeda': 'EURUSD'}, {'moeda': 'EURGBP'}, {'moeda': 'EURJPY'}, {'moeda': 'GBPUSD'}, {'moeda': 'AUDUSD'}]
        self.login_iq()
        
    def login_iq (self):
        self.start = True
        while True:
            self.Iq = IQ_Option(self.username, self.password)
            self.Iq.connect()
            try:
                if self.Iq.check_connect():
                    print('Successfully logged in.')
                    self.run()
                    return self.Iq
                else:
                    print('Failed to log in. Retrying...')
            except Exception as e:
                print(f'An error occurred while trying to log in: {e}')
                time.sleep(10)  # Espera por 10 segundos antes de tentar reconectar
                continue

    def sma(self,candles, periodo):
        candles = candles[:periodo]
        length = len (candles)
        sum = reduce((lambda last, x: last + x), candles)
        sma =  sum / length
        return sma

    def prev(self,s, i):
        return s[abs(round(i))]

    def iff(self,se, verd, fals): 
        if se:
            return verd
        else:
            return fals

    def entrada(self,moeda, comando,time_comando):
            print(f"\n {datetime.now(). strftime('%H:%M:%S')} Abrindo operação self.a {comando.upper()}!, {moeda}")
            bot = Bot(f"\n {datetime.now(). strftime('%H:%M:%S')} Abrindo operação para {comando.upper()}!, {moeda}")  
            bot.send_message_group(f"abrindo operação:{moeda,comando} ")              
            status, id = self.Iq.buy(self.valor, self.par, comando, time_comando)
            if status:
                self.total_jogada +=1
                status, lucro = self.Iq.check_win_v4(id)
                if lucro >0 and status == 'win':
                    self.vitorias+=1
                    print(f"\n LUCRO DE {lucro}\n", end='\r')
                    Bot(f"\n LUCRO DE {lucro}\n, Total de Vitorias {self.vitorias}, Total de Derrotas {self.derrota}")
                elif lucro ==0:
                    print("\n EMPATE!", end='\r')
                    self.derrota += 1
                    self.derrota_t +=1
                    Bot(f"\n EMPATE!, Total de Vitorias {self.vitorias}, Total de Derrotas {self.derrota}")
                else:
                    print (f"\n loss,{lucro}\n", end='\r')
                    self.derrota += 1
                    self.derrota_t +=1
                    Bot(f"\n loss,{lucro}\n, Total de Vitorias {self.vitorias}, Total de Derrotas {self.derrota}")

            else: 
                print(f"\n mensagem: {id}\n\n")
                if self.OTC:
                    self.pares = [{'moeda': 'EURUSD-OTC'}, {'moeda': 'EURGBP-OTC'}, {'moeda': 'EURJPY-OTC'}, {'moeda': 'GBPUSD-OTC'}]
                    self.OTC = False
                if self.OTC:
                    self.pares = [{'moeda': 'EURUSD'}, {'moeda': 'EURGBP'}, {'moeda': 'EURJPY'}, {'moeda': 'GBPUSD'}, {'moeda': 'AUDUSD'}]
                    self.OTC = True
                if id ==" Time for purchasing options is over, please try again later.":
                    return None
                Bot(f"\n mensagem: {id}\n\n")
                Bot(f"Troca para OTC")
                
                return self.Iq.change_balance(self.balance_type)

    def limpar_terminal(self):
        import os
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def calculo_media(self,moeda, put, calls):
        if self.medias == False:
            print("Tempo:", self.contador_t,end='\n')
            self.contador_t +=1

        if self.contador_t == self.limite_tempo:
            self.medias = True
            self.contador_t = 0
            
        if self.medias:
            if put:
                self.media_put += 1
                self.contador += 1
                print('Entrada:',self.porcentagem_entrada, 'Contador:',self.contador, 'Moeda:',moeda,end='\n')

            if calls:
                self.media_calls += 1
                self.contador += 1
                print('Entrada:',self.porcentagem_entrada, 'Contador:',self.contador, 'Moeda:',moeda,end='\n')
            if self.contador == self.limite_contador:
                x = self.media_put / self.limite_contador
                y = self.media_calls / self.limite_contador
                self.contador = 0

                if x >= y:
                    x_tradado = round(abs(x - self.xx + self.lrange))
                    self.porcentagem_entrada = x_tradado
                    self.medias=False
                    self.media_put = 0
                    self.media_calls = 0
                    self.contador = 0
                    if self.porcentagem_entrada >= 101:
                        self.porcentagem_entrada = 100
                        self.medias = True
                        self.contador = 0
                        self.media_put = 0
                        self.media_calls = 0
                        
                    print('Entrada:',self.porcentagem_entrada, 'Contador:',self.contador, 'Moeda:',moeda,end='\n')
                else:
                    y_tratado = round(abs(y - self.yy + self.lrange))
                    self.porcentagem_entrada = y_tratado
                    self.medias=False
                    self.media_put = 0
                    self.media_calls = 0
                    self.contador = 0
                    if self.porcentagem_entrada >= self.limite_porcentagem_entrada:
                        self.porcentagem_entrada = 100
                        self.medias = True
                        self.contador = 0
                        self.media_put = 0
                        self.media_calls = 0
                    print('Entrada',self.porcentagem_entrada,'calls', self.lrange,end='\n')

        if self.porcentagem_entrada == 0 or self.porcentagem_entrada <= 10:
            self.porcentagem_entrada += self.mudanca_entrada
                
    def volatil(self, moeda, put, calls, color):
        negativo = 0 
        positivo = 0
        resultado_negativo = 0
        resultado_positivo = 0
        entrou = ''
        
        try:
            i_put = put
            i_call = calls
            n_put = abs(i_put)
            n_call = abs(i_call)

        except Exception as e:
            print(e)
            Bot(e)
        try:
            if isinstance(n_put, (int, float)) and isinstance(n_call, (int, float)):
                if n_put >= self.limite_volatilidade or n_call >= self.limite_volatilidade:
                    print(f"Volatilidade alta detectada para {moeda} - put: {n_put}% | call: {n_call}%")
                    Bot(f"Volatilidade alta detectada para {moeda} - put: {n_put}% | call: {n_call}%")
                    if n_put >= self.limite_volatilidade and color == "green" and entrou != "put" or put <= self.porcentagem_entrada_toleranca and color == "green" and entrou != "put":
                            entrou = "put"
                            self.par = moeda
                            self.medias = True
                            self.entrada(moeda,"put", round(self.timeframe / 60))
                            
                    elif n_call >= self.limite_volatilidade and color == "red" and entrou != "call" or n_call >= self.limite_volatilidade and color == "red" and entrou != "call":
                        entrou = "call"
                        self.par = moeda
                        self.medias = True
                        self.entrada(moeda,"call", round(self.timeframe / 60))

                if n_put >= 110 or n_call >= 110:
                    self.moedas_volatio = moeda
                    Bot('').send_message1(f"Moeda com volatividade acima de 110% {moeda}")

                if n_put >= 110 or n_call >= 110:
                    self.moedas_volatio = moeda
                    self.linha_superior =15
                    self.linha_inferior  =-15
                    self.quantia_velas = 10
                    self.divisor -= 1
                    self.vara = 9
                    Bot('').send_message1(f"Moeda com volatividade acima de 110% {moeda}")    

                elif n_put >= 101 and n_call >= 101:
                    self.linha_superior -= 1
                    self.linha_inferior  += 1
                    Bot(f"Alteração das linha limite, inferior{self.linha_inferior}, superior {self.linha_superior}")

                if self.linha_inferior == -5 and self.linha_superior == 5:
                    self.linha_superior = 10
                    self.linha_inferior  = -10
                    Bot(f"Restauração das linha limite, inferior{self.linha_inferior}, superior {self.linha_superior}")

                if self.derrota == 8:
                    self.linha_superior += 2
                    self.linha_inferior  -= 2
                    Bot(f"Calculando, inferior{self.linha_inferior}, superior {self.linha_superior}")
                
                if self.total_jogada >= 10:
                    resultado_negativo = self.total_jogada - self.derrota
                    resultado_positivo = self.total_jogada - self.vitorias
                    Bot(f"Resultados, Derrota{resultado_negativo}, Positivo {resultado_positivo}")

                if self.divisor <= 2:
                    self.divisor = 5 
                    Bot(f"Restaurando divisor {self.divisor}")

                    try:
                        negativo = (self.derrota/self.total_jogada)*100
                        Bot(f"negativo {negativo}%")
                    except Exception as e:
                        print(e)
                        pass

                    try:
                        positivo = (self.vitorias/self.total_jogada)*100
                        Bot(f"positivo {positivo}%")
                    except Exception as e:
                        print(e)
                        pass
                if resultado_negativo >1 or resultado_positivo > 1:
                    print(f"{resultado_negativo}, {negativo}%, {resultado_positivo}, {positivo}%")
                    Bot(f"{resultado_negativo}, {negativo}%, {resultado_positivo}, {positivo}%")

                if positivo == 75:
                    self.vara = self.vara

                if negativo >= self.negativo_limite:
                    self.linha_superior += 2
                    self.linha_inferior  += 2
                    self.quantia_velas += 2
                    self.divisor -= 1
                    self.vara = 5
                    self.n +=10
                    Bot(f"modificando: negativos {self.linha_superior}, {self.linha_inferior}, {self.quantia_velas}, {self.divisor}, {self.vara}")

                if n_put >= 110 or n_call >= 100:
                    self.moedas_volatio = moeda
                    Bot('').send_message1(f"Moeda com volatividade acima de 50% {moeda}")
            else:
                print("Variáveis put e call não contêm números válidos.")
        except Exception as e:
            print(e)
            Bot(e)
    
    def run(self):    
        try:
            entrou=''

            for par in self.pares:
                moeda = par['moeda']
                print(f"Iniciando análise para o par: {moeda}")
                Bot(f"Iniciando análise para o par: {moeda}")
                self.Iq.start_candles_stream(moeda, self.timeframe, self.quantia_velas)
                
            while True:
                    for par in self.pares:
                        moeda = par['moeda']
                        _= self.Iq.get_realtime_candles(moeda, self.timeframe).copy()
                    
                        open = [_[x]['open'] for x in _]
                        open.reverse()
                    
                        close = [_[x]['close'] for x in _]
                        close.reverse()

                        high = [_[x]['max'] for x in _]
                        high.reverse()

                        low = [_[x]['min'] for x in _]
                        low.reverse()
                        
                        if self.quantia_velas > 5:
                            varp = max(1, round(self.quantia_velas / 50)) 
                            ranges = []

                            for i in range(10): 
                                try:
                                    high_sorted = sorted(high[varp:], reverse=True)
                                    low_sorted = sorted(low[varp:])
                                    
                                    high_val = self.prev(high_sorted, -varp * i)
                                    low_val = self.prev(low_sorted, -varp * i)
                                    range_val = high_val - low_val

                                    if range_val == 0 and varp == 1:
                                        close_diff = abs(self.prev(close, -varp * i) - self.prev(close, -varp * (i + 1)))
                                        ranges.append(close_diff)
                                    else:
                                        ranges.append(range_val)
                                except IndexError:
                                    continue  

                            if ranges:
                                self.lrange = (sum(ranges) / len(ranges)) * 0.2
                            else:
                                self.lrange = 1  
                        else:
                            cdelta = [abs(x - self.prev(close, -5)) for x in close]
                            var0 = self.iff( (cdelta[0] > (high[0])) or (high[0]== low[0]), cdelta, [high[x] - low [x] for x in range (len(high))])
                            self.lrange = self.sma (var0, 5) * .2
                        
                        
                        mba = self.sma([ (high[x] + low[x]) /2 for x in range(len(high))], self.quantia_velas)
                        vclose = (close[0] -mba) / self.lrange
                        color = open[0] > close [0] and 'red' or 'green'
                        try:
                            put = round( (vclose / self.linha_superior) * 100,2)
                            calls = round( (vclose / self.linha_inferior) * 100,2)    
                        except:
                            put = 0
                        print(f"\n put: {put}% | CALL {calls}%", end='\n')
                        
                        
                        self.calculo_media(moeda,put,calls)
                        self.volatil(moeda, put, calls, color)
                        print('Entrada:',self.porcentagem_entrada,end='\n')
                        time.sleep(0.5)
                        
                        if put >= self.porcentagem_entrada and color == "green" and entrou != "put" and put <= self.porcentagem_entrada_toleranca and color == "green" and entrou != "put":
                            entrou = "put"
                            self.par = moeda
                            self.medias = True
                            self.entrada(moeda,"put", round(self.timeframe / 60))
                            
                        elif calls >= self.porcentagem_entrada and color == "red" and entrou != "call" and calls <= self.porcentagem_entrada_toleranca and color == "red" and entrou != "call":
                            entrou = "call"
                            self.par = moeda
                            self.medias = True
                            self.entrada(moeda,"call", round(self.timeframe / 60))


        except Exception as e:
            print('Erro: ', e)
            check, reson = self.Iq.check_connect()
            if check:
                print('Reconectado')
            else:
                print('Erro 404')



