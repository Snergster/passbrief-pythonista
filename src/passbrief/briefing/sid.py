#!/usr/bin/env python3
"""
SID (Standard Instrument Departure) Manager

Provides Standard Instrument Departure procedure validation and compatibility checking.
"""


class SIDManager:
    """Manages Standard Instrument Departure procedure analysis."""

    @staticmethod
    def get_applicable_sids(icao, runway):
        """
        Get Standard Instrument Departures (SIDs) applicable to the departure runway
        Returns list of applicable SID procedures with runway compatibility
        """
        print(f"🛫 Checking Standard Instrument Departures for {icao} runway {runway}...")

        # Common SID database for major airports
        # In production, this would query FAA or Jeppesen database
        sid_database = SIDManager._get_sid_database()

        if icao in sid_database:
            airport_sids = sid_database[icao]
            applicable_sids = []

            for sid in airport_sids:
                if SIDManager._is_runway_compatible(runway, sid['runways']):
                    applicable_sids.append(sid)

            if applicable_sids:
                print(f"   ✅ Found {len(applicable_sids)} applicable SID(s)")
                return applicable_sids
            else:
                print(f"   ⚠️ No SIDs available for runway {runway}")
                return []
        else:
            print(f"   ℹ️ No SID data available for {icao}")
            return []

    @staticmethod
    def _is_runway_compatible(runway, sid_runways):
        """Check if runway is compatible with SID runway restrictions"""
        if not sid_runways or sid_runways == ['ALL']:
            return True

        # Handle runway number variations (09/27, 09L/27R, etc.)
        runway_base = runway.replace('L', '').replace('R', '').replace('C', '').zfill(2)

        for sid_runway in sid_runways:
            sid_base = sid_runway.replace('L', '').replace('R', '').replace('C', '').zfill(2)
            if runway_base == sid_base:
                return True

        return False

    @staticmethod
    def _get_sid_database():
        """
        Sample SID database for common airports
        In production, this would query real departure procedure databases
        """
        return {
            'KPAO': [
                {
                    'name': 'DUMBARTON SEVEN',
                    'identifier': 'DUMBARTON7',
                    'runways': ['ALL'],
                    'initial_altitude': '2000',
                    'restrictions': ['DUMBARTON fix at or above 2000ft'],
                    'notes': 'Standard departure for Bay Area'
                }
            ],
            'KRHV': [
                {
                    'name': 'PIGEON POINT THREE',
                    'identifier': 'PGN3',
                    'runways': ['31L', '31R'],
                    'initial_altitude': '3000',
                    'restrictions': ['PGN at or above 3000ft'],
                    'notes': 'Westbound departure'
                }
            ],
            'KSJC': [
                {
                    'name': 'BSALT THREE',
                    'identifier': 'BSALT3',
                    'runways': ['12L', '12R', '30L', '30R'],
                    'initial_altitude': '4000',
                    'restrictions': ['BSALT at or above 4000ft'],
                    'notes': 'Bay Area standard'
                },
                {
                    'name': 'PIGEON POINT SEVEN',
                    'identifier': 'PGN7',
                    'runways': ['12L', '12R'],
                    'initial_altitude': '5000',
                    'restrictions': ['PGN at or above 5000ft'],
                    'notes': 'Westbound coastal departure'
                }
            ],
            'KOAK': [
                {
                    'name': 'OAKLAND SEVEN',
                    'identifier': 'OAKLAND7',
                    'runways': ['ALL'],
                    'initial_altitude': '3000',
                    'restrictions': ['OAK VORTAC at or above 3000ft'],
                    'notes': 'Standard Oakland departure'
                }
            ]
        }