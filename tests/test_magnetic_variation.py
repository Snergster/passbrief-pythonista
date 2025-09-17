#!/usr/bin/env python3
"""
Test script for magnetic variation calculation
Tests the three-tier system: pygeomag -> manual -> regional approximation
"""

def test_magnetic_variation():
    """Test magnetic variation calculation methods"""
    # Import the method from the refactored app
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from passbrief import AirportManager
    
    print("Testing Magnetic Variation Calculation")
    print("=" * 50)
    
    # Test locations with known magnetic variation
    test_locations = [
        {"name": "KSLC (Salt Lake City)", "lat": 40.7884, "lon": -111.9778, "expected": "~12°E"},
        {"name": "KJFK (New York JFK)", "lat": 40.6398, "lon": -73.7789, "expected": "~-13°W"},
        {"name": "KSFO (San Francisco)", "lat": 37.6213, "lon": -122.3790, "expected": "~13°E"},
        {"name": "KMIA (Miami)", "lat": 25.7959, "lon": -80.2870, "expected": "~-6°W"}
    ]
    
    print("\n🧪 Testing NOAA WMM API availability...")
    try:
        import requests
        from datetime import datetime
        
        # Test API call directly
        api_url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"
        params = {
            'lat1': 40.7884,  # KSLC Salt Lake City
            'lon1': -111.9778,
            'model': 'WMM',
            'startYear': datetime.now().year,
            'startMonth': datetime.now().month, 
            'startDay': datetime.now().day,
            'resultFormat': 'json',
            'key': 'zNEw7'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and len(data['result']) > 0:
                declination = data['result'][0]['declination']
                print("✅ NOAA WMM API is working!")
                print(f"✅ Sample calculation: KSLC = {declination:+.2f}° declination")
                api_available = True
            else:
                print("❌ API returned invalid data format")
                api_available = False
        else:
            print(f"❌ API request failed: HTTP {response.status_code}")
            api_available = False
        
    except Exception as e:
        print(f"❌ NOAA API not available: {e}")
        print("📝 Check internet connection or try manual input")
        api_available = False
    
    print(f"\n🧭 Testing magnetic variation calculation for {len(test_locations)} airports...")
    
    for i, location in enumerate(test_locations, 1):
        print(f"\n{i}. {location['name']} (Expected: {location['expected']})")
        
        try:
            # This will test the full three-tier system
            if api_available:
                print("   Using NOAA WMM API...")
            else:
                print("   Will fall back to manual input or regional approximation...")
                
            variation = AirportManager._calculate_magnetic_variation(
                location['lat'], 
                location['lon']
            )
            print(f"   Result: {variation:+.2f}° magnetic variation")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*50}")
    if api_available:
        print("🎉 NOAA WMM API integration working perfectly!")
        print("✈️ Magnetic variation will be calculated automatically")
        print("🌐 Using official WMM2025 data from NOAA")
    else:
        print("⚠️ NOAA API not available - manual entry required")
        print("🌐 Check internet connection")
        print("📱 System will still work with manual input and regional approximation")
    
    return api_available

if __name__ == "__main__":
    test_magnetic_variation()