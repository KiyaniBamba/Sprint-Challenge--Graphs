from room import Room
from player import Player
from world import World

import random
from ast import literal_eval

class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None

    def size(self):
        return len(self.queue)

class Stack():
    def __init__(self):
        self.stack = []
    def push(self, value):
        self.stack.append(value)
    def pop(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            return None
    def size(self):
        return len(self.stack)


# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player("name", world.starting_room) # start 

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []

player_map={0:{}}
for direction in world.starting_room.get_exits():
    player_map[0][direction] = '?' # initialiser

def unexplored_rooms_down_path(origin, starting_direction, ghost_explorer = None, visited = None):
        
        # If that room is not in the players map AND has not been visited by this DFT...
            # Mark it as visited and increment the unexplored rooms count                
            # Then send a new ghost explorer down each of the potential connected rooms
                # But only if that direction exists and if the room that way has not been visited
                
        room_total = 0
        if ghost_explorer is None:
            ghost_explorer = Player("BOO", player.current_room)
        if visited is None:
            visited = set()
        ghost_explorer.travel(starting_direction)
        r = ghost_explorer.current_room.id
        if r is origin:
            return 0
        if r not in player_map and r not in visited:
            visited.add(r)
            room_total += 1
            for d in ['n', 'e', 's', 'w']:
                if ghost_explorer.current_room.get_room_in_direction(d) is not None and ghost_explorer.current_room.get_room_in_direction(d) not in visited:
                    ghost_copy = Player("Copy", ghost_explorer.current_room)
                    room_total += unexplored_rooms_down_path(r, d, ghost_copy, visited)
        return room_total


def explore_shortest():
    """
    Checks the potential paths from the current room, returns the direction that contains
    the fewest (but non-zero) number of unexplored rooms down that path.
    In the larger graph where many room paths are interconnected, a shorter number typically
    denotes a dead end branch which is more efficient to traverse the first time you see it
    """
    results = set()
    current = player.current_room
    direction = current.get_exits()

    for d in direction:
        next_room = current.get_room_in_direction(d)
        unexplored = unexplored_rooms_down_path(current.id, d)
        if unexplored > 0:
            results.add((d, unexplored))
    if len(results) > 0:
        return min(results, key = lambda t: t[1])[0]
    else:
        return None

def bfs_for_unexplored():
    """
    Performs BFS to find shortest path to room with unexplored exit from current location
    Returns the first path to meet this criteria
    """
    # Create an empty queue and enqueue a PATH to the current room
    q = Queue()
    q.enqueue([player.current_room.id])
    # Create a Set to store visited rooms
    v = set()

    while q.size() > 0:
        p = q.dequeue()
        last_room = p[-1]
        if last_room not in v:
            # Check if it has unexplored rooms
            if '?' in list(player_map[last_room].values()):
                # >>> IF YES, RETURN PATH (excluding starting room) so player can go travel shortest path to room with unexplored exit
                return p[1:]
            # Else mark it as visited
            v.add(last_room)
            # Then add a PATH to its neighbors to the back of the queue
            for direction in player_map[last_room]:
                path_copy = p.copy()
                path_copy.append(player_map[last_room][direction])
                q.enqueue(path_copy)

def origin(direction):
    """
    Small util function returning the opposite of a direction
    used in quickly determining the origin direction when a player arrives in a new room
    """
    opposite = {"n": "s", "e": "w", "s": "n", "w": "e"}
    return opposite[direction]

def dft_for_dead_end():
        
    while '?' in list(player_map[player.current_room.id].values()):
        current_id = player.current_room.id
        unexplored_rooms =[]
        for key, val in list(player_map[player.current_room.id].items()):
            if val == '?':
                unexplored_rooms.append(key)
        if len(unexplored_rooms) == 1:
            next_dir = unexplored_rooms[0]
        else:
            next_dir = explore_shortest()
            if next_dir == None:
                break
        player_map[player.current_room.id][next_dir] = player.current_room.get_room_in_direction(next_dir).id
        traversal_path.append(next_dir)
        player.travel(next_dir)
        if player.current_room.id not in player_map:
            player_map[player.current_room.id] = {}
        if len(player_map[player.current_room.id]) <1:
            for direction in player.current_room.get_exits():
                player_map[player.current_room.id][direction] = '?'
        player_map[player.current_room.id][origin(next_dir)] = current_id

def travel_to_nearest_unexplored():
    """
    Once a room with no unexplored exits is reached, run a BFS to find 
    the shortest path to a room with an unexplored exit for each room in 
    that path, then move that direction and log the movement in the traversal path
    """

    bfs_path = bfs_for_unexplored()
    while bfs_path is not None and len(bfs_path) > 0:
        next_room = bfs_path.pop(0)
        next_direction = next((k for k, v in player_map[player.current_room.id].items() if v == next_room), None)
        traversal_path.append(next_direction)
        player.travel(next_direction)


def populate_traversal_path():
    """
    While the player's map is shorter than the number of rooms, continue looping
    through DFT until a dead end OR already fully-explored room is found,
    then perform BFS to find shortest path to room with unexplored path and go there
    """
    while len(player_map) < len(room_graph):      
        dft_for_dead_end()
        travel_to_nearest_unexplored()

# # The actual maze traversal function
populate_traversal_path()


# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
