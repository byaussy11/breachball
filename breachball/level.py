"""Loads the brick catalog (reusable brick-type templates, shared across
every level) and individual level JSON files, per the data schema."""

import json


class BrickCatalog:
    def __init__(self, entries: dict):
        self.entries = entries

    @classmethod
    def load(cls, path) -> "BrickCatalog":
        with open(path) as f:
            data = json.load(f)
        return cls(data)

    def get(self, brick_id: str) -> dict:
        return self.entries[brick_id]


class Level:
    def __init__(self, data: dict):
        self.section = data.get("section")
        self.level_number = data.get("level_number")
        self.is_boss_level = data.get("is_boss_level", False)
        self.arena_type = data.get("arena_type", "shared_zone")
        self.paddle_lanes = data.get("paddle_lanes", {})
        self.player_count_scaling = data.get("player_count_scaling", {})
        self.brick_grid = self._resolve_brick_grid(data)
        self.enemy_types = data.get("enemy_types", {})
        self.enemy_spawns = data.get("enemy_spawns", [])
        self.boss_id = data.get("boss_id")

    @staticmethod
    def _resolve_brick_grid(data: dict):
        if "brick_grid" in data:
            return data["brick_grid"]
        if "legend" in data and "rows" in data:
            legend = data["legend"]
            return [[legend.get(ch) for ch in row] for row in data["rows"]]
        raise ValueError("Level JSON must include either 'brick_grid' or 'legend' + 'rows'")

    @classmethod
    def load(cls, path) -> "Level":
        with open(path) as f:
            data = json.load(f)
        return cls(data)
