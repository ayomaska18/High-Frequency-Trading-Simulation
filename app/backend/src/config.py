from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    coinapi_api_key: str
    pgadmin_default_email: str 
    pgadmin_default_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_hostname: str
    database_port: str
    influxdb_mode: str
    influxdb_url: str
    influxdb_username: str
    influxdb_password: str
    influxdb_org: str
    influxdb_bucket: str
    influxdb_admin_token: str


    class Config:
        env_file = ".env"
        
settings = Settings() 