import json
import math

def export_to_geojson(file_path, export_points=False, export_profiles=False, export_links=False,
                      points_data=None, profiles_data=None, links_data=None):
    features = []

    if export_points and points_data:
        for p in points_data:
            features.append({
                "type": "Feature",
                "properties": {
                    "index": p.get('index'),
                    "type": p.get('type'),
                    "depth_m": p.get('depth')
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [p['lon'], p['lat']]
                }
            })

    if export_profiles and profiles_data:
        for i, prof in enumerate(profiles_data):
            angle_rad = math.radians(prof["azimuth"])
            perp_angle_rad = math.radians(prof["azimuth"] + 90)
            meter_to_deg_lat = 1 / 111320
            meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(prof["start_lat"])))

            lat_offset = prof["total_delta"] * math.cos(perp_angle_rad) * meter_to_deg_lat
            lon_offset = prof["total_delta"] * math.sin(perp_angle_rad) * meter_to_deg_lon

            line_coords = []
            for d in prof["distances"]:
                lat_c = d * math.cos(angle_rad) * meter_to_deg_lat
                lon_c = d * math.sin(angle_rad) * meter_to_deg_lon
                line_coords.append([prof["start_lon"] + lon_c + lon_offset,
                                    prof["start_lat"] + lat_c + lat_offset])

            features.append({
                "type": "Feature",
                "properties": {"name": f"Profil {i + 1}", "total_delta": prof["total_delta"]},
                "geometry": {"type": "LineString", "coordinates": line_coords}
            })

    if export_links and links_data:
        for i, link in enumerate(links_data):
            line_coords = [[p['lon'], p['lat']] for p in link]
            features.append({
                "type": "Feature",
                "properties": {"name": f"Polaczenie {i + 1}"},
                "geometry": {"type": "LineString", "coordinates": line_coords}
            })

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=4)