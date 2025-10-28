from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QListWidget, QPushButton
from dnd_llm import Game  # Import the Game class from dnd_llm.py

class DnDUI(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("D&D Master UI")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Left side: Character stats, name, items, attacks, and skills
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.character_name = QLabel("Character Name")
        left_layout.addWidget(self.character_name)

        self.character_stats = QLabel("Stats: \nHP: 100\nAttack: 10\nDefense: 5")
        left_layout.addWidget(self.character_stats)

        self.items_list = QListWidget()
        left_layout.addWidget(self.items_list)

        self.attacks_list = QListWidget()
        left_layout.addWidget(self.attacks_list)

        self.skills_list = QListWidget()
        left_layout.addWidget(self.skills_list)

        main_layout.addWidget(left_widget)

        # Middle: Story text
        middle_widget = QWidget()
        middle_layout = QVBoxLayout()
        middle_widget.setLayout(middle_layout)

        self.story_text = QTextEdit()
        middle_layout.addWidget(self.story_text)

        main_layout.addWidget(middle_widget)

        # Right side: Quest log
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        self.quest_log = QTextEdit()
        right_layout.addWidget(self.quest_log)

        main_layout.addWidget(right_widget)

        # Update UI with initial data
        self.update_ui()

    def update_ui(self):
        # Update character info
        if self.game.players:
            player = self.game.players[0]
            self.character_name.setText(player.name)
            self.character_stats.setText(f"Stats: \nHP: {player.hp}\nAttack: {player.attack}\nDefense: {player.defense}")
            self.items_list.clear()
            self.items_list.addItems(player.inventory.keys())
            self.attacks_list.clear()
            self.attacks_list.addItems(player.skills.keys())
            self.skills_list.clear()
            self.skills_list.addItems(player.skill_abilities.keys())

        # Update story text
        if self.game.story_data:
            self.story_text.setPlainText(self.game.story_data["setting"])

        # Update quest log
        if self.game.quest_log:
            quest_text = ""
            for quest in self.game.quest_log:
                quest_text += f"{quest['title']}\n{quest['description']}\n\n"
            self.quest_log.setPlainText(quest_text)

if __name__ == "__main__":
    app = QApplication([])

    # Initialize the game
    game = Game()
    game.story_type = "A dark fantasy story about hunting vampires in a medieval city"
    game.generate_story_elements()

    # Create and show the UI
    window = DnDUI(game)
    window.show()
    app.exec_()