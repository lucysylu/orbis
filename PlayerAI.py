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
        self.spawned = []
        self.nest_spawn = {}
        self.move_count = 0
        self.goal_nests = 3
        self.is_early_game = True
        self.friendly_nest_distance_importance = 0.25
        self.enemy_nest_distance_importance = 0.25
        self.nest_core_importance = 0.5
        self.target_nests = {}
        self.defense_points = {}
        self.builder_count = 0
        self.nest_build_point;
        self.straight_builders = []
        self.zz_builders = []
        self.steps = 0;

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


    def is_past_mid(self, world):
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

    def nest_fitness(self, friendly_nest_distance, enemy_nest_distance, nesting_core_score, world):
        return (self.friendly_nest_distance_importance * -friendly_nest_distance +
            self.enemy_nest_distance_importance * enemy_nest_distance +
            self.nest_core_importance * nesting_core_score)

    def obtain_best_nest_points(self, world):
        friendly_nest_position = world.get_friendly_nest_positions()[0]
        enemy_nest_position = world.get_enemy_nest_positions()[0]
        best_nests = []

        for tile in world.get_tiles():
            tile_position = tile.position

            friendly_distance = world.get_shortest_path_distance(tile_position, friendly_nest_position)
            enemy_distance = world.get_shortest_path_distance(tile_position, enemy_nest_position)
            nesting_core_score = 0
            if self.is_nesting_core(world, point):
                nesting_core_score = 1
            best_nests.append((tile, nest_fitness(friendly_distance,
                                                  enemy_distance,
                                                  nesting_core_score)))

        best_nests = sorted(best_nests, key=lambda x:x(1))
        overall_best_nests = best_nests[0:self.goal_nests]
        best_nest_dict = {}

        for nest in overall_best_nests:
            nearby_tiles = world.get_neighbours(nest.position)
            best_nest_dict[nest] = nearby_tiles

        return best_nest_dict

    def get_northwestern_point(self, world, point, neighbors):
        northern_point = neighbors[Direction.NORTH]
        western_point = neighbors[Direction.WEST]

        if world.at_edge(point) and world.at_edge(northern_point):
            return (northern_point[0] - 1, northern_point[1])
        else:
            return (western_point[0], western_point[1] + 1)

    def get_northeastern_point(self, world, point, neighbors):
        northern_point = neighbors[Direction.NORTH]
        eastern_point = neighbors[Direction.EAST]

        if world.at_edge(point) and world.at_edge(northern_point):
            return (northern_point[0] + 1, northern_point[1])
        else:
            return (eastern_point[0], eastern_point[1])

    def get_southwestern_point(self, world, point, neighbors):
        southern_point = neighbors[Direction.SOUTH]
        western_point = neighbors[Direction.WEST]

        if world.at_edge(point) and world.at_edge(southern_point):
            return (southern_point[0] - 1, southern_point[1])
        else:
            return (western_point[0], western_point[1] - 1)

    def get_southeastern_point(self, world, point, neighbors):
        southern_point = neighbors[Direction.SOUTH]
        eastern_point = neighbors[Direction.EAST]

        if world.at_edge(point) and world.at_edge(southern_point):
            return (southern_point[0] + 1, southern_point[1])
        else:
            return (eastern_point[0], eastern_point[1] - 1)

    def obtain_defence_points(self, world):
        friendly_nest_positions = world.get_friendly_nest_positions()
        for friendly_nest_position in friendly_nest_positions:
            neighbors = world.get_neighbours(friendly_nest_position)

            northwestern_point = self.get_northwestern_point(world, friendly_nest_position, neighbors)
            northeastern_point = self.get_northeastern_point(world, friendly_nest_position, neighbors)
            southwestern_point = self.get_southwestern_point(world, friendly_nest_position, neighbors)
            southeastern_point = self.get_southeastern_point(world, friendly_nest_position, neighbors)

            self.defense_points[friendly_nest_position] = [northwestern_point, northeastern_point, southwestern_point,
                                                           southeastern_point]

    def builder_scout_two(self, world, unit):



    def zz_move(self, world, unit, goal):
        next = world.get_next_point_in_shortest_path(unit.position, goal)
        if next[0] < unit.position[0]:
            a = -1
        elif next[0] > unit.position[0]:
            a = 1
        else: a = 0

        if next[1] < unit.position[1]:
            b = -1
        elif next[1] > unit.position[1]:
            b = 1
        else:
            b = 0

        if steps == 0:
            world.move(unit, next)
        elif steps == 1:
            world.move(unit, ())





    def scout_move(self, world, unit):

        nests = world.get_friendly_nest_positions()
        if not self.is_past_mid:
            if len(nests) < self.goal_nests and self.builder_count < self.goal_nests:
                self.builder_count += 1
                builder_scout(world, unit)
            else:


    def find_build_point(self, world, unit):
        best_nests = self.obtain_best_nest_points()
        closest = world.get_closest_point_from(unit.position, lambda nest: nest in best_nests)
        return closest

    def find_friendlies(self, world, friendly_units):
        #return a set of friendly positions
        friendly_pos = set()
        for unit in friendly_units:
            friendly_pos.add(unit.position)
        return friendly_pos

    def find_enemies(self, world, enemy_units):
        #return a set of enemy positions
        enemy_pos = set()
        for unit in enemy_units:
            enemy_pos.add(unit.position)
        return enemy_pos

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
        move_count += 1
        for unit in friendly_units:
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, None).position,
                                           None)
            #assign a new firefly to a role

            if unit.uuid not in self.spawned:
                #TODO: Add code for checking if merged
                if (not self.is_past_mid and self.move_count % 2 == 0):
                    self.scouts.append(unit.uuid)
                elif (self.is_past_mid and self.move_count % 2 == 0):
                    self.hunters.append(unit.uuid)
                else:
                    self.defenders.append(unit.uuid)
                self.spawned.append(unit.uuid)

            if unit.uuid in self.spawned:
                if unit.uuid in self.hunters:

                elif unit.uuid in self.scouts:
                    if not self.build_nest_point:
                        self.build_nest_point = self.find_build_point(unit)
                    if unit.uuid not in (self.straight_builders or self.zz_builders):
                        if self.move_count % 3 == 0:
                            self.straight_builders.append(unit.uuid)
                        elif move_count % 3 == 1 or move_count % 3 == 2:
                            self.zz_builders.append(unit.uuid)
                    if self.build_nest_point:

                    if unit.uuid in self.straight_builders:
                        world.move(world.get_next_point_in_shortest_path(unit.position, build_next_point))


                elif unit.uuid in self.defenders:



            if path: world.move(unit, path[0])






