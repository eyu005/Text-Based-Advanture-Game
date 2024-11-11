#Eunsang Yu 
#05/27/2024
#Game 3 

import json 
import re 
import sys

# This function takes in a string file_path and it loads 
# the dungeon configuration from a JSON file
def load_dungeon(file_path):
    with open(file_path, 'r') as dungeon_file:
        return json.load(dungeon_file)

# Stop words that do not meaningfully contribute to how the game will proces 
# player input
stop_words = ["a", "an", "and", "are", "as", "at", "be", "but", "the"]

player_location = "entrance"    #Player starting location
Inventory = []                  #Player inventory

# This function takes in a list of inventory and prints the current state of the inventory 
# to the player. If inventory is empty, it notifies the player that inventory is empty. If 
# not empty, it gives the player list of objects that are in the inventory.
def print_inventory(Inventory):
    if Inventory:
        print("Your inverytory: ")
        for item in Inventory:
            print(f"- {item['objID']}")
    else:
        print("Your inventory is empty.")

# This function processes a player's input string, removing common 
# stop words, and converting the remaining words to uppercase. It is useful for 
# standardizing user commands, makking it easier to pares and execute them in the game. 
def take_input(player_input):
    words = []
    for word in re.findall(r'\b\w+\b', player_input):
        if word.lower() not in stop_words:
            words.append(word.upper())
    return words

# This function prints a list of object names present in the current room of the dungeon. 
# It helps players to know what objects are available for interaction in their current location.
def print_room_description(dungeon):
    object_names = [obj['objID'] for obj in dungeon[player_location].get('objects', [])]
    if object_names:
        print("You see the following objects:")
        for name in object_names:
            print(f"- {name}")

# This function processes a command for the player to move in a specified direction 
# within the dungeon. It updates the player's location if the move is valid. 
# It takes two parameters, words and dungeon 
def command_GO(words, dungeon):
    global player_location
    direction_map = {'N': 'north', 'S': 'south', 'E': 'east', 'W': 'west'}

    if len(words) > 1:
        direction = words[1].upper()
        if direction in direction_map:
            direction = direction_map[direction]
        else:
            direction = direction.lower()
        new_location = dungeon[player_location].get(direction)
        if new_location:
            player_location = new_location
            print(f"You moved {direction} to the {player_location}.")
            print_room_description(dungeon)
        else:
            print("You can't go that direction.")
    else:
        print("Specify a direction to go.")
    print_inventory(Inventory)
    print("\n")

# This function processes a command for the player to take an object from the current 
# room and add it to their inventory. It updates the game state by removing the object from the 
# room and adding ti to the player's inventory if the action is allowed. 
def command_TAKE(words, dungeon):
    global player_location

    if len(words) > 1:
        obj_id = words[1].lower()
        room_objects = dungeon[player_location].get('objects', [])
        for obj in room_objects:
            if obj['objID'] == obj_id:
                if 'TAKE' in obj.get('interactions', []):
                    Inventory.append(obj)
                    room_objects.remove(obj)
                    print(f"You took the {obj_id}.")

                    if obj_id == "treasure":
                        print("Congratulations! You found the hidden treasure and won the game")
                        sys.exit(0)
                else:
                    print("Can't take this object.")
                break
        else:
            print("Can't take this object.")
    else:
        print("Specify an object to take.")
    print_inventory(Inventory)
    print("\n")

# This function processes a command for the player to look at an object or direction in the current room.
# It provides description of the objects or the next room in the specified direciton, updating the game 
# state. 
def command_LOOK(words, dungeon):
    global player_location

    if len(words) > 1:
        direction_or_obj = words[1].lower()
        if direction_or_obj in {'north', 'south', 'east', 'west'}:
            next_room = dungeon[player_location].get(direction_or_obj)
            if next_room:
                print(f"To the {direction_or_obj}, you see the {next_room}.")
            else:
                print("Nothing in that direction.")
        else:
            for obj in dungeon[player_location].get('objects', []):
                if obj['objID'].lower() == direction_or_obj:
                    if 'LOOK' in obj.get('interactions', []):
                        print(obj['description'])
                        break
            else:
                print("Nothing to see here.")
    else:
        print(dungeon[player_location]['description'])
    print_inventory(Inventory)
    print("\n")

