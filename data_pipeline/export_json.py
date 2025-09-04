import os
import json
import math
import pandas as pd
import psycopg2
from psycopg2 import sql

# --- Read DB creds from environment ---
PG_HOST = os.getenv("PG_HOST", "")
PG_DATABASE = os.getenv("PG_DATABASE", "")
PG_USER = os.getenv("PG_USER", "")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_PORT = os.getenv("PG_PORT", "5432")

TABLE_NAME = "entity.pincode_store_mapping"
CHANNEL_ID_COL = "channel_id"
LAT_COL = "latitude"
LON_COL = "longitude"
STORE_ID_COL = "store_id"

CHANNEL_ID_CONFIG = {
    27: {"name": "Blinkit", "color": "#D8C414"},
    65: {"name": "Swiggy", "color": "#EC822A"},
    109: {"name": "Zepto", "color": "#A10DA1"},
}

ROOT = os.path.dirname(os.path.dirname(__file__))
STORES_JSON_PATH = os.path.join(ROOT, "stores.json")
CONFIG_JS_PATH = os.path.join(ROOT, "config.js")


def db_connect():
    try:
        conn = psycopg2.connect(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
        )
        print("✅ Connected to Postgres.")
        return conn
    except Exception as e:
        print(f"❌ Could not connect to Postgres: {e}")
        return None


def fetch_data(conn):
    try:
        ids = tuple(CHANNEL_ID_CONFIG.keys())
        schema, tbl = TABLE_NAME.split(".", 1)
        table_fragment = sql.SQL("{}.{}").format(
            sql.Identifier(schema), sql.Identifier(tbl)
        )

        query = sql.SQL(
            'SELECT {lat}, {lon}, {channel}, {store} FROM {table} WHERE {channel} IN %s'
        ).format(
            lat=sql.Identifier(LAT_COL),
            lon=sql.Identifier(LON_COL),
            channel=sql.Identifier(CHANNEL_ID_COL),
            store=sql.Identifier(STORE_ID_COL),
            table=table_fragment,
        )

        with conn.cursor() as cur:
            cur.execute(query, (ids,))
            rows = cur.fetchall()
            cols = [LAT_COL, LON_COL, CHANNEL_ID_COL, STORE_ID_COL]
            df = pd.DataFrame(rows, columns=cols)
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

        records.append(
            {
                "lat": lat,
                "lon": lon,
                "source_name": source_name,
                "color": color,
                "store_id": store_id,
            }
        )

    with open(STORES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"✅ Wrote {len(records)} records to {STORES_JSON_PATH}")


def write_config_js():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        print("⚠️ No GOOGLE_MAPS_API_KEY found in environment.")
    with open(CONFIG_JS_PATH, "w", encoding="utf-8") as f:
        f.write(f"const GOOGLE_MAPS_API_KEY = '{api_key}';\n")
    print(f"✅ Wrote config.js with API key")


def main():
    conn = db_connect()
    if conn:
        df = fetch_data(conn)
        conn.close()
        sanitize_and_export(df)
    else:
        print("⚠️ Skipping DB fetch.")
        if not os.path.exists(STORES_JSON_PATH):
            with open(STORES_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("✅ Created empty stores.json")
    write_config_js()


if __name__ == "__main__":
    main()
