import os
import requests
from typing import List, Optional, Tuple
from ..state import POI, RoutePlan, RouteStep

class AMapService:
    def __init__(self):
        self.api_key = os.getenv("AMAP_API_KEY")
        self.base_url = "https://restapi.amap.com/v3"
        
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to (lat, lon).
        Returns None if failed.
        """
        if not self.api_key:
            print("Warning: AMAP_API_KEY not set.")
            return None
            
        url = f"{self.base_url}/geocode/geo"
        params = {
            "address": address,
            "key": self.api_key,
            "city": "beijing" # Optional restriction
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("status") == "1" and data.get("geocodes"):
                # location is "lon,lat"
                location_str = data["geocodes"][0]["location"]
                lon_str, lat_str = location_str.split(",")
                return float(lat_str), float(lon_str)
            else:
                print(f"Geocode failed for {address}: {data.get('info')}")
                return None
        except Exception as e:
            print(f"Geocode error for {address}: {e}")
            return None

    def get_optimal_route(self, pois: List[POI], travel_mode: str = "walking") -> RoutePlan:
        """
        Calculate route for a list of POIs.
        travel_mode: 'walking' or 'driving'
        """
        if not pois:
            return RoutePlan(steps=[], total_duration=0, total_distance=0, summary="No POIs provided", mode=travel_mode)

        # 1. Enrich coordinates if missing
        valid_pois = []
        for poi in pois:
            if not poi.lat or not poi.lon:
                coords = self.get_coordinates(poi.name)
                if coords:
                    poi.lat, poi.lon = coords
            
            if poi.lat and poi.lon:
                valid_pois.append(poi)
            else:
                print(f"Skipping POI {poi.name} due to missing coordinates")

        if len(valid_pois) < 2:
             # Fallback for single point or no valid points
             steps = [RouteStep(poi=p, visit_duration=60, transit_note="单一景点") for p in valid_pois]
             return RoutePlan(steps=steps, total_duration=len(valid_pois)*60, total_distance=0, summary=" -> ".join([p.name for p in valid_pois]), mode=travel_mode)

        # 2. Construct API Request
        # Origin: First POI
        origin = f"{valid_pois[0].lon},{valid_pois[0].lat}"
        # Destination: Last POI
        destination = f"{valid_pois[-1].lon},{valid_pois[-1].lat}"
        
        # Waypoints: Intermediate POIs
        waypoints = []
        if len(valid_pois) > 2:
            for p in valid_pois[1:-1]:
                waypoints.append(f"{p.lon},{p.lat}")
        waypoints_str = "|".join(waypoints)

        # Determine API endpoint based on mode
        if travel_mode == "driving":
            url = f"{self.base_url}/direction/driving"
        else:
            url = f"{self.base_url}/direction/walking"

        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key,
        }
        if waypoints_str:
            params["waypoints"] = waypoints_str
        
        # Driving API specific params if needed (e.g. strategy)
        if travel_mode == "driving":
            params["strategy"] = 0 # 0: speed priority (default)

        # 3. Call API
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("status") == "1" and data.get("route") and data["route"].get("paths"):
                path = data["route"]["paths"][0]
                total_duration_sec = int(path.get("duration", 0))
                total_distance_m = int(path.get("distance", 0))
                
                # Construct RoutePlan
                steps = []
                for i, poi in enumerate(valid_pois):
                    transit_note = f"{'驾车' if travel_mode == 'driving' else '步行'}前往下一站" if i < len(valid_pois) - 1 else "行程结束"
                    steps.append(RouteStep(poi=poi, visit_duration=60, transit_note=transit_note))
                
                summary = " -> ".join([p.name for p in valid_pois])
                
                # Convert duration to minutes (approx) + visit time
                total_duration_min = (total_duration_sec // 60) + (len(valid_pois) * 60)
                
                # Extract polyline
                polyline_list = []
                if path.get("steps"):
                    for step in path["steps"]:
                        if step.get("polyline"):
                            polyline_list.append(step["polyline"])
                
                full_polyline = ";".join(polyline_list)

                return RoutePlan(
                    steps=steps,
                    total_duration=total_duration_min,
                    total_distance=total_distance_m,
                    summary=summary,
                    polyline=full_polyline,
                    mode=travel_mode
                )
            else:
                print(f"AMap Routing failed: {data.get('info')}. Falling back to straight line logic.")
                raise Exception("AMap API returned failure")

        except Exception as e:
            print(f"Routing error: {e}. Using fallback.")
            # Fallback: Simple straight line logic (mock)
            return self._fallback_route(valid_pois)

    def _fallback_route(self, pois: List[POI]) -> RoutePlan:
        # Simple pass-through
        steps = []
        for i, poi in enumerate(pois):
            steps.append(RouteStep(poi=poi, visit_duration=60, transit_note="直线距离估算"))
        
        return RoutePlan(
            steps=steps,
            total_duration=len(pois) * 70, # Mock duration
            total_distance=0, # Mock distance
            summary=" -> ".join([p.name for p in pois]),
            mode="walking" # Default fallback
        )

# Global instance
amap_service = AMapService()
