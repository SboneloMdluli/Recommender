from hydra import compose, initialize
from pydantic import BaseModel


class Headers(BaseModel):
    user_agent: str


class Settings(BaseModel):
    headers: Headers


def load_config() -> Settings:
    with initialize(version_base=None, config_path="../../config"):
        cfg = compose(config_name="settings")
        return Settings(headers=Headers(user_agent=cfg.headers.user_agent))


settings = load_config()
