from hydra import compose, initialize
from pydantic import BaseModel


class BookSettings(BaseModel):
    urls: dict[str, str]
    elements: dict[str, str]


def load_config() -> BookSettings:
    with initialize(version_base=None, config_path="../../config/books"):
        cfg = compose(config_name="books")
        return BookSettings(urls=cfg.urls, elements=cfg.elements)


book_settings: BookSettings = load_config()
