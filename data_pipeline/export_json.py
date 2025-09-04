# data_pipeline/export_json.py
import os
import json
import math
import pandas as pd
import psycopg2

# --- Config from environment ---
PG_HOST = os.getenv("PG_HOST")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Table details (hardcoded, since they don’t change often)
TABLE_NAME = "entity.pincode_store_mapping"
LAT_COL = "latitude"
LON_COL = "longitude"
CHANNEL_ID_COL = "channel_id"
STORE_ID_COL = "store_id"

# Channel config mapping
CHANNEL_ID_CONFIG = {
    27: {"name": "Blinkit", "color": "#D8C414"},
    65: {"name": "Swiggy", "color": "#EC822A"},
    109: {"name": "Zepto", "color": "#A10DA1"},
}

# File outputs (repo root)
STORES_JSON_PATH = os.path.join("stores.json")
CONFIG_JS_PATH = os.path.join("config.js")


def db_connect():
    """Connect to Postgres using secrets from env"""
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
    """Fetch required columns from DB"""
    try:
        ids = tuple(CHANNEL_ID_CONFIG.keys())
        query = f"""
            SELECT "{LAT_COL}", "{LON_COL}", "{CHANNEL_ID_COL}", "{STORE_ID_COL}"
            FROM {TABLE_NAME}
            WHERE "{CHANNEL_ID_COL}" IN %s
        """
        df = pd.read_sql_query(query, conn, params=(ids,))
        print(f"✅ Fetched {len(df)} rows from DB.")
        return df
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame(columns=[LAT_COL, LON_COL, CHANNEL_ID_COL, STORE_ID_COL])


def sanitize_and_export(df):
    """Clean data and write stores.json"""
    records = []
    for _, row in df.iterrows():
        try:
            lat = float(row[LAT_COL])
            lon = float(row[LON_COL])
            if math.isnan(lat) or math.isnan(lon):
                continue
        except Exception:
            continue

        channel_id = int(row[CHANNEL_ID_COL])
        mapping = CHANNEL_ID_CONFIG.get(channel_id, {})
        source_name = mapping.get("name", "Unknown")
        color = mapping.get("color", "#888888")

        records.append(
            {
                "lat": lat,
                "lon": lon,
                "source_name": source_name,
                "color": color,
                "store_id": row[STORE_ID_COL],
            }
        )

    with open(STORES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"✅ Wrote {len(records)} records to {STORES_JSON_PATH}")


def write_config_js():
    """Write config.js with API key"""
    with open(CONFIG_JS_PATH, "w", encoding="utf-8") as f:
        f.write(f"const GOOGLE_MAPS_API_KEY = '{GOOGLE_MAPS_API_KEY}';\n")
    print(f"✅ Wrote {CONFIG_JS_PATH} with API key")


def main():
    conn = db_connect()
    if conn:
        df = fetch_data(conn)
        conn.close()
    else:
        print("⚠️ Skipping DB fetch.")
        df = pd.DataFrame(columns=[LAT_COL, LON_COL, CHANNEL_ID_COL, STORE_ID_COL])

    sanitize_and_export(df)
    if GOOGLE_MAPS_API_KEY:
        write_config_js()
    else:
        print("⚠️ No GOOGLE_MAPS_API_KEY found in environment.")


if __name__ == "__main__":
    main()
