from pydantic import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    db_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/iot"
    
    mqtt_host: str = "broker"
    mqtt_port: int = 8883
    mqtt_tls: bool = True
    mqtt_ca_cert: Optional[str] = "/certs/ca.crt"
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_client_id: str = "backend-consumer"
    
    start_mqtt: bool = False  # enable in compose

    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60
    admin_user: str = "admin"
    admin_password: str = "adminpass"
    
    cors_origins: str = "https://localhost, http://localhost:8080"
    
    class Config: 
        env_file = ".env"
settings = Settings()
