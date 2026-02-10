import os
import toml
from pathlib import Path
import snowflake.connector
from contextlib import contextmanager
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

DATABASE = "GNN_SUPPLY_CHAIN_RISK"
SCHEMA = "GNN_SUPPLY_CHAIN_RISK"

_connection = None

def _load_private_key(key_path: str):
    with open(os.path.expanduser(key_path), "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def _load_snowflake_config():
    config_path = Path.home() / ".snowflake" / "connections.toml"
    if not config_path.exists():
        config_path = Path.home() / ".snowflake" / "config.toml"
    
    if config_path.exists():
        config = toml.load(config_path)
        connection_name = os.getenv("SNOWFLAKE_CONNECTION_NAME", "demo")
        
        if connection_name in config:
            return config[connection_name]
        elif "demo" in config:
            return config["demo"]
        elif len(config) > 0:
            for key, value in config.items():
                if isinstance(value, dict) and "account" in value:
                    return value
    return None

def get_connection():
    global _connection
    if _connection is None or _connection.is_closed():
        config = _load_snowflake_config()
        
        if config:
            conn_params = {
                "account": config.get("account") or config.get("accountname"),
                "user": config.get("user") or config.get("username"),
                "database": DATABASE,
                "schema": SCHEMA,
            }
            
            authenticator = config.get("authenticator", "").upper()
            if authenticator == "SNOWFLAKE_JWT" and "private_key_file" in config:
                conn_params["private_key"] = _load_private_key(config["private_key_file"])
            elif "password" in config:
                conn_params["password"] = config["password"]
            else:
                conn_params["authenticator"] = "externalbrowser"
            
            if "warehouse" in config:
                conn_params["warehouse"] = config["warehouse"]
            if "role" in config:
                conn_params["role"] = config["role"]
            
            _connection = snowflake.connector.connect(**conn_params)
        else:
            _connection = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT", "sfsenorthamerica-trsmith_aws1"),
                user=os.getenv("SNOWFLAKE_USER", "trsmith"),
                authenticator="externalbrowser",
                database=DATABASE,
                schema=SCHEMA,
            )
    return _connection

@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()

def query_to_dicts(cursor, query: str, params: tuple = None) -> list[dict]:
    cursor.execute(query, params)
    columns = [desc[0].lower() for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def query_one(cursor, query: str, params: tuple = None) -> dict | None:
    results = query_to_dicts(cursor, query, params)
    return results[0] if results else None
