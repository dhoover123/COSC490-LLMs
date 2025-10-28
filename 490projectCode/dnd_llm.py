import random
import json
from openai import OpenAI
from config2 import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, SITE_URL, SITE_NAME
import sys
from io import StringIO
import time
from functools import wraps

def time_api_call(func):
    """Decorator to time API calls and print the duration"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nAPI Call Duration ({func.__name__}): {duration:.2f} seconds")
        return result
    return wrapper

# Initialize OpenAI client with OpenRouter
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

@time_api_call
def call_deepseek_api(prompt):
    """Helper function to call OpenRouter API using OpenAI SDK"""
    if OPENROUTER_API_KEY == "your_api_key_here":
        print("Error: Please set your OpenRouter API key in config.py")
        return None

    try:
        completion = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

def roll_dice(sides=20, rolls=1):
    """Roll dice with specified number of sides and rolls"""
    return [random.randint(1, sides) for _ in range(rolls)]

def roll_luck_check():
    """Roll a d15 for story-based luck checks"""
    return roll_dice(15)[0]

class Character:
    def __init__(self, name, hp, attack, defense, skills, inventory, description=""):
        self.name = name
        self.max_hp = hp  # Add max_hp to track maximum health
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.skills = skills
        self.inventory = inventory
        self.description = description  # Add description attribute

    def take_damage(self, damage):
        actual_damage = damage
        self.hp -= actual_damage
        if self.hp <= 0:
            print(f"{self.name} has been defeated!")
        else:
            print(f"{self.name} takes {actual_damage} damage! (HP: {self.hp})")

    def heal(self, amount):
        """Heal the character, ensuring it doesn't exceed max_hp."""
        self.hp = min(self.hp + amount, self.max_hp)  # Respect max_hp
        print(f"{self.name} heals for {amount} HP! (Current HP: {self.hp})")

    def attack_target(self, target, attacker_type="player"):
        hit_roll = random.randint(1, 4)
        if hit_roll != 4:
            damage = random.randint(1, 20)
            print(f"{attacker_type.capitalize()}: {self.name} attacks {target.name} for {damage} damage!")
            target.take_damage(damage)
        else:
            print(f"{attacker_type.capitalize()}: {self.name}'s attack misses!")

    def use_skill(self, skill, target=None):
        # Call the API to determine the effect of the skill
        @time_api_call
        def get_skill_effect():
            prompt = f"""
            In the context of a D&D game, determine the effect of the skill "{skill}" used by {self.name}.
            The skill should either damage an enemy, heal the player, or have a descriptive effect.
            Return a JSON response with the following format:
            {{
                "effect": "damage|heal|description",
                "description": "A short description of the effect"
            }}
            """
            return call_deepseek_api(prompt)

        response = get_skill_effect()
        if response:
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                effect_data = json.loads(response)
                effect = effect_data.get("effect")
                description = effect_data.get("description", "Unknown effect")

                print(f"\n{self.name} uses {skill}!")
                print(f"Effect: {description}")

                if effect == "damage":
                    hit_roll = random.randint(1, 4)  # 1-3 hit, 4 miss
                    if hit_roll != 4:
                        amount = random.randint(1, 20)  # Random damage between 1 and 20
                        if target:
                            target.take_damage(amount)
                            print(f"Deals {amount} damage to {target.name}!")
                        else:
                            print("No target selected for damage skill!")
                    else:
                        print(f"{self.name}'s skill misses!")
                elif effect == "heal":
                    hit_roll = random.randint(1, 4)  # 1-3 hit, 4 miss
                    if hit_roll != 4:
                        amount = random.randint(1, 20)  # Random heal between 1 and 20
                        if target:
                            target.heal(amount)
                        else:
                            self.heal(amount)
                    else:
                        print(f"{self.name}'s skill fails to heal!")
                elif effect == "description":
                    # Just describe the effect, no damage or healing
                    pass
                else:
                    print("Skill has no effect!")

            except json.JSONDecodeError as e:
                print(f"Error parsing skill effect: {e}")

    def use_item(self, item, target=None):
        """Use an item from the inventory."""
        if item not in self.inventory:
            print(f"{self.name} does not have {item} in their inventory!")
            return 0

        @time_api_call
        def get_item_effect():
            # Call the API to determine the effect of the item
            prompt = f"""
            In the context of a D&D game, determine the effect of the item "{item}" used by {self.name}.
            The item should either damage an enemy, heal the player, or have a descriptive effect.
            Return a JSON response with the following format:
            {{
                "effect": "damage|heal|description",
                "description": "A short description of the effect"
            }}
            """
            return call_deepseek_api(prompt)

        response = get_item_effect()
        if response:
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                effect_data = json.loads(response)
                effect = effect_data.get("effect")
                description = effect_data.get("description", "Unknown effect")

                print(f"\n{self.name} uses {item}!")
                print(f"Effect: {description}")

                if effect == "damage":
                    hit_roll = random.randint(1, 4)  # 1-3 hit, 4 miss
                    if hit_roll != 4:
                        amount = random.randint(1, 20)  # Random damage between 1 and 20
                        if target:
                            target.take_damage(amount)
                            print(f"Deals {amount} damage to {target.name}!")
                        else:
                            print("No target selected for damage item!")
                        return amount  # Return damage to be applied to the enemy
                    else:
                        print(f"{self.name}'s item misses!")
                        return 0
                elif effect == "heal":
                    hit_roll = random.randint(1, 4)  # 1-3 hit, 4 miss
                    if hit_roll != 4:
                        amount = random.randint(1, 20)  # Random heal between 1 and 20
                        if target:
                            target.heal(amount)
                        else:
                            self.heal(amount)
                        return amount  # Return heal amount
                    else:
                        print(f"{self.name}'s item fails to heal!")
                        return 0
                elif effect == "description":
                    # Just describe the effect, no damage or healing
                    return 0
                else:
                    print("Item has no effect!")
                    return 0

            except json.JSONDecodeError as e:
                print(f"Error parsing item effect: {e}")
                return 0
        return 0

