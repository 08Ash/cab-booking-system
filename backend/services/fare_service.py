from maps_config import gmaps

def calculate_fare(pickup_lat, pickup_lng, drop_lat, drop_lng):
    
    result = gmaps.distance_matrix(
        (pickup_lat, pickup_lng),
          (drop_lat, drop_lng),
          mode="driving"
    )
    
    distance_meters = result["rows"][0]["elements"][0]["distance"]["value"]

    distance_km = distance_meters / 1000

    base_fare = 50
    per_km_rate = 12

    fare = base_fare + (distance_km * per_km_rate)

    return round(fare, 2)