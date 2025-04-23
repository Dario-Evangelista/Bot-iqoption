import json
import os

caminho = "../../config.json"

def id_gruop(update):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), caminho))

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)  

        chat = update.get('message', {}).get('chat', {})
        chat_id = chat.get('id')

        if chat_id and str(chat_id).startswith("-100"):  
            print(f"✅ ID do grupo configurado: {chat_id}")
            config['group'] = chat_id

            with open(config_path, 'w') as file:
                json.dump(config, file, indent=4)

            return chat_id
        else:
            print("❌ Não parece ser um grupo. ID:", chat_id)
            return None

    except Exception as e:
        print("❌ Erro ao salvar ID do grupo:", e)
        return None
