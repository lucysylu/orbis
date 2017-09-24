from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.walls = []
        self.cores = []
        self.hunters = []
        self.defenders = []
        self.scouts = []
        self.closed = False
        self.hunter_nest_pairs = {}

    def check_walls(self, world):

        #check type of map, find nesting cores
        x = world.get_width()
        y = world.get_height()
        wall_count = 0
        for i in x:
            for j in y:
                point = (i, j)
                if world.is_wall(point):
                    self.walls.append(point)
                    if world.is_edge(point):
                        wall_count += 1

                if self.is_nesting_core(world, point):
                    self.cores.append(point)

        if wall_count == (x * 2 + y * 2 - 4):
            self.closed = True

    def is_nesting_core(self, world, point):
        neighbours = world.get_neighbours(point)
        wall_count = 0
        for key in neighbours:
            if world.is_wall(neighbours[key]):
                wall_count += 1
        if wall_count == 3:
            return True
        else: return False


    def is_mid(self, world):
        #checks if a third of tiles are taken or if enemy gets close to nests
        x = world.get_width()
        y = world.get_height()

        tile_count = 0
        for i in x:
            for j in y:
                point = (i, j)
                if not point.is_neutral():
                    tile_count += 1
        if tile_count/(x * y) >= 0.33:
            return True
        else: return False


    def hunter_pair(self, world):
        #assigns a nest to each hunter
        nests = world.get_enemy_nest_positions()
        clusters = world.get_enemy_nest_clusters()

        for hunter in self.hunters:
            closest_nest = world.get_closest_enemy_nest_from(hunter.position)
            self.hunter_nest_pair[hunter] = closest_nest
            if closest_nest not in clusters:
                nests.remove(closest_nest)


    def hunter_move(self, world, unit, hunter_nest_pairs):
        #activates mid-game, goes straight for nests
        self.hunter_pair(world)
        next_point = world.get_next_point_in_shortest_path(self.hunter_pair[unit.uuid])
        world.move(unit, next_point)



    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.
        
        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world
        for unit in friendly_units:
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, None).position,
                                           None)

            if path: world.move(unit, path[0])






