from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime paths used by the local MVP pipeline."""

    project_root: Path
    raw_dir: Path
    processed_dir: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "PipelineConfig":
        data_dir = project_root / "data"
        return cls(
            project_root=project_root,
            raw_dir=data_dir / "raw",
            processed_dir=data_dir / "processed",
        )