# This function processes a command for the player to open an object in the current room.
# It checks if the object can be opened and updates the game state. 
def command_OPEN(words, dungeon):
    global player_location

    if len(words) > 1:
        obj_ID = words[1].lower()
        found = False
        for obj in dungeon[player_location].get('objects', []):
            if obj['objID'].lower() == obj_ID and 'OPEN' in obj['interactions']:
                found = True
                if 'locked' in obj and obj['locked'] == 'LOCKED':
                    print(f"{obj_ID} is currently locked")
                else:
                    print(f"You opened {obj_ID}")
                break
        if not found:
            print(f"Cannot open this object")
    else:
        print('Specify an object to open')
    print_inventory(Inventory)
    print("\n")

# This function processes a command for the player to use an object, either on another 
# object or by itself, in the current room. It provides feedback based on whether an 
# object can be used or not. It then updates the game state. 
def command_USE(words, dungeon):
    global player_location

    if len(words) > 2:
        obj_id1 = words[1].lower()
        obj_id2 = words[2].lower()

        print(f"You used {obj_id1} on the {obj_id2}")
    elif len(words) > 1:
        obj_id = words[1].lower()
        for obj in dungeon[player_location].get('objects', []):
            if obj['objID'].lower() == obj_id and 'USE' in obj['interactions']:
                print(f"You used the {obj_id}")
                break
        else:
            print("Nothing happens")
    else:
        print("Specify an object to use")
    print_inventory(Inventory)
    print("\n")

# This function takes in player's input command and delegates the 
# appropriate action to other command functions. 
def play_game(words, dungeon):
    if not words:
        return
    
    verb = words[0]

    if verb == "GO":
        command_GO(words, dungeon)
    elif verb == "TAKE":
        command_TAKE(words, dungeon)
    elif verb == "LOOK":
        command_LOOK(words, dungeon)
    elif verb == "OPEN":
        command_OPEN(words, dungeon)
    elif verb == "USE":
        command_USE(words, dungeon)

# Print instructions at the start of the game
def print_instructions():
    print("Welcome to the Dungeon Treasure Hunt!")
    print("Your goal is to find the hidden treasure!\n")
    print("Dungeon keys:", dungeon.keys(),"\n")    
    print("You can use the following commands: \n")
    print("Go <direction> - Allows you to move from one room to another")
    print("TAKE <object> - Allows you to put an object in your inventory")
    print("OPEN <object> - Allows you to open up an object(typically a door)")
    print("USE <object> (<object>) - Allows you to interact with an object in the room")
    print("LOOK <direction> | <object> | <nothing> - If given an object, object's description is printed.")
    print("                                          If given a direction, the name of the room in that direction is given")

if __name__=="__main__":
    #If the length of the argument to run the program is less than 2, 
    #it notifies the player to provide proper command to run the game. 
    if len(sys.argv) != 2:
        print("Usage: python3 game.py <dungeon_file.json>")
        sys.exit(1)
    
    dungeon_file = sys.argv[1]
    dungeon = load_dungeon(dungeon_file)

    global plyaer_location
    # Checking if the starting state is entrance. 
    # If not, then the game is starting at location provided 
    # in the json file. 
    if 'entrance' in dungeon:
        player_location = 'entrance'
    else:
        player_location = list(dungeon.keys())[0]
        print(f"starting at {player_location}")

    print_instructions()
    print("Starting location:", player_location)
    print_room_description(dungeon)
# Game loop
while True:
    player_input = input("Type your command: ")
    words = take_input(player_input)
    play_game(words, dungeon)
