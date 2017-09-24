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
        self.defender_mapping = {}
        self.defender_enemy_attack_threshold = 5

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

            self.defense_points[friendly_nest_position] = {
                northwestern_point:None,
                northeastern_point:None,
                southwestern_point:None,
                southeastern_point:None
            }

def get_closest_friendly_nests(self, world, point):
        friendly_nest_positions = world.get_friendly_nest_positions()
        friendly_nest_tuples = []
        for position in friendly_nest_positions:
            dist = world.get_shortest_path_distance(point, position)
            friendly_nest_tuples.append((position, dist))

        friendly_nest_tuples = sorted(friendly_nest_tuples, key=lambda x:x[1])
        return friendly_nest_tuples

    def should_defender_attack_enemy(self, world, defender):
        if defender.uuid not in self.defender_mapping:
            return False, None

        position_to_defend = self.defender_mapping[defender.uuid]
        closest_enemy = world.get_closest_enemy_from(position_to_defend, None)
        enemy_dist = world.get_shortest_path_distance(defender_position, closest_enemy.position)

        if enemy_dist < self.defender_enemy_attack_threshold:
            return True, closest_enemy
        else:
            return False, None

    def do_defender_move(self, world, defender):
        """

        :param world:
        :param defender: FriendlyUnit
        :return:
        """
        if defender.uuid not in self.defender_mapping:
            defender_position = defender.position
            friendly_nest_tuples = self.get_closest_friendly_nests(world, defender_position)

            assigned = False
            for friendly_nest_tuple in friendly_nest_tuples:
                friendly_nest_position = friendly_nest_tuple[0]
                defense_points = self.defense_points[friendly_nest_position]
                for defense_point in defense_points:
                    if not assigned and defense_points[defense_point] is None:
                        self.defense_points[friendly_nest_position] = defender.uuid
                        self.defender_mapping[defender.uuid] = defense_point
                        assigned = True

            if not assigned:
                closest_defender = self.defenders[0]
                closest_dist = world.get_shortest_path_distance(defender_position, closest_defender.position)
                for other_defender_uuid in self.defenders:
                    other_defender = world.get_unit(other_defender_uuid)
                    other_dist = world.get_shortest_path_distance(defender_position, other_defender.position)
                    if other_dist < closest_dist:
                        closest_defender = other_defender
                        closest_dist = other_dist
                world.move(defender, closest_defender.position)

        should_defender_attack, enemy_unit = should_defender_attack(world, defender)
        if should_defender_attack:
            world.move(defender, enemy_unit.position)
        else:
            world.move(defender, self.defender_mapping[defender.uuid])


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
        self.hunter_pair(world)
        for unit in friendly_units:
            if unit.last_move_result == MoveResult.NEWLY_MERGED:
                parents = []
                for other_unit_uuid in self.spawned:
                    if unit.is_merged_with_unit(other_unit_uuid):
                        parents.append(other_unit_uuid)

                defender_count = 0
                scout_count = 0
                hunter_count = 0

                for parent_uuid in parents:
                    if parent_uuid in self.defenders:
                        defender_count += 1
                    elif parent_uuid in self.scouts:
                        scout_count += 1
                    elif hunter_uuid in self.hunters:
                        hunter_count += 1

                if defender_count >= scout_count and defender_count >= hunter_count:
                    self.defenders.append(unit.uuid)
                elif scout_count >= hunter_count and scout_count >= defender_count:
                    self.scouts.append(unit.uuid)
                else:
                    self.hunters.append(unit.uuid)

            #assign a new firefly to a role
            if unit.uuid not in self.spawned:
                #TODO: Add code for checking if merged
                if (self.is_early_game and self.move_count % 2 == 0):
                    self.scouts.append(unit.uuid)
                elif (not self.is_early_game and self.move_count % 2 == 0):
                    self.hunters.append(unit.uuid)
                else:
                    self.defenders.append(unit.uuid)
                self.spawned.append(unit.uuid)

            if unit.uuid in self.spawned:
                if unit.uuid in self.hunters:
                    self.hunter_move(world, unit, self.hunter_nest_pair)
                elif unit.uuid in self.scouts:

                elif unit.uuid in self.defenders:
                    self.do_defender_move(world, unit)





