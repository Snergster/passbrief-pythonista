#!/usr/bin/env python3
"""Weather management and acquisition services."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import requests

from ..config import Config
from ..io import ConsoleIO, IOInterface
from ..models import ManualWeatherPrompt, WeatherSnapshot


LOGGER = logging.getLogger(__name__)


class WeatherManager:
    """Manages weather data fetching and processing."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        io: Optional[IOInterface] = None,
    ) -> None:
        self._session = session or requests.Session()
        self._io = io or ConsoleIO()

    def fetch_metar(self, icao_code: str) -> Optional[WeatherSnapshot]:
        """Fetch METAR data and return a structured weather snapshot."""

        url = (
            "https://aviationweather.gov/api/data/metar?ids="
            f"{icao_code}&format=json&taf=false"
        )

        try:
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - thin wrapper
            LOGGER.warning("Weather fetch failed for %s: %s", icao_code, exc)
            return self.request_manual_weather(icao_code)

        try:
            data = response.json()
        except ValueError as exc:  # pragma: no cover - thin wrapper
            LOGGER.warning("Invalid weather payload for %s: %s", icao_code, exc)
            return self.request_manual_weather(icao_code)

        if not data:
            LOGGER.warning("No METAR data returned for %s", icao_code)
            return self.request_manual_weather(icao_code)

        metar_data = data[0]
        metar_time = datetime.fromisoformat(metar_data["reportTime"].replace("Z", "+00:00"))
        current_time = datetime.now(timezone.utc)
        age_minutes = int((current_time - metar_time).total_seconds() / 60)

        if age_minutes > Config.METAR_MAX_AGE_MINUTES:
            LOGGER.info(
                "Discarding stale METAR for %s (age=%s min)",
                icao_code,
                age_minutes,
            )
            return self.request_manual_weather(icao_code)

        raw_altimeter = float(metar_data.get("altim", 29.92))
        if raw_altimeter > 100:
            altimeter_inhg = round(raw_altimeter * 0.02953, 2)
            unit_info = "hPa converted to inHg"
            LOGGER.debug(
                "Converted altimeter %s hPa to %s inHg for %s",
                raw_altimeter,
                altimeter_inhg,
                icao_code,
            )
        else:
            altimeter_inhg = round(raw_altimeter, 2)
            unit_info = "inHg (no conversion)"

        return WeatherSnapshot(
            station=icao_code,
            observed_at=metar_time,
            age_minutes=age_minutes,
            wind_dir=int(metar_data.get("wdir", 0) or 0),
            wind_speed=int(metar_data.get("wspd", 0) or 0),
            temperature_c=float(metar_data.get("temp", 15) or 15),
            altimeter_inhg=altimeter_inhg,
            raw_altimeter=raw_altimeter,
            altimeter_units=unit_info,
            source="NOAA Aviation Weather",
        )

    def request_manual_weather(self, station: str) -> Optional[WeatherSnapshot]:
        """Collect manual weather input when METAR data is unavailable."""

        self._io.warning(f"METAR unavailable for {station} - manual input required")
        try:
            prompt = ManualWeatherPrompt(
                wind_dir=int(self._io.prompt("Wind direction (degrees magnetic)", "0")),
                wind_speed=int(self._io.prompt("Wind speed (knots)", "0")),
                temperature_c=float(self._io.prompt("Temperature (°C)", "15")),
                altimeter_inhg=float(self._io.prompt("Altimeter setting (inHg)", "29.92")),
            )
        except ValueError:
            self._io.error("Invalid manual weather input; aborting weather collection")
            return None

        observed_at = datetime.now(timezone.utc)
        return WeatherSnapshot(
            station=station,
            observed_at=observed_at,
            age_minutes=0,
            wind_dir=prompt.wind_dir,
            wind_speed=prompt.wind_speed,
            temperature_c=prompt.temperature_c,
            altimeter_inhg=prompt.altimeter_inhg,
            raw_altimeter=prompt.altimeter_inhg,
            altimeter_units="Manual input (inHg)",
            source="Manual Input",
        )
