from ast import Return
from decimal import ROUND_HALF_DOWN
from distutils.command.check import check
from operator import length_hint
from os import stat
from statistics import mode
from subprocess import call
from iqoptionapi.stable_api import IQ_Option
from time import time
import time
from datetime import datetime
from functools import reduce

import threading
import sys
import logging
import requests
import time
import json

class Bot():
    def __init__(self,msg) -> None:
        self.url = "https://api.telegram.org/bot{key}/"
        self.msg = msg
        self.send_message(msg)
        requests.post(self.url + 'sendmessage', {'chat_id': '-1002098433488','text': str('Bot-On')})
        

    def send_message(self, msg):
        if msg == '':
            None
        else:
            requests.post(self.url + 'sendmessage', {'chat_id': '-1002098433488','text': str(msg)})
    
    def send_message1(self, moeda):
        if self.msg == f"Moeda com volatividade acima de 50% {moeda}":
            requests.post(self.url + 'sendmessage', {'chat_id': '-1002098433488','text': str(self.msg)})
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
        self.divisor = 5

        self.total_jogada=0
        self.vitorias=0
        self.derrota=0
        self.derrota_t=0 
        self.media_put = 0
        self.media_calls = 0
        self.contador = 0
        self.medias = True
        self.xx = 0
        self.yy = 0
        self.limite_volatilidade = 35
        self.negativo_limite = 10
        self.porcentagem_entrada_toleranca = 10
        self.contador_t = 0
        self.pares = [{'moeda': 'EURUSD'},{'moeda': 'EURGBP'}]
        self.login_iq()
        
        pass

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
            Bot(f"\n {datetime.now(). strftime('%H:%M:%S')} Abrindo operação para {comando.upper()}!, {moeda}")                
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
                """if self.OTC:
                    self.pares = [{'moeda': 'EURUSD-OTC'}, {'moeda': 'EURGBP-OTC'}, {'moeda': 'EURJPY-OTC'}, {'moeda': 'GBPUSD-OTC'}]
                    self.OTC = False
                if self.OTC:
                    self.pares = [{'moeda': 'EURUSD'}, {'moeda': 'EURGBP'}, {'moeda': 'EURJPY'}, {'moeda': 'GBPUSD'}, {'moeda': 'AUDUSD'}]
                    self.OTC = True
                if id ==" Time for purchasing options is over, please try again later.":
                    return """
                Bot(f"\n mensagem: {id}\n\n")
                Bot(f"Troca para OTC")
                
                return self.Iq.change_balance(self.balance_type)

    def limpar_terminal(self):
        import os
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def start_user_input_thread(self):
        def user_input():
            while True:
                new_linha_superior = input("\nDigite o novo valor para self.linha_superior (ou deixe em branco para manter o atual): \n\n")
                if new_linha_superior:
                    self.linha_superior = float(new_linha_superior)

                new_linha_inferior = input("\nDigite o novo valor para self.linha_inferior (ou deixe em branco para manter o atual): \n\n")
                if new_linha_inferior:
                    self.linha_inferior = float(new_linha_inferior)

                new_valor = input("\nDigite o novo valor para velas (ou deixe em branco para manter o atual):\n\n ")
                if new_valor:
                    self.quantia_velas = float(new_valor)

                new_entrada = input("\nDigite o novo valor para entrada (ou deixe em branco para manter o atual):\n\n ")
                if new_entrada:
                    self.porcentagem_entrada = float(new_entrada)

        input_thread = threading.Thread(target=user_input)
        input_thread.daemon = True
        input_thread.start()
    
    def calculo_media(self,moeda, put, calls):
        if self.medias == False:
            print("Tempo:", self.contador_t,end='\n')
            self.contador_t +=1

        if self.contador_t == 200:
            self.medias = True
            self.contador_t = 0
            
        if self.medias:
            if put:
                self.media_put += put
                self.media_calls += calls
                self.contador += 1
                print('Entrada:',self.porcentagem_entrada, 'Contador:',self.contador, 'Moeda:',moeda,end='\n')
            if self.contador == 40:
                x = self.media_put / 40
                y = self.media_calls / 40
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
                    if self.porcentagem_entrada >= 101:
                        self.porcentagem_entrada = 100
                        self.medias = True
                        self.contador = 0
                        self.media_put = 0
                        self.media_calls = 0
                    print('Entrada',self.porcentagem_entrada,'calls', self.lrange,end='\n')

        if self.porcentagem_entrada == 0 or self.porcentagem_entrada <= 10:
            self.porcentagem_entrada += 15


                
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
                            if moeda == "EURUSD":
                                self.par="EURUSD"
                        
                            elif moeda == "EURGBP":
                                self.par="EURGBP"

                            elif moeda == "EURJPY":
                                self.par="EURJPY"

                            elif moeda == "GBPUSD":
                                self.par="GBPUSD"

                            elif moeda == "AUDUSD":
                                self.par="AUDUSD"

                            elif moeda == "EURUSD-OTC":
                                self.par="EURUSD-OTC"
                        
                            elif moeda == "EURGBP-OTC":
                                self.par="EURGBP-OTC"

                            elif moeda == "EURJPY-OTC":
                                self.par="EURJPY-OTC"
                            self.medias = True
                            self.entrada(moeda,"put", round(self.timeframe / 60))
                            
                    elif n_call >= self.limite_volatilidade and color == "red" and entrou != "call" or n_call >= self.limite_volatilidade and color == "red" and entrou != "call":
                        entrou = "call"
                        if moeda == "EURUSD":
                            self.par="EURUSD"
                    
                        elif moeda == "EURGBP":
                            self.par="EURGBP"

                        elif moeda == "EURJPY":
                            self.par="EURJPY"

                        elif moeda == "GBPUSD":
                            self.par="GBPUSD"

                        elif moeda == "AUDUSD":
                            self.par="AUDUSD"

                        elif moeda == "EURUSD-OTC":
                            self.par="EURUSD-OTC"
                    
                        elif moeda == "EURGBP-OTC":
                            self.par="EURGBP-OTC"

                        elif moeda == "EURJPY-OTC":
                            self.par="EURJPY-OTC"

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
                            varp = round(self.quantia_velas/50)
                            vara = sorted(high[varp:], reverse=True)[0] = sorted(low[varp:]) [0]
                            varrl = self.iff(vara == 0 and varp == 1, abs(close[0] - self.prev(close, -varp)), -varp)
                            varb = self.prev( sorted(high[varp:], reverse=True), -varp+1) -self.prev(sorted(low[varp:]), -varp)
                            varr2 = self.iff( varb == 0 and varp ==1,abs(self.prev(close, -varp) - self.prev(close, -varp*2) ), varb)
                            varc =  self.prev(sorted(high[varp:], reverse=True), -varp*2) -self.prev(sorted(low[varp:]), -varp*2)
                            varr3 = self.iff(varc == 0 and varp == 1, abs(self.prev(close, -varp*2) - self.prev(close, -varp*3)), varc)
                            vard = self.prev(sorted(high[varp:], reverse=True), -varp*3) - self.prev(sorted(low[varp:]), -varp*3)
                            varr4 = self.iff(vard == 0 and varp == 1, abs(self.prev(close, -varp*3) - self.prev(close, -varp*4)), vard)
                            vare = self.prev(sorted(high[varp:], reverse=True), -varp*4) -self.prev(sorted(low[varp:]), -varp*4)
                            varr5 = self.iff(vare== 0 and varp == 1, abs(self.prev(close, -varp*4) - self.prev(close, -varp*5)), vare)
                            vare5 = self.prev(sorted(high[varp:], reverse=True), -varp*5) -self.prev(sorted(low[varp:]), -varp*5)
                            varr6 = self.iff(vare5== 0 and varp == 1, abs(self.prev(close, -varp*5) - self.prev(close, -varp*6)), vare5)
                            vare6 = self.prev(sorted(high[varp:], reverse=True), -varp*6) -self.prev(sorted(low[varp:]), -varp*6)
                            varr7 = self.iff(vare6== 0 and varp == 1, abs(self.prev(close, -varp*6) - self.prev(close, -varp*7)), vare6)
                            vare7 = self.prev(sorted(high[varp:], reverse=True), -varp*7) -self.prev(sorted(low[varp:]), -varp*7)
                            varr8 = self.iff(vare7== 0 and varp == 1, abs(self.prev(close, -varp*7) - self.prev(close, -varp*8)), vare7)
                            vare8 = self.prev(sorted(high[varp:], reverse=True), -varp*8) -self.prev(sorted(low[varp:]), -varp*8)
                            varr9 = self.iff(vare8== 0 and varp == 1, abs(self.prev(close, -varp*8) - self.prev(close, -varp*9)), vare8)
                            vare9 = self.prev(sorted(high[varp:], reverse=True), -varp*9) -self.prev(sorted(low[varp:]), -varp*9)
                            varr10 = self.iff(vare9== 0 and varp == 1, abs(self.prev(close, -varp*10) - self.prev(close, -varp*10)), vare9)
                            self.lrange = ((varrl + varr2 + varr3 + varr4 + varr5 + varr6 + varr7 + varr8 + varr9 + varr10)/ 10) * .2
                        else:
                            cdelta = [abs(x - self.prev(close, -5)) for x in close]
                            var0 = self.iff( (cdelta[0] > (high[0])) or (high[0]== low[0]), cdelta, [high[x] - low [x] for x in range (len(high))])
                            self.lrange = self.sma (var0, 5) * .2
                        
                        
                        mba = self.sma([ (high[x] + low[x]) /2 for x in range(len(high))], self.quantia_velas)
                        vclose = (close[0] -mba) / self.lrange
                        color = open[0] > close [0] and 'red' or 'green'

                        """print(f'{varp}',end='\n')
                        print(f'{vara}',end='\n')
                        print(f'{varrl}',end='\n')
                        print(f'{varb}',end='\n')
                        print(f'{varr2}',end='\n')
                        print(f'{varc}',end='\n')
                        print(f'{varr3}',end='\n')
                        print(f'{vard}',end='\n')
                        print(f'{varr4}',end='\n')
                        print(f'{vare}',end='\n')"""
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
                            if moeda == "EURUSD":
                                self.par="EURUSD"
                        
                            elif moeda == "EURGBP":
                                self.par="EURGBP"

                            elif moeda == "EURJPY":
                                self.par="EURJPY"

                            elif moeda == "GBPUSD":
                                self.par="GBPUSD"

                            elif moeda == "AUDUSD":
                                self.par="AUDUSD"

                            elif moeda == "EURUSD-OTC":
                                self.par="EURUSD-OTC"
                        
                            elif moeda == "EURGBP-OTC":
                                self.par="EURGBP-OTC"

                            elif moeda == "EURJPY-OTC":
                                self.par="EURJPY-OTC"
                            self.medias = True
                            self.entrada(moeda,"put", round(self.timeframe / 60))
                            
                        elif calls >= self.porcentagem_entrada and color == "red" and entrou != "call" and calls <= self.porcentagem_entrada_toleranca and color == "red" and entrou != "call":
                            entrou = "call"
                            if moeda == "EURUSD":
                                self.par="EURUSD"
                        
                            elif moeda == "EURGBP":
                                self.par="EURGBP"

                            elif moeda == "EURJPY":
                                self.par="EURJPY"

                            elif moeda == "GBPUSD":
                                self.par="GBPUSD"

                            elif moeda == "AUDUSD":
                                self.par="AUDUSD"

                            elif moeda == "EURUSD-OTC":
                                self.par="EURUSD-OTC"
                        
                            elif moeda == "EURGBP-OTC":
                                self.par="EURGBP-OTC"

                            elif moeda == "EURJPY-OTC":
                                self.par="EURJPY-OTC"

                            self.medias = True
                            self.entrada(moeda,"call", round(self.timeframe / 60))


        except Exception as e:
            print('Erro: ', e)
            check, reson = self.Iq.check_connect()
            if check:
                print('Reconectado')
            else:
                print('Erro 404')

        


Login()
