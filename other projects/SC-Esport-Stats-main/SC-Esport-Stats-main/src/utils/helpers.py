def load_json(file_path):
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def save_to_csv(data, file_path):
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

def format_date(date):
    return date.strftime('%Y-%m-%d')