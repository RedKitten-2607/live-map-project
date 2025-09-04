# --- Database Config ---
PG_HOST = '1.pgsql.db.1digitalstack.com'
PG_DATABASE = 'postgres'
PG_USER = 'powerbi'
PG_PASSWORD = 'powerbi@007'
PG_PORT = 5432

# --- Table and Columns ---
TABLE_NAME = 'entity.pincode_store_mapping'
CHANNEL_ID_COL = 'channel_id'
LAT_COL = 'latitude'
LON_COL = 'longitude'
STORE_ID_COL = 'store_id'

# --- Channel mapping ---
CHANNEL_ID_CONFIG = {
    27: {'name': 'Blinkit', 'color': "#D8C414"},
    65: {'name': 'Swiggy',  'color': "#EC822A"},
    109: {'name': 'Zepto',  'color': "#A10DA1"}
}

# --- API Keys ---
# GOOGLE_MAPS_API_KEY = "AIzaSyDoKVo3LiVRqP5UrG6WHh6uGhZZqlXGiO8"
