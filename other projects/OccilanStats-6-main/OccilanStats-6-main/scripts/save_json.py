import json

def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Données enregistrées dans {file_path}")

def load_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)