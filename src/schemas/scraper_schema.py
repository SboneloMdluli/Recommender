from dataclasses import dataclass

from hydra.core.config_store import ConfigStore


@dataclass
class Settings:
    headers: dict[str, str]
    urls: dict[str, str]


@dataclass
class WebScraper:
    settings: Settings


cs = ConfigStore.instance()

# Register the config schema explicitly with the full config group path
cs.store(
    name="config_schema", node=WebScraper, group="scrapping", package="_group_"
)