class Enemy:
    def __init__(self, name, hp, attack, defense, skills, inventory, reward):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.skills = skills
        self.inventory = inventory
        self.reward = reward

    def take_damage(self, damage):
        actual_damage = damage
        self.hp -= actual_damage
        if self.hp <= 0:
            print(f"{self.name} has been defeated!")
        else:
            print(f"{self.name} takes {actual_damage} damage! (HP: {self.hp})")

    def attack_target(self, game):
        """Attack a random target (player or companion)."""
        # Combine players and companions into a single list of potential targets
        targets = game.players + game.companions
        # Filter out targets with HP <= 0
        active_targets = [target for target in targets if target.hp > 0]

        if not active_targets:
            print(f"{self.name} has no valid targets!")
            return

        # Randomly choose a target
        target = random.choice(active_targets)
        hit_roll = random.randint(1, 4)
        if hit_roll != 4:
            damage = random.randint(1, 20)
            print(f"Enemy: {self.name} attacks {target.name} for {damage} damage!")
            target.take_damage(damage)
        else:
            print(f"Enemy: {self.name}'s attack misses!")

class Game:
    def __init__(self):
        self.players = []
        self.npcs = []
        self.story_log = []
        self.current_turn = 0
        self.story_type = ""
        self.quest_log = []
        self.companions = []
        self.current_location = ""
        self.story_data = None
        self.discoveries = []  # Store discoveries for consistent exploration
        self.encounters = []  # Initialize encounters list
        self.actions = []  # Initialize actions list
        self.combat_description = None  # Store the combat description
        self.completed_combats = set()  # Track which locations have completed combat

    def add_player(self, player):
        """Add a player to the game"""
        self.players.append(player)

    def start_game(self):
        print("\nWelcome to the Dynamic D&D Adventure Generator!")
        print("\nPlease describe the type of story you'd like to experience.")
        print("Example: 'A dark fantasy story about hunting vampires in a medieval city'")
        print("or 'A lighthearted adventure about helping magical creatures in an enchanted forest'")

        self.story_type = input("\nYour story premise: ").strip()
        if not self.story_type:
            print("Story premise cannot be empty. Please try again.")
            return

        # Generate story elements and characters
        print("\nGenerating your adventure...")
        self.story_data = self.generate_story_elements()
        if not self.story_data:
            print("Failed to generate story elements. Please try again.")
            return

        # Create a single player
        print("\nChoose your character:")

        # Display available characters
        print("\nAvailable characters:")
        for j, char in enumerate(self.story_data["character_options"], 1):
            print(f"\n{j}. {char['name']}")
            print(f"Description: {char['description']}")
            print(f"HP: {char['hp']}")
            print(f"Attack: {char['attack']}")
            print(f"Defense: {char['defense']}")
            print("Skills:", ", ".join(char['skills']))
            print("Starting items:", ", ".join(char['inventory']))

        # Let player choose their character
        while True:
            try:
                choice = int(input(f"\nEnter your choice (1-{len(self.story_data['character_options'])}): "))
                if 1 <= choice <= len(self.story_data["character_options"]):
                    char_data = self.story_data["character_options"][choice - 1]
                    player = Character(
                        name=char_data["name"],
                        hp=char_data["hp"],
                        attack=char_data["attack"],
                        defense=char_data["defense"],
                        skills=char_data["skills"],
                        inventory=char_data["inventory"],
                        description=char_data["description"]
                    )
                    self.add_player(player)
                    print(f"\nPlayer created: {player.name}")
                    break
                print(f"Please enter a number between 1 and {len(self.story_data['character_options'])}.")
            except ValueError:
                print("Please enter a valid number.")

        # Ensure 3 companions are created
        if len(self.companions) < 3:
            print("\nGenerating additional companions...")
            while len(self.companions) < 3:
                companion_data = self.story_data["companions"][len(self.companions)]
                companion = Character(
                    name=companion_data["name"],
                    hp=companion_data["hp"],
                    attack=companion_data["attack"],
                    defense=companion_data["defense"],
                    skills=companion_data["skills"],
                    inventory=companion_data["inventory"],
                    description=companion_data["description"]
                )
                self.companions.append(companion)
                print(f"Companion {len(self.companions)} created: {companion.name}")

        # Begin the adventure
        print("\nYour adventure begins...")
        print(f"\n{self.story_data['setting']}")
        print("\nMain Quest:", self.story_data["quests"]["main_quest"]["title"])
        print(self.story_data["quests"]["main_quest"]["description"])

        # Start the main game loop
        self.main_game_loop()

    @time_api_call
    def generate_story_elements(self, retries=3):
        # Generate story-appropriate characters, locations, and quests using the API
        prompt = f"""
        Based on the story premise: "{self.story_type}"
        Generate a JSON response containing:
        1. A detailed world setting
        2. Available character options that fit the theme (3-4 characters)
        3. Main quest and 2-3 side quests, each tied to a specific location
        4. Key locations (5 total: starting area, 3 side areas, and final area)
        5. Potential companions (2-3)

        Format the response as:
        {{
            "setting": "detailed world description",
            "locations": ["starting_area", "side_area_1", "side_area_2", "side_area_3", "final_area"],
            "character_options": [{{
                "name": "",
                "description": "",
                "hp": number,
                "attack": number,
                "defense": number,
                "skills": ["skill1", "skill2", ...],
                "inventory": ["item1", "item2", ...]
            }}],
            "quests": {{
                "main_quest": {{
                    "title": "",
                    "description": "",
                    "objectives": ["obj1", "obj2", ...],
                    "location": "final_area"
                }},
                "side_quests": [{{
                    "title": "",
                    "description": "",
                    "objectives": ["obj1", "obj2", ...],
                    "location": "side_area_1"
                }}, {{
                    "title": "",
                    "description": "",
                    "objectives": ["obj1", "obj2", ...],
                    "location": "side_area_2"
                }}, {{
                    "title": "",
                    "description": "",
                    "objectives": ["obj1", "obj2", ...],
                    "location": "side_area_3"
                }}]
            }},
            "companions": [{{
                "name": "",
                "description": "",
                "hp": number,
                "attack": number,
                "defense": number,
                "skills": ["skill1", "skill2", ...],
                "inventory": ["item1", "item2", ...]
            }}]
        }}
        """
        for attempt in range(retries):
            response = call_deepseek_api(prompt)
            if response:
                try:
                    # Clean the response by removing markdown code blocks if present
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0].strip()

                    # Ensure the response is complete JSON
                    if not response.endswith("}"):
                        response += "}"

                    self.story_data = json.loads(response)

                    # Validate required fields
                    required_fields = ["setting", "locations", "character_options", "quests", "companions"]
                    for field in required_fields:
                        if field not in self.story_data:
                            raise ValueError(f"Missing required field: {field}")

                    # Validate and ensure all required fields are present in character_options
                    for char in self.story_data["character_options"]:
                        # Ensure all required fields are present
                        if "name" not in char:
                            char["name"] = "Unknown Character"
                        if "description" not in char:
                            char["description"] = "A mysterious adventurer."
                        if "hp" not in char:
                            char["hp"] = 20  # Default HP
                        if "attack" not in char:
                            char["attack"] = 5  # Default attack
                        if "defense" not in char:
                            char["defense"] = 5  # Default defense
                        if "skills" not in char:
                            char["skills"] = ["Slash", "Shield Block"]  # Default skills
                        if "inventory" not in char:
                            char["inventory"] = ["Sword", "Shield"]  # Default inventory

                    # Set the starting area (no quest or combat)
                    self.current_location = self.story_data["locations"][0]
                    # Initialize quest log with main quest and side quests
                    self.quest_log = [self.story_data["quests"]["main_quest"]] + self.story_data["quests"]["side_quests"]

                    # Convert companions to Character objects
                    self.companions = []
                    for companion_data in self.story_data["companions"]:
                        companion = Character(
                            name=companion_data["name"],
                            hp=companion_data["hp"],
                            attack=companion_data["attack"],
                            defense=companion_data["defense"],
                            skills=companion_data["skills"],
                            inventory=companion_data["inventory"],
                            description=companion_data["description"]
                        )
                        self.companions.append(companion)

                    return self.story_data  # Return the story data instead of True
                except json.JSONDecodeError as e:
                    print(f"Error parsing story elements (Attempt {attempt + 1}/{retries}): {e}")
                except ValueError as e:
                    print(f"Error in story data (Attempt {attempt + 1}/{retries}): {e}")
            else:
                print(f"Failed to get a response from the API (Attempt {attempt + 1}/{retries}).")

        print("Failed to generate story elements after multiple attempts. Please try again.")
        return None

    def generate_character_options(self, prompt):
        """Generate character options based on the story context"""
        characters = []
        for char_data in self.generate_story_elements():
            try:
                character = Character(
                    name=char_data["name"],
                    hp=char_data["hp"],
                    attack=char_data["attack"],
                    defense=char_data["defense"],
                    skills=char_data["skills"],
                    inventory=char_data["inventory"],
                    description=char_data["description"]
                )
                characters.append(character)
            except KeyError as e:
                print(f"Error creating character: Missing {e} data")
            return characters

    @time_api_call
    def generate_npcs(self, context):
        """Generate NPCs based on the story context"""
        prompt = f"""
        Based on the context: "{context}"
        Generate 2-3 NPCs in JSON format:
        [{{
            "name": "",
            "hp": number,
            "attack": number,
            "defense": number,
            "skills": ["skill1", "skill2", ...],
            "inventory": ["item1", "item2", ...]
        }}]
        """
        response = call_deepseek_api(prompt)
        if response:
            try:
                npc_data = json.loads(response)
                npcs = []
                for data in npc_data:
                    npc = Character(
                        name=data["name"],
                        hp=data["hp"],
                        attack=data["attack"],
                        defense=data["defense"],
                        skills=data["skills"],
                        inventory=data["inventory"],
                        description=data["description"]
                    )
                    npcs.append(npc)
                return npcs
            except json.JSONDecodeError as e:
                print(f"Error parsing NPC data: {e}")
                return []
        return []

    def check_combat_end(self):
        """Check if combat has ended"""
        if not any(p.hp > 0 for p in self.players):
            print("\nAll players have been defeated!")
            return True
        if not any(n.hp > 0 for n in self.npcs):
            print("\nAll enemies have been defeated!")
            return True
        return False

    def confirm_exit(self):
        """Confirm if player wants to exit the game"""
        confirm = input("\nAre you sure you want to exit? (y/n): ")
        return confirm.lower() == 'y'

    def present_choice(self, choices):
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(choices):
                    return choice
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")

    def travel(self):
        """Handle travel between locations"""
        if not hasattr(self, 'all_locations'):
            quest_locations = set()
            for quest in self.quest_log:
                # Strip any additional text from the location name
                location = quest["location"].split(" (")[0]  # Remove everything after " ("
                quest_locations.add(location)
            quest_locations.add(self.story_data["locations"][0])
            self.all_locations = list(quest_locations)
            final_area = self.story_data["locations"][-1]
            # Add the final area without the suffix to the list
            self.all_locations[self.all_locations.index(final_area)] = final_area

        choices = [f"Stay in {self.current_location.title()}"] + [loc for loc in self.all_locations if loc != self.current_location]
        print("\nWhere would you like to go?")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice.title()}")

        choice = self.present_choice(choices)

        if choice == 1:
            print(f"\nYou choose to stay in {self.current_location.title()}.")
        else:
            selected_location = choices[choice - 1]
            # Check if the selected location is the final area
            if selected_location == self.story_data["locations"][-1]:
                # Check if all side quests are completed
                side_quests = [q for q in self.quest_log if q != self.story_data["quests"]["main_quest"]]
                if side_quests:
                    print("\nYou must complete all side quests before traveling to the final area!")
                    return
            self.current_location = selected_location.title()
            print(f"\nTraveling to {self.current_location}...")

            # Reset all exploration-related attributes
            self.discoveries = []
            self.encounters = []
            self.actions = []
            self.combat_description = None

            # Generate content for the new location immediately
            self.explore_location()
            return

    def view_quests(self):
        """Display current quests"""
        print("\nQuest Log:")
        for quest in self.quest_log:
            print(f"\n{quest['title']}")
            print(f"Description: {quest['description']}")
            print("Objectives:")
            for obj in quest['objectives']:
                print(f"- {obj}")

    def interact_with_companions(self):
        """Handle companion interactions"""
        if not self.companions:
            print("\nNo companions available.")
            return

        print("\nAvailable companions:")
        for i, companion in enumerate(self.companions, 1):
            print(f"{i}. {companion.name} - {companion.description}")

        choice = self.present_choice([c.name for c in self.companions])
        companion = self.companions[choice - 1]

        print(f"\nTalking with {companion.name}...")
        prompt = f"Generate a dialogue response for {companion.name} based on their description: {companion.description}"
        response = call_deepseek_api(prompt)
        if response:
            print(f"\n{companion.name}: {response}")

    def rest(self):
        """Handle resting and healing for players and companions"""
        heal_amount = 50
        # Heal players
        for player in self.players:
            player.hp = min(player.hp + heal_amount, player.max_hp)
            print(f"\n{player.name} rests and recovers {heal_amount} HP. (Current HP: {player.hp})")

        # Heal companions
        for companion in self.companions:
            companion.hp = min(companion.hp + heal_amount, companion.max_hp)
            print(f"{companion.name} rests and recovers {heal_amount} HP. (Current HP: {companion.hp})")

    def check_inventory(self):
        """Display inventory for all players"""
        for player in self.players:
            print(f"\n{player.name}'s inventory:")
            for item in player.inventory:  # Iterate over the list of items
                print(f"- {item}")  # Simply print each item

    def display_combat_status(self):
        """Display current health status of all combatants"""
        print("\nCurrent Combat Status:")
        print("-" * 30)
        print("Players:")
        for player in self.players:
            print(f"{player.name}: {player.hp}/{player.max_hp} HP")
        print("\nCompanions:")
        for companion in self.companions:
            print(f"{companion.name}: {companion.hp}/{companion.max_hp} HP")
        print("")
        for enemy in self.npcs:
            if enemy.hp > 0:
                print(f"{enemy.name}: {enemy.hp} HP")
        print("-" * 30)

    def main_game_loop(self):
        try:
            # Initialize combat log
            self.combat_log = []

            while True:
                # Check if all players are defeated
                if not any(p.hp > 0 for p in self.players):
                    print("\nAll players have been defeated! Game over.")
                    break

                # Display current status
                print(f"\nLocation: {self.current_location}")
                self.story_log.append(f"Location: {self.current_location}")
                print("Current Quests:")
                self.story_log.append("Current Quests:")
                for quest in self.quest_log:
                    print(f"- {quest['title']}: {quest['description']} (Location: {quest['location']})")
                    self.story_log.append(f"- {quest['title']}: {quest['description']} (Location: {quest['location']})")

                # Add a line of space between quests and options
                print()

                # Initialize choices list
                choices = [
                    "Travel to new location",
                    "Check quest log",
                    "Talk to companions",
                    "Rest and heal",
                    "Check inventory",
                    "Exit game"
                ]

                # Add "Explore current location" only if discoveries or encounters are not available
                if not (hasattr(self, 'discoveries') and (self.discoveries or self.encounters)):
                    choices.insert(0, "Explore current location")

                # Add "Interact with environment" option only if discoveries or encounters are available
                if hasattr(self, 'discoveries') and (self.discoveries or self.encounters):
                    choices.insert(0, "Interact with environment")

                # Display action choices
                for i, choice in enumerate(choices, 1):
                    print(f"{i}. {choice}")
                    self.story_log.append(f"{i}. {choice}")

                choice = self.present_choice(choices)

                if choice == 1 and "Interact with environment" in choices:
                    self.interact_with_environment()
                elif choice == 1 and "Explore current location" in choices:
                    self.explore_location()
                elif choice == 2:
                    self.travel()
                elif choice == 3:
                    self.view_quests()
                elif choice == 4:
                    self.interact_with_companions()
                elif choice == 5:
                    self.rest()
                elif choice == 6:
                    self.check_inventory()
                elif choice == 7 and "Exit game" in choices:
                    if self.confirm_exit():
                        break

        except KeyboardInterrupt:
            print("\nGame terminated by user.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try running the game again.")

    @time_api_call
    def interact_with_environment(self):
        """Allow the player to interact with the environment, including initiating combat"""
        if not self.discoveries and not self.encounters:
            print("\nYou have done everything in this area.")
            return

        print("\nInteract with the environment:")
        options = []

        # Add combat first if available and not completed for this location
        if self.encounters and self.current_location not in self.completed_combats:
            if not self.combat_description:
                prompt = f"""
                In the context of the story premise "{self.story_type}", describe the combat encounter with the following enemy in one sentence:
                Enemy: {self.encounters[0]}
                """
                response = call_deepseek_api(prompt)
                if response:
                    self.combat_description = response
                else:
                    self.combat_description = f"Initiate combat: {self.encounters[0]}"

            options.append(f"Initiate combat: {self.combat_description}")

        # Add discoveries after combat
        options.extend(self.discoveries)

        # Add an option to back out
        options.append("Back to main menu")

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        choice = self.present_choice(options)
        selected_option = options[choice - 1]

        if selected_option == "Back to main menu":
            print("\nReturning to the main menu...")
            return
        elif selected_option.startswith("Initiate combat"):
            print("\nYou choose to initiate combat!")
            enemies = self.generate_enemy()
            if enemies:
                self.handle_combat(enemies)
                self.completed_combats.add(self.current_location)  # Mark this location's combat as completed
                self.encounters = []
                # Complete the quest after combat
                self.complete_quest(self.current_location)
        else:
            print(f"\nYou choose to interact with: {selected_option}")
            prompt = f"""
            In the context of the story premise "{self.story_type}", describe the interaction with the following discovery in a few sentences:
            Discovery: {selected_option}
            """
            response = call_deepseek_api(prompt)
            if response:
                print(f"\n{response}")

            # Remove the discovery from the list after interaction
            self.discoveries.remove(selected_option)

            # Complete the quest after first interaction
            self.complete_quest(self.current_location)

            return

    @time_api_call
    def generate_enemy(self):
        """Generate 1-3 enemies based on the current story context"""
        num_enemies = random.randint(1, 3)  # Generate 1-3 enemies
        enemies = []
        for _ in range(num_enemies):
            prompt = f"""
            Generate an enemy for the story premise: "{self.story_type}"
            Format as JSON:
            {{
                "name": "",
                "hp": number,
                "attack": number,
                "defense": number,
                "skills": ["skill1", "skill2", ...],
                "inventory": ["item1", "item2", ...],
                "reward": {{
                    "type": "item|weapon|stat_boost",
                    "value": "item_name|weapon_name|stat_name",
                    "amount": number
                }}
            }}
            """
            response = call_deepseek_api(prompt)
            if response:
                try:
                    # Clean the response by removing markdown code blocks if present
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0].strip()

                    enemy_data = json.loads(response)
                    # Shorten the enemy's name
                    enemy_data["name"] = enemy_data["name"].split(" ")[0]  # Use the first word of the name
                    # Ensure the enemy has skills
                    if "skills" not in enemy_data:
                        enemy_data["skills"] = ["Slash", "Shield Block"]  # Default skills
                    # Ensure enemy HP is capped at 100
                    enemy_data["hp"] = min(enemy_data["hp"], 100)

                    enemy = Enemy(
                        name=enemy_data["name"],
                        hp=enemy_data["hp"],
                        attack=enemy_data["attack"],
                        defense=enemy_data["defense"],
                        skills=enemy_data["skills"],
                        inventory=enemy_data["inventory"],
                        reward=enemy_data["reward"]
                    )
                    enemies.append(enemy)
                except json.JSONDecodeError as e:
                    print(f"Error parsing enemy data: {e}")
        return enemies

    def handle_combat(self, enemies):
        """Handle combat between players, companions, and multiple enemies"""
        print("\nA wild encounter appears!")
        for enemy in enemies:
            print(f"- {enemy.name}")

        while any(p.hp > 0 for p in self.players) and any(e.hp > 0 for e in enemies):
            # Display combat status before each round
            self.display_combat_status()

            for player in self.players:
                if player.hp > 0:
                    print(f"\n{player.name}'s turn!")
                    print("Choose an action:")
                    print("1. Attack")
                    print("2. Use Skill")
                    print("3. Use Item")
                    choice = self.present_choice(["Attack", "Use Skill", "Use Item"])

                    if choice == 1:
                        print("Available enemies:")
                        active_enemies = [e for e in enemies if e.hp > 0]
                        for i, enemy in enumerate(active_enemies, 1):
                            print(f"{i}. {enemy.name} (HP: {enemy.hp})")
                        enemy_choice = self.present_choice([e.name for e in active_enemies])
                        player.attack_target(active_enemies[enemy_choice - 1])
                    elif choice == 2:
                        print("Available skills:")
                        for i, skill in enumerate(player.skills, 1):
                            print(f"{i}. {skill}")
                        skill_choice = self.present_choice(list(player.skills))
                        print("Available targets:")
                        targets = [p for p in self.players if p.hp > 0] + [c for c in self.companions if c.hp > 0] + [e for e in enemies if e.hp > 0]
                        for i, target in enumerate(targets, 1):
                            target_type = "Player" if target in self.players else "Companion" if target in self.companions else "Enemy"
                            print(f"{i}. {target.name} (HP: {target.hp}) [{target_type}]")
                        target_choice = self.present_choice([t.name for t in targets])
                        player.use_skill(list(player.skills)[skill_choice - 1], targets[target_choice - 1])
                    elif choice == 3:
                        print("Available items:")
                        for i, item in enumerate(player.inventory, 1):
                            print(f"{i}. {item}")
                        item_choice = self.present_choice(list(player.inventory))
                        print("Available targets:")
                        targets = [p for p in self.players if p.hp > 0] + [c for c in self.companions if c.hp > 0] + [e for e in enemies if e.hp > 0]
                        for i, target in enumerate(targets, 1):
                            target_type = "Player" if target in self.players else "Companion" if target in self.companions else "Enemy"
                            print(f"{i}. {target.name} (HP: {target.hp}) [{target_type}]")
                        target_choice = self.present_choice([t.name for t in targets])
                        player.use_item(list(player.inventory)[item_choice - 1], targets[target_choice - 1])

            if any(e.hp > 0 for e in enemies):
                # Companions take their turns
                for companion in self.companions:
                    if companion.hp <= 0:
                        print(f"\n{companion.name} is unconscious and cannot act.")
                        continue

                    if any(e.hp > 0 for e in enemies):
                        print(f"\n{companion.name}'s turn!")
                        # Companions perform a regular attack
                        hit_roll = random.randint(1, 4)  # 1-3 hit, 4 miss
                        if hit_roll != 4:
                            damage = random.randint(1, 20)  # Damage between 1 and 20
                            # Choose a random enemy to attack
                            active_enemies = [e for e in enemies if e.hp > 0]
                            target = random.choice(active_enemies)
                            print(f"Companion: {companion.name} attacks {target.name} for {damage} damage!")
                            target.take_damage(damage)
                        else:
                            print(f"Companion: {companion.name}'s attack misses!")

            if any(e.hp > 0 for e in enemies):
                # Enemies take their turns
                for enemy in enemies:
                    if enemy.hp > 0:
                        print(f"\n{enemy.name}'s turn!")
                        enemy.attack_target(self)  # Pass the game instance to the enemy

        if all(e.hp <= 0 for e in enemies):
            for enemy in enemies:
                self.give_reward(enemy.reward)
            print("\nAll enemies have been defeated!")
            self.complete_quest(self.current_location)
            return

    def give_reward(self, reward):
        """Give the player a reward after defeating an enemy"""
        try:
            if reward["type"] == "item":
                self.players[0].inventory.append(reward["value"])
                print(f"\nYou received a {reward['value']}!")
            elif reward["type"] == "weapon":
                self.players[0].inventory.append(reward["value"])
                print(f"\nYou received a {reward['value']}!")
            elif reward["type"] == "stat_boost":
                current_value = getattr(self.players[0], reward["value"])
                setattr(self.players[0], reward["value"], current_value + reward["amount"])
                print(f"\nYour {reward['value']} increased by {reward['amount']}!")
        except (KeyError, AttributeError) as e:
            print(f"\nReceived a reward but couldn't process it: {e}")

    @time_api_call
    def complete_quest(self, location):
        """Complete the quest associated with the current location"""
        for quest in self.quest_log:
            if quest["location"] == location:
                print(f"\nQuest Completed: {quest['title']}")
                print(quest["description"])

                # Generate a detailed conclusion
                prompt = f"""
                Generate a detailed conclusion for completing the quest "{quest['title']}" in {location}.
                The conclusion should describe the outcome, rewards, and impact on the story.
                Keep it to 2-3 sentences.
                """
                response = call_deepseek_api(prompt)
                if response:
                    print(f"\nConclusion: {response}")
                else:
                    print("\nConclusion: You have successfully completed the quest, achieving your objectives and making progress in your adventure.")

                self.quest_log.remove(quest)

                # Check if this was the final area
                if location == self.story_data["locations"][-1]:
                    self.handle_game_completion()
                break

    @time_api_call
    def handle_game_completion(self):
        """Handle the completion of the game"""
        print("\n" + "=" * 50)
        print("Congratulations! You have completed the main quest!")
        print("=" * 50)

        # Generate a story conclusion
        prompt = f"""
        Generate a detailed conclusion for the story: "{self.story_type}"
        The conclusion should wrap up the main plot points and describe the impact of the player's actions.
        Keep it to 3-4 sentences.
        """
        response = call_deepseek_api(prompt)
        if response:
            print(f"\nStory Conclusion:\n{response}")

        print("\nThank you for playing!")
        exit()

    @time_api_call
    def explore_location(self):
        """Handle exploring the current location"""
        print(f"\nExploring {self.current_location}...")

        # Generate discoveries and encounters for the location
        prompt = f"""
        Generate discoveries for {self.current_location} in the context of: {self.story_type}
        Format as JSON:
        {{
            "discoveries": ["discovery1", "discovery2", ...],
            "encounters": ["encounter1", "encounter2", ...],
            "actions": ["action1", "action2", ...]
        }}
        """
        response = call_deepseek_api(prompt)
        if response:
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                if not response.endswith("}"):
                    response += "}"

                location_data = json.loads(response)

                # Set discoveries
                self.discoveries = location_data.get("discoveries", [])
                if not self.discoveries:
                    self.discoveries = ["A mysterious object catches your eye."]

                # Set encounters - ensure combat for quest locations that haven't been completed
                has_quest = any(quest["location"] == self.current_location for quest in self.quest_log)
                if has_quest and self.current_location not in self.completed_combats:
                    self.encounters = ["A dangerous foe blocks your path."]
                    num_encounters = random.randint(1, 3)
                    while len(self.encounters) < num_encounters:
                        self.encounters.append(f"Another enemy approaches...")
                else:
                    self.encounters = location_data.get("encounters", [])

                # Set actions
                self.actions = location_data.get("actions", [])

            except json.JSONDecodeError as e:
                print(f"Error parsing location data: {e}")
                return

