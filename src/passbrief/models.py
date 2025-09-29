"""Domain models for PassBrief."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterator, Mapping, Optional


class _MappingMixin(Mapping[str, Any]):
    """Allow dataclasses to behave like read-only mappings for legacy access."""

    def __getitem__(self, key: str) -> Any:  # pragma: no cover - trivial
        return asdict(self)[key]

    def __iter__(self) -> Iterator[str]:  # pragma: no cover - trivial
        return iter(asdict(self).keys())

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(asdict(self))


@dataclass(frozen=True)
class WeatherSnapshot(_MappingMixin):
    """METAR-derived weather observations."""

    station: str
    observed_at: datetime
    age_minutes: int
    wind_dir: int
    wind_speed: int
    temperature_c: float
    altimeter_inhg: float
    raw_altimeter: float
    altimeter_units: str
    source: str


@dataclass(frozen=True)
class ManualWeatherPrompt(_MappingMixin):
    """Represents manual weather input when METAR is unavailable."""

    wind_dir: int
    wind_speed: int
    temperature_c: float
    altimeter_inhg: float


@dataclass(frozen=True)
class WindComponents(_MappingMixin):
    """Resolved headwind/crosswind data."""

    headwind: int
    crosswind: int
    crosswind_direction: str
    is_tailwind: bool
    crosswind_exceeds_limits: bool


@dataclass(frozen=True)
class ClimbGradientResult(_MappingMixin):
    """Computed climb gradient information for a single IAS regime."""

    ias: int
    true_airspeed: float
    ground_speed: float
    gradient_ft_per_nm: Optional[float]


@dataclass(frozen=True)
class ClimbGradientSummary(_MappingMixin):
    """Summarises climb performance at 91 and 120 KIAS."""

    tas_91: float
    gs_91: float
    gradient_91: Optional[float]
    tas_120: float
    gs_120: float
    gradient_120: Optional[float]
    climb_rate_91kias: Optional[float]


@dataclass(frozen=True)
class TakeoffPerformance(_MappingMixin):
    """Takeoff performance figures."""

    ground_roll_ft: int
    total_distance_ft: int


@dataclass(frozen=True)
class LandingPerformance(_MappingMixin):
    """Landing performance figures."""

    ground_roll_ft: int
    total_distance_ft: int


@dataclass(frozen=True)
class PerformanceSummary(_MappingMixin):
    """Aggregated performance calculations."""

    density_altitude_ft: int
    takeoff: TakeoffPerformance
    landing: LandingPerformance
    climb_91: ClimbGradientResult
    climb_120: ClimbGradientResult
    wind: WindComponents
