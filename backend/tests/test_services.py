import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.route_optimizer import optimize_route, _haversine
from app.services.country_service import get_country_info
from app.agents.travel_graph import BUDGET_MULTIPLIERS_INR

def test_route_optimizer_empty():
    result = optimize_route([])
    assert result['sequence'] == []
    assert result['total_distance_km'] == 0.0

def test_route_optimizer_single():
    result = optimize_route(['Eiffel Tower'], city_hint='Paris')
    assert result['sequence'] == ['Eiffel Tower']

def test_route_optimizer_multiple():
    locs = ['Eiffel Tower', 'Louvre Museum', 'Notre Dame Cathedral']
    result = optimize_route(locs, city_hint='Paris')
    assert len(result['sequence']) == 3
    assert set(result['sequence']) == set(locs)
    assert result['total_distance_km'] > 0
    assert 'coordinates' in result
    assert 'center' in result

def test_haversine_known_distance():
    # Paris to London ~344km
    dist = _haversine(48.8566, 2.3522, 51.5074, -0.1278)
    assert 300 < dist < 400

def test_country_service_goa():
    info = get_country_info('Goa')
    assert info is not None
    assert info['name'] == 'India'
    assert info['currency_code'] == 'INR'

def test_country_service_paris():
    info = get_country_info('Paris')
    assert info is not None
    assert info['name'] == 'France'

def test_country_service_unknown():
    info = get_country_info('xyzabc123')
    assert info is not None  # Should fallback to India

def test_budget_multipliers():
    assert 'budget' in BUDGET_MULTIPLIERS_INR
    assert 'mid-range' in BUDGET_MULTIPLIERS_INR
    assert 'luxury' in BUDGET_MULTIPLIERS_INR
    assert BUDGET_MULTIPLIERS_INR['budget'] < BUDGET_MULTIPLIERS_INR['luxury']

def test_route_has_coordinates():
    result = optimize_route(['Baga Beach', 'Fort Aguada'], city_hint='Goa')
    assert 'coordinates' in result
    for loc in result['sequence']:
        assert loc in result['coordinates']
        coords = result['coordinates'][loc]
        assert len(coords) == 2

def test_route_details_have_coords():
    result = optimize_route(['Baga Beach', 'Fort Aguada', 'Anjuna Beach'], city_hint='Goa')
    for detail in result['route_details']:
        assert 'from_coords' in detail
        assert 'to_coords' in detail