# Example extended usage
if __name__ == "__main__":
    try:
        # Initialize game
        game = Game()

        # Start game and get story premise
        print("\nWelcome to the Dynamic D&D Adventure Generator!")
        print("\nPlease describe the type of story you'd like to experience.")
        print("Example: 'A dark fantasy story about hunting vampires in a medieval city'")
        print("or 'A lighthearted adventure about helping magical creatures in an enchanted forest'")

        story_premise = input("\nYour story premise: ").strip()
        if not story_premise:
            print("Story premise cannot be empty. Please try again.")
            exit()

        # Set the story type and generate elements
        game.story_type = story_premise
        print("\nGenerating your adventure...")
        story_data = game.generate_story_elements()
        if not story_data:
            print("Failed to generate story elements. Please try again.")
            exit()

        num_players = 1

        # Create players
        for i in range(num_players):
            print(f"\nCreating Player {i+1}:")

            # Display available characters
            print("\nAvailable characters:")
            for j, char in enumerate(story_data["character_options"], 1):
                print(f"\n{j}. {char['name']}")
                print(f"Description: {char['description']}")
                print(f"HP: {char['hp']}")
                print(f"Attack: {char['attack']}")
                print(f"Defense: {char['defense']}")
                print("Skills:", ", ".join(char['skills']))
                print("Starting items:", ", ".join(char['inventory']))

            # Let player choose their character
            while True:
                try:
                    choice = int(input(f"\nPlayer {i+1}, choose your character (1-{len(story_data['character_options'])}): "))
                    if 1 <= choice <= len(story_data["character_options"]):
                        char_data = story_data["character_options"][choice - 1]
                        player = Character(
                            name=char_data["name"],
                            hp=char_data["hp"],
                            attack=char_data["attack"],
                            defense=char_data["defense"],
                            skills=char_data["skills"],
                            inventory=char_data["inventory"],
                            description=char_data["description"]
                        )
                        game.add_player(player)
                        print(f"\nPlayer {i+1} created: {player.name}")
                        break
                    print(f"Please enter a number between 1 and {len(story_data['character_options'])}.")
                except ValueError:
                    print("Please enter a valid number.")

        # Begin the adventure
        print("\nAll players have chosen their characters. Your adventure begins...")
        print(f"\nSetting: {story_data['setting']}")
        print("\nMain Quest:", story_data["quests"]["main_quest"]["title"])
        print(story_data["quests"]["main_quest"]["description"])

        # Start the main game loop
        game.main_game_loop()

    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please try running the game again.")
