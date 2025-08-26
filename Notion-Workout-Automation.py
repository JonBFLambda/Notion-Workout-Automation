import os
import requests
from datetime import datetime
import json
import re

def handler(pd):
    """
    Handles inserting predefined workout routines into a Notion database.

    This function reads the routine type from the incoming HTTP request, 
    retrieves the last inserted orders, and automatically inserts new 
    entries into Notion, maintaining previous Stand values for each exercise.

    Args:
        pd: Pipedream request object containing the trigger event with the request body.

    Returns:
        dict: Status of the operation and count of inserted entries.
    """

    NOTION_TOKEN = os.environ["NOTION_TOKEN"]
    DATABASE_ID = os.environ["DATABASE_ID"]

    print("DEBUG - NOTION_TOKEN:", NOTION_TOKEN[:10] + "...")
    print("DEBUG - DATABASE_ID:", DATABASE_ID)

    # --- Parse incoming request body ---
    raw_body = pd.steps["trigger"]["event"].get("body")
    if not raw_body:
        print("ERROR - No body received")
        return {"ok": False, "error": "No body received"}

    if isinstance(raw_body, str):
        try:
            body = json.loads(raw_body)
        except Exception as e:
            print("ERROR - Failed to parse body:", raw_body)
            return {"ok": False, "error": str(e)}
    else:
        body = raw_body

    routine_type = body.get("tipo")
    print("DEBUG - Received routine type:", routine_type)

    # --- Predefined routines ---
    routines = {
        "PUSH": [
            ("Press banca", "4x6-8", "1-3"),
            ("Press inclinado mancuernas", "3x6-10", "1-3"),
            ("Contractora pectoral", "3x6-10", "1-2"),
            ("Contractora posterior", "3x8-10", "1-2"),
            ("Elevaciones laterales polea", "4x6-12", "0-1"),
            ("Extensiones tríceps unilateral", "4x8-12", "0-1"),
            ("Abdomen en banco", "5x10-20", "0-1"),
        ],
        "PULL": [
            ("Dominadas pronas", "3x6-8", "0-1"),
            ("Remo neutro máquina", "4x6-10", "1-2"),
            ("Jalón al pecho", "4x8-10", "1-2"),
            ("Curl bayesian en polea", "3x6-8", "0-1"),
            ("Curl martillo", "3x10-12", "0-1"),
            ("Hiperextensiones", "3x10-20", "1-3"),
        ],
        "LEGS": [
            ("Sentadilla Hack", "3x6-8", "1-3"),
            ("Zancadas kettlebell", "3x8-10", "1-3"),
            ("Curl femoral unilateral", "4x8-12", "0-1"),
            ("Aductor en máquina", "3x8-12", "0-1"),
            ("Cuádriceps unilateral", "3x8-12", "0-1"),
            ("Gemelos en hacka", "5x10-20", "0-1"),
            ("Abdomen en banco", "5x10-20", "0-1"),
        ],
        "UPPER": [
            ("Dips barras paralelas", "3x8-12", "1-3"),
            ("Pull over en polea", "4x6-10", "1-2"),
            ("Laterales en polea", "3x8-12", "0-1"),
            ("Press kettlebell", "3x8-12", "1-2"),
            ("Curl predicador", "3x8-12", "0-1"),
            ("Extensiones tríceps unilateral", "2x8-10", "0-1"),
            ("Hombro posterior unilateral", "3x8-12", "0-1"),
        ],
    }

    exercises = routines.get(routine_type, [])
    today_date = datetime.now().strftime("%Y-%m-%d")

    headers_notion = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # --- Fetch global order ---
    query_global = {
        "sorts": [{"property": "Orden", "direction": "descending"}],
        "page_size": 1,
    }
    res_global = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=headers_notion,
        json=query_global,
    )
    data_global = res_global.json()

    last_order_global = 0
    if data_global.get("results"):
        props = data_global["results"][0]["properties"]
        if "Orden" in props and props["Orden"]["number"] is not None:
            last_order_global = props["Orden"]["number"]

    # --- Fetch last entries of this routine type ---
    query_type = {
        "filter": {"property": "Nombre", "title": {"contains": routine_type}},
        "sorts": [{"property": "Orden", "direction": "descending"}],
        "page_size": 100,
    }
    res_type = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=headers_notion,
        json=query_type,
    )
    data_type = res_type.json()

    # --- Retrieve last Stand values ---
    last_values_stand = {}
    for page in data_type.get("results", []):
        props = page["properties"]
        if "Ejercicio" in props and props["Ejercicio"]["rich_text"]:
            exercise_name = props["Ejercicio"]["rich_text"][0]["text"]["content"]
            if "Stand" in props and props["Stand"]["rich_text"]:
                stand_val = props["Stand"]["rich_text"][0]["text"]["content"]
                last_values_stand[exercise_name] = stand_val

    # --- Determine new orders ---
    last_order_type = 0
    if data_type.get("results"):
        props = data_type["results"][0]["properties"]
        if "Nombre" in props and props["Nombre"]["title"]:
            title = props["Nombre"]["title"][0]["plain_text"]
            match = re.search(rf"{routine_type}-(\d+)", title)
            if match:
                last_order_type = int(match.group(1))

    new_order_global = last_order_global + 1
    new_order_type = last_order_type + 1

    print(f"DEBUG - New global order: {new_order_global}, New {routine_type} order: {new_order_type}")

    # --- Insert exercises into Notion ---
    inserted_count = 0
    for (name, series_reps, rir) in reversed(exercises):
        stand_val = last_values_stand.get(name, "")
        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Nombre": {"title": [{"text": {"content": f"{routine_type}-{new_order_type}"}}]},
                "Orden": {"number": new_order_global},
                "Fecha": {"date": {"start": today_date}},
                "Tipo": {"select": {"name": "GIMNASIO"}},
                "Ejercicio": {"rich_text": [{"text": {"content": name}}]},
                "Stand": {"rich_text": [{"text": {"content": stand_val}}]},
                "Series x Reps": {"rich_text": [{"text": {"content": series_reps}}]},
                "RIR": {"rich_text": [{"text": {"content": rir}}]},
                "RIR Registrado": {"rich_text": []},
                "Anotaciones": {"rich_text": []},
            },
        }
        try:
            res = requests.post("https://api.notion.com/v1/pages", headers=headers_notion, json=data)
            if res.status_code == 200:
                inserted_count += 1
            else:
                print("Error Notion:", res.status_code, res.text)
        except Exception as e:
            print("Error inserting:", str(e))

    return {"ok": True, "tipo": routine_type, "inserted": inserted_count}
