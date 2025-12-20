from collections import deque
from src.utils import Position, GameSettings, Logger
from src.maps.map import Map

class NavigationManager:
    MAX_ITERATIONS = 5000  # Safety limit to prevent infinite loops/freezes

    @staticmethod
    def bfs(start: Position, end: Position, map_instance: Map, dynamic_obstacles: set[tuple[int, int]] | None = None) -> list[Position] | None:
        """
        Finds a path from start to end using Breadth-First Search on the map's collision grid.
        Returns a list of Position objects representing the path (excluding start, including end).
        Returns None if no path is found.
        """
        start_tile = (int(start.x // GameSettings.TILE_SIZE), int(start.y // GameSettings.TILE_SIZE))
        end_tile = (int(end.x // GameSettings.TILE_SIZE), int(end.y // GameSettings.TILE_SIZE))

        if start_tile == end_tile:
            return []

        # Queue stores (current_tile, path_so_far)
        queue = deque([(start_tile, [])])
        visited = {start_tile}
        
        width = map_instance.tmxdata.width
        height = map_instance.tmxdata.height
        
        # Pre-process static obstacles from Map
        # Accessing protected member _collision_map for performance optimization in BFS
        static_obstacles = set()
        if hasattr(map_instance, '_collision_map'):
            for rect in map_instance._collision_map:
                tx = int(rect.x // GameSettings.TILE_SIZE)
                ty = int(rect.y // GameSettings.TILE_SIZE)
                static_obstacles.add((tx, ty))
        
        # Directions: Up, Down, Left, Right
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        iterations = 0

        while queue:
            iterations += 1
            if iterations > NavigationManager.MAX_ITERATIONS:
                Logger.warning("BFS Max iterations reached. Aborting pathfinding.")
                return None

            (cx, cy), path = queue.popleft()

            if (cx, cy) == end_tile:
                # Convert path of tiles back to Positions (center of tile)
                final_path = []
                for tx, ty in path:
                    # Target center of tile
                    px = tx * GameSettings.TILE_SIZE
                    py = ty * GameSettings.TILE_SIZE
                    final_path.append(Position(px, py))
                return final_path

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                
                # Check bounds
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        # Check dynamic obstacles
                        if dynamic_obstacles and (nx, ny) in dynamic_obstacles:
                            continue

                        # Check static obstacles
                        if (nx, ny) in static_obstacles:
                            continue

                        visited.add((nx, ny))
                        new_path = path + [(nx, ny)]
                        queue.append(((nx, ny), new_path))
                            
        return None
