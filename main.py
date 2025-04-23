import json
import time
import requests
from src import core
from src.ultis import admin, id_group
local = "config.json"

start = input("Gostaria de configurar o bot com Id? (s/n): ").strip().lower()

if start == "s":
    print("antes de iniciar adicione o token do bot em config.json")
    print("1. Vá até o bot e envie o comando `admin_bot` para definir o usuário administrador.")
    print("2. Para configurar o grupo, entre no grupo e envie `adm_grup`.")
    print("Vamos iniciar o bot...")
else:
    print("Bot será iniciado sem configurações iniciais.")

with open(local, "r") as file:
    data = json.load(file)
    token = data["token"]
    url = f"https://api.telegram.org/bot{token}/"

def get_update(data):
    requests.get(url + 'getUpdates', data={'offset': data['update_id'] + 1})

def get_message(chat_id, msg):
    requests.post(url + 'sendMessage', data={'chat_id': chat_id, 'text': str(msg)})

while start == "s":
    try:
        updates = ''
        while not isinstance(updates, dict) or 'result' not in updates:
            try:
                response = requests.get(url + 'getUpdates')
                updates = response.json()
            except Exception as e:
                updates = ''
                if 'Failed to establish a new connection' in str(e):
                    print('Perda de conexão. Tentando novamente...')
                else:
                    print('Erro desconhecido: ' + str(e))
                time.sleep(3)

        if updates.get('result'):
            for data in updates['result']:
                get_update(data)
                print(json.dumps(data, indent=2))

                message = data.get('message')
                if not message:
                    continue

                text = message.get('text', '').strip().lower()
                chat_id = message['chat']['id']

                if text == "admin_bot":
                    admin.id_admin(data)
                    get_message(chat_id, "✅ Administrador configurado com sucesso!")
                elif text == "adm_grup":
                    id_group.id_gruop(data)
                    get_message(chat_id, "✅ Grupo configurado com sucesso!")
                    start = None 

        time.sleep(3)

    except Exception as e:
        print('Erro no loop principal:', e)

core.Login("usuario e senha")
