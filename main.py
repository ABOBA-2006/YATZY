from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
import random
import time


COMBINATIONS_AMOUNT = 15
COMBINATIONS_UPPER = [
            "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes"]
COMBINATIONS_LOWER_1 = [
            "One Pair", "Two Pairs", "Three of a Kind", "Four of a Kind", "SKIP"]
COMBINATIONS_LOWER_2 = [
            "Small Straight", "Large Straight", "Full House", "Chance", "Yatzy"]
DICE_AMOUNT = 5
DICE_SPINNING_ANIMATION_DURATION = 1.5
WIDTH = 600
HEIGHT = 800

user_scores = [0] * COMBINATIONS_AMOUNT
bot_scores = [0] * COMBINATIONS_AMOUNT
user_scores_blocks = []
bot_scores_blocks = []
dice_blocks = []
dices = [1] * DICE_AMOUNT
round = 0
rerolls = 2
is_rolling = False
is_game_started = False


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_scores()
        self.init_titles()
        self.init_dice()
        self.init_text()
        self.init_combinations()

        self.setWindowTitle("YATZY")
        self.setFixedSize(WIDTH, HEIGHT)
        self.show()

    def init_scores(self):
        # Left/Right column
        left_column_widget = QWidget(self)
        left_column_widget.setGeometry(0, int(0.25 * HEIGHT), int(0.15 * WIDTH), int(0.5 * HEIGHT))

        right_column_widget = QWidget(self)
        right_column_widget.setGeometry(int(0.85 * WIDTH), int(0.25 * HEIGHT), int(0.15 * WIDTH), int(0.5 * HEIGHT))

        left_column = QVBoxLayout(left_column_widget)
        right_column = QVBoxLayout(right_column_widget)
        for i in range(COMBINATIONS_AMOUNT):
            left_label, right_label = QLabel(), QLabel()
            left_label.setText(str(user_scores[i]))
            right_label.setText(str(bot_scores[i]))
            left_label.setAlignment(Qt.AlignCenter)
            right_label.setAlignment(Qt.AlignCenter)
            left_label.setStyleSheet("background-color: lightgreen; font-size: 20px; color: darkgreen;")
            right_label.setStyleSheet("background-color: lightpink; font-size: 20px; color: crimson;")
            left_column.addWidget(left_label)
            right_column.addWidget(right_label)
            user_scores_blocks.append(left_label)
            bot_scores_blocks.append(right_label)

    def init_titles(self):
        bot_name = QLabel(self)
        bot_name.setAlignment(Qt.AlignCenter)
        bot_name.setText("BOT-IVAN")
        bot_name.setStyleSheet("color: crimson; font-size: 30px; font-weight: bold;")
        bot_name.setGeometry(0,0, WIDTH, HEIGHT // 16)

        user = QLabel(self)
        user.setAlignment(Qt.AlignCenter)
        user.setText("YOU")
        user.setStyleSheet("color: darkgreen; font-size: 30px; font-weight: bold;")
        user.setGeometry(0, HEIGHT - (HEIGHT//16), WIDTH, HEIGHT // 16)

    def init_dice(self):
        dice_widget = QWidget(self)
        dice_widget.setGeometry(int(0.2 * WIDTH), int(0.25 * HEIGHT), int(0.6 * WIDTH), int(0.5 * HEIGHT))
        dice_row = QHBoxLayout(dice_widget)

        divider = 13
        for i in range(DICE_AMOUNT):
            dice = QPushButton(self)
            icon = QIcon("dice-1.png")
            dice.setIcon(icon)
            dice.setIconSize(QSize(HEIGHT // divider, HEIGHT // divider))
            dice.setFixedSize(HEIGHT // divider, HEIGHT // divider)
            dice.setStyleSheet("""
                                    QPushButton {
                                        background-color: transparent;
                                    }
                            
                                    QPushButton:hover {
                                      background-color: lightgray;
                                    }
                                      """)
            dice.clicked.connect(lambda checked, i=i: self.roll_button_pressed(True, i))
            dice_row.addWidget(dice)
            dice_blocks.append(dice)

    def init_text(self):
        roll_widget = QWidget(self)
        roll_widget.setGeometry(int(0.2 * WIDTH), int(0.55 * HEIGHT), int(0.6 * WIDTH), int(0.20 * HEIGHT))
        roll_layout = QGridLayout(roll_widget)

        text_widget = QWidget(self)
        text_widget.setGeometry(int(0.2 * WIDTH), int(0.3 * HEIGHT), int(0.6 * WIDTH), int(0.15 * HEIGHT))
        text_layout = QVBoxLayout(text_widget)

        roll = QPushButton(self)
        roll.setText("ROLL")
        roll.setFixedWidth(int(0.3 * WIDTH))
        roll.setFixedHeight(int(0.125 * HEIGHT))
        roll.setStyleSheet("""
                              QPushButton {
                                  border-radius: 20px;
                                  background-color: lightgreen;
                                  font-size: 30px;
                                  color: darkgreen;
                                  border: 2px solid #000;
                              }
                              QPushButton:hover {
                                  background-color: lightpink;
                                  color:crimson;
                              }
                                      """)
        roll.clicked.connect(lambda : self.roll_button_pressed(False, None))
        roll_layout.addWidget(roll)

        self.round_number_text = QLabel(self)
        self.round_number_text.setAlignment(Qt.AlignCenter)
        self.round_number_text.setText("ROUND # ___")
        self.round_number_text.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.reroll_text = QLabel(self)
        self.reroll_text.setAlignment(Qt.AlignCenter)
        self.reroll_text.setText("Re-Rolls: ___")
        self.reroll_text.setStyleSheet("font-size: 20px; font-weight: bold;")

        text_layout.addWidget(self.round_number_text)
        text_layout.addWidget(self.reroll_text)

    def init_combinations(self):
        user_combinations_widget = QWidget(self)
        user_combinations_widget.setGeometry(0, int(0.75 * HEIGHT), WIDTH, int(0.2 * HEIGHT))
        bot_combinations_widget = QWidget(self)
        bot_combinations_widget.setGeometry(0, int(0.05 * HEIGHT), WIDTH, int(0.2 * HEIGHT))

        user_combinations = QVBoxLayout(user_combinations_widget)
        first_row_user = QHBoxLayout()
        second_row_user = QHBoxLayout()
        third_row_user = QHBoxLayout()
        user_combinations.addLayout(first_row_user)
        user_combinations.addLayout(second_row_user)
        user_combinations.addLayout(third_row_user)
        bot_combinations = QVBoxLayout(bot_combinations_widget)
        first_row_bot = QHBoxLayout()
        second_row_bot = QHBoxLayout()
        third_row_bot = QHBoxLayout()
        bot_combinations.addLayout(first_row_bot)
        bot_combinations.addLayout(second_row_bot)
        bot_combinations.addLayout(third_row_bot)

        for i in range(2):
            for text in COMBINATIONS_UPPER:
                combination = QPushButton(text)
                if i == 0:
                    first_row_user.addWidget(combination)
                else:
                    first_row_bot.addWidget(combination)
            for text in COMBINATIONS_LOWER_1:
                combination = QPushButton(text)
                if i == 0:
                    second_row_user.addWidget(combination)
                else:
                    second_row_bot.addWidget(combination)
            for text in COMBINATIONS_LOWER_2:
                combination = QPushButton(text)
                if i == 0:
                    third_row_user.addWidget(combination)
                else:
                    third_row_bot.addWidget(combination)

    def roll_button_pressed(self, is_one_dice, dice_num):
        global is_rolling, round, rerolls, is_game_started
        if not is_rolling:
            is_rolling = True
            self.start_time = time.time()
            self.timer = QTimer(self)
            if is_one_dice:
                if rerolls >= 1 and is_game_started:
                    rerolls -= 1
                    self.reroll_text.setText("Re-Rolls: " + str(rerolls))
                    self.timer.timeout.connect(lambda : self.update_one_dice(dice_num))
                else:
                    is_rolling = False
                    return
            else:
                is_game_started = True
                round += 1
                self.round_number_text.setText("ROUND # " + str(round))
                rerolls = 2
                self.reroll_text.setText("Re-Rolls: " + str(rerolls))
                self.timer.timeout.connect(self.update_dice)
            self.timer.start(70)  # Update every 100ms (10 times per second)
        else:
            return

    def update_dice(self):
        dice_randoms = []
        elapsed_time = time.time() - self.start_time
        for i in range(DICE_AMOUNT):
            random_dice = random.randint(1, 6)
            dice_randoms.append(random_dice)
            icon = QIcon("dice-" + str(random_dice) + ".png")
            dice_blocks[i].setIcon(icon)
        if elapsed_time >= DICE_SPINNING_ANIMATION_DURATION:
            self.timer.stop()
            global is_rolling, dices
            dices = dice_randoms.copy()
            is_rolling = False

    def update_one_dice(self, dice_num):
        elapsed_time = time.time() - self.start_time
        random_dice = random.randint(1, 6)
        icon = QIcon("dice-" + str(random_dice) + ".png")
        dice_blocks[dice_num].setIcon(icon)
        if elapsed_time >= DICE_SPINNING_ANIMATION_DURATION:
            self.timer.stop()
            global is_rolling
            dices[dice_num] = random_dice
            is_rolling = False


if __name__ == '__main__':
    app = QApplication([])
    window = GUI()
    app.exec_()