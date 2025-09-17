#!/usr/bin/env python3
"""
PassBrief Test Suite for Pythonista iOS
Combined test file for validating deployment
"""

def test_imports():
    """Test that all components can be imported"""
    print("Testing imports...")
    try:
        import passbrief_pythonista as passbrief
        assert hasattr(passbrief, 'create_briefing_generator')
        assert hasattr(passbrief, 'BriefingGenerator')
        assert hasattr(passbrief, 'PerformanceCalculator')
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_briefing_generator():
    """Test briefing generator creation"""
    print("Testing briefing generator...")
    try:
        import passbrief_pythonista as passbrief
        bg = passbrief.create_briefing_generator()
        assert bg is not None
        print("✅ Briefing generator created successfully")
        return True
    except Exception as e:
        print(f"❌ Briefing generator error: {e}")
        return False

def test_performance_calculations():
    """Test basic performance calculations"""
    print("Testing performance calculations...")
    try:
        import passbrief_pythonista as passbrief
        calc = passbrief.PerformanceCalculator()

        # Test pressure altitude
        pa = calc.calculate_pressure_altitude(29.92, 4500)
        assert pa == 4500  # Should be field elevation at standard pressure

        # Test density altitude
        da = calc.calculate_density_altitude(4500, 15)
        assert isinstance(da, (int, float))

        # Test wind components
        wind = calc.calculate_wind_components(270, 10, 90)
        assert 'headwind' in wind
        assert 'crosswind' in wind

        print("✅ Performance calculations working")
        return True
    except Exception as e:
        print(f"❌ Performance calculation error: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("🧪 Running PassBrief Pythonista Validation Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_briefing_generator,
        test_performance_calculations
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Deployment is ready for use.")
    else:
        print("⚠️ Some tests failed. Check deployment before use.")

    return passed == total

if __name__ == "__main__":
    run_all_tests()
