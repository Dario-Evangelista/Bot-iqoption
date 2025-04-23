import json
import os

caminho = "../../config.json"

def id_admin(update):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"{caminho}"))

    try:
        with open(config_path, 'r') as file:
            data = json.load(file)

        admin_id = update['message']['from']['id']
        data['admin'] = admin_id

        with open(config_path, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"✅ ID do administrador configurado: {admin_id}")
        
        return admin_id

    except Exception as e:
        print("❌ Erro ao salvar ID do administrador:", e)
        return None
