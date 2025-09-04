import os
import json
import math
import pandas as pd
import psycopg2
from config import (
    PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD, PG_PORT,
    TABLE_NAME, CHANNEL_ID_COL, LAT_COL, LON_COL, STORE_ID_COL,
    CHANNEL_ID_CONFIG, GOOGLE_MAPS_API_KEY
)

ROOT = os.path.dirname(os.path.dirname(__file__))
STORES_JSON_PATH = os.path.join(ROOT, "stores.json")
CONFIG_JS_PATH = os.path.join(ROOT, "config.js")

def db_connect():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            port=PG_PORT
        )
        print("✅ Connected to Postgres.")
        return conn
    except Exception as e:
        print(f"❌ Could not connect to Postgres: {e}")
        return None

def fetch_data(conn):
    try:
        ids = tuple(CHANNEL_ID_CONFIG.keys())
        query = f"""
            SELECT "{LAT_COL}", "{LON_COL}", "{CHANNEL_ID_COL}", "{STORE_ID_COL}"
            FROM {TABLE_NAME}
            WHERE "{CHANNEL_ID_COL}" IN {ids};
        """
        df = pd.read_sql_query(query, conn)
        print(f"✅ Fetched {len(df)} rows from database.")
        return df
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame(columns=[LAT_COL, LON_COL, CHANNEL_ID_COL, STORE_ID_COL])

def sanitize_and_export(df):
    records = []
    for _, r in df.iterrows():
        try:
            lat = float(r[LAT_COL])
            lon = float(r[LON_COL])
            if math.isnan(lat) or math.isnan(lon):
                continue
        except Exception:
            continue

        channel_id = int(r[CHANNEL_ID_COL])
        mapping = CHANNEL_ID_CONFIG.get(channel_id, {})
        source_name = mapping.get("name", "Unknown")
        color = mapping.get("color", "#888888")
        store_id = r[STORE_ID_COL]

        records.append({
            "lat": lat,
            "lon": lon,
            "source_name": source_name,
            "color": color,
            "store_id": store_id
        })

    with open(STORES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"✅ Wrote {len(records)} records to {STORES_JSON_PATH}")

def write_config_js():
    with open(CONFIG_JS_PATH, "w", encoding="utf-8") as f:
        f.write(f"const GOOGLE_MAPS_API_KEY = '{GOOGLE_MAPS_API_KEY}';\n")
    print(f"✅ Wrote config.js with API key")

def main():
    conn = db_connect()
    if not conn:
        return
    df = fetch_data(conn)
    conn.close()
    sanitize_and_export(df)
    write_config_js()

if __name__ == "__main__":
    main()
