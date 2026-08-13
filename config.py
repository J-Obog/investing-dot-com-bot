from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ForumConfig:
    company_id: str
    company_slug: str
    asset_type: str

    @classmethod
    def from_dict(cls, data: dict) -> ForumConfig:
        return cls(
            company_id=data["companyId"],
            company_slug=data["companySlug"],
            asset_type=data["assetType"],
        )


@dataclass(frozen=True)
class BotConfig:
    at_bot: str
    command_symbol: str
    valid_commands: list[str]
    visible_forums: list[ForumConfig]

    @classmethod
    def from_dict(cls, data: dict) -> BotConfig:
        return cls(
            at_bot=data["atBot"],
            command_symbol=data["commandSymbol"],
            valid_commands=data["validCommands"],
            visible_forums=[
                ForumConfig.from_dict(forum) for forum in data["visibleForums"]
            ],
        )

    @classmethod
    def from_json(cls, path: str | Path) -> BotConfig:
        with Path(path).open(encoding="utf-8") as config_file:
            return cls.from_dict(json.load(config_file))
