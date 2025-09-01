import pandas as pd
import folium
import psycopg2

# --- 1. Configuration ---

# ⚙️ Database Connection Details
PG_HOST = '1.pgsql.db.1digitalstack.com'
PG_DATABASE = 'postgres'
PG_USER = 'powerbi'
PG_PASSWORD = 'powerbi@007'
PG_PORT = 5432

# Table and Column Names
TABLE_NAME = 'entity.pincode_store_mapping'
CHANNEL_ID_COL = 'channel_id'
LAT_COL = 'latitude'
LON_COL = 'longitude'
STORE_ID_COL = 'store_id'

# Service Configuration: Maps your channel IDs to names and colors
CHANNEL_ID_CONFIG = {
    27: {'name': 'Blinkit', 'color': "#D8C414"}, 
    65: {'name': 'Swiggy',  'color': "#EC822A"},
    109: {'name': 'Zepto',  'color': "#A10DA1"}
}

# 🗺️ Output file path
output_file = "index.html"

# --- 2. Database Functions ---

def db_connect():
    """Connects to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(user=PG_USER,
                                password=PG_PASSWORD,
                                host=PG_HOST,
                                port=PG_PORT,
                                database=PG_DATABASE)
        print("✅ Connected to Postgres successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to Postgres: {e}")
        return None

def fetch_data_from_db(conn, table, lat_col, lon_col, channel_col, channel_ids):
    """Fetches location data from a single table for specific channel IDs."""
    try:
        ids_to_query = tuple(channel_ids)
        query = f'SELECT "{lat_col}", "{lon_col}", "{channel_col}", "{STORE_ID_COL}" FROM {table} WHERE "{channel_col}" IN {ids_to_query};'

        print(f"\nExecuting query: {query}")
        df = pd.read_sql_query(query, conn)
        print(f"   - Fetched a total of {len(df)} rows from table '{table}'.")
        return df
    except Exception as e:
        print(f"   - ❌ Error fetching from '{table}': {e}")
        return None

# --- 3. Main Script Logic ---

conn = db_connect()

if conn:
    channel_ids_to_fetch = list(CHANNEL_ID_CONFIG.keys())
    df = fetch_data_from_db(conn, TABLE_NAME, LAT_COL, LON_COL, CHANNEL_ID_COL, channel_ids_to_fetch)
    
    conn.close()
    print("✅ Database connection closed.")

    if df is not None and not df.empty:
        # --- Map IDs to Names and Colors ---
        df['source_name'] = df[CHANNEL_ID_COL].map(lambda id: CHANNEL_ID_CONFIG.get(id, {}).get('name', 'Unknown'))
        df['color'] = df[CHANNEL_ID_COL].map(lambda id: CHANNEL_ID_CONFIG.get(id, {}).get('color', 'gray'))

        # --- Create the Map ---
        # Note: .mean() automatically ignores empty values, so this is correct.
        center_lat = df[LAT_COL].mean()
        center_lon = df[LON_COL].mean()

        store_counts = df.groupby('source_name').size()
        store_counts_html = """
        <div style="position: fixed; 
                    bottom: 50px; 
                    left: 50px; 
                    z-index: 1000; 
                    background-color: white; 
                    padding: 10px; 
                    border: 2px solid gray; 
                    border-radius: 5px">
            <h4>Store Counts</h4>
        """
        for service, count in store_counts.items():
            color = CHANNEL_ID_CONFIG[df[df['source_name'] == service][CHANNEL_ID_COL].iloc[0]]['color']
            store_counts_html += f'<p><span style="color:{color}">●</span> {service}: {count}</p>'
        store_counts_html += "</div>"

        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        m.get_root().html.add_child(folium.Element(store_counts_html))

        print("\nAdding location points to the map...")
        # Loop through the dataframe to add each point
        for idx, row in df.iterrows():
            # --- ✅ MODIFICATION: Skip row if lat/lon is empty ---
            if pd.isna(row[LAT_COL]) or pd.isna(row[LON_COL]):
                continue # Go to the next row

            tooltip_text = (
                f"<b>Service:</b> {row['source_name']}<br>"
                f"<b>Store ID:</b> {row[STORE_ID_COL]}<br>"
                f"<b>Lat:</b> {row[LAT_COL]:.4f}<br>"
                f"<b>Lon:</b> {row[LON_COL]:.4f}"
            )

            # Add a circle marker with the specific color for that service
            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=4,
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.8,
                tooltip=tooltip_text
            ).add_to(m)

        # --- Save the Map to an HTML File ---
        m.save(output_file)
        print(f"\n✅ Success! Combined map has been saved to '{output_file}'")
    else:
        print("\n❌ No data was fetched from the database. The map was not generated.")