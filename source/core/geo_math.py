import math

class GeoMath:
    @staticmethod
    def grid_to_latlon(grid):
        """
        Converts a 4 or 6 character Maidenhead Grid Square to decimal Latitude and Longitude.
        Example: 'FN31pr' -> Lat: 41.7292, Lon: -72.625
        """
        grid = grid.strip().upper()
        if len(grid) < 4:
            return None, None

        # Parse longitude characters
        lon = (ord(grid[0]) - ord('A')) * 20 - 180
        lon += (ord(grid[2]) - ord('0')) * 2

        # Parse latitude characters
        lat = (ord(grid[1]) - ord('A')) * 10 - 90
        lat += (ord(grid[3]) - ord('0')) * 1

        # Check for 6-character sub-grid refinement
        if len(grid) >= 6:
            lon += (ord(grid[4]) - ord('A') + 0.5) * (2 / 24)
            lat += (ord(grid[5]) - ord('A') + 0.5) * (1 / 24)
        else:
            # Default to the center of the 4-character grid square
            lon += 1.0
            lat += 0.5

        return round(lat, 4), round(lon, 4)

    @staticmethod
    def calculate_distance_bearing(lat1, lon1, lat2, lon2):
        """
        Calculates Great-Circle Distance (in kilometers) and initial bearing (in degrees)
        between two decimal lat/lon points using the Haversine formula.
        """
        if None in (lat1, lon1, lat2, lon2):
            return 0.0, 0.0

        # Convert decimal degrees to radians
        r_lat1, r_lon1, r_lat2, r_lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula for distance
        dlon = r_lon2 - r_lon1
        dlat = r_lat2 - r_lat1
        a = math.sin(dlat/2)**2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        earth_radius_km = 6371.0
        distance = earth_radius_km * c

        # Initial bearing calculation
        x = math.sin(dlon) * math.cos(r_lat2)
        y = math.cos(r_lat1) * math.sin(r_lat2) - (math.sin(r_lat1) * math.cos(r_lat2) * math.cos(dlon))
        initial_bearing = math.atan2(x, y)
        
        # Convert radians back to degrees and normalize to 0-360
        bearing = (math.degrees(initial_bearing) + 360) % 360

        return round(distance, 1), round(bearing, 1)