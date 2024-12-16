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
    "One Pair", "Two Pairs", "Three of a Kind", "Four of a Kind"]
COMBINATIONS_LOWER_2 = [
    "Small Straight", "Large Straight", "Full House", "Chance", "Yatzy"]
COMBINATIONS = COMBINATIONS_UPPER + COMBINATIONS_LOWER_1 + COMBINATIONS_LOWER_2
DICE_AMOUNT = 5
DICE_SPINNING_ANIMATION_DURATION = 1.5
WIDTH = 600
HEIGHT = 800
MAX_ROUND = 10

user_scores = [0] * MAX_ROUND
bot_scores = [0] * MAX_ROUND
bot_combinations_blocks = []
user_scores_blocks = []
user_score = 0
bot_scores_blocks = []
bot_score = 0
dice_blocks = []
dices = [1] * DICE_AMOUNT
round = 0
rerolls = 2
is_rolling = False
is_game_started = False
is_move_finished = True
is_user_turn = True


def count_points(combination, dice_array):
    match combination:
        case "Ones":
            return dice_array.count(1) * 1
        case "Twos":
            return dice_array.count(2) * 2
        case "Threes":
            return dice_array.count(3) * 3
        case "Fours":
            return dice_array.count(4) * 4
        case "Fives":
            return dice_array.count(5) * 5
        case "Sixes":
            return dice_array.count(6) * 6
        case "One Pair":
            pairs = [value for value in range(1, 7) if dice_array.count(value) >= 2]
            pair = max(pairs, default=0)
            return pair * 2
        case "Two Pairs":
            pairs = [value for value in range(1, 7) if dice_array.count(value) >= 2]
            pair = max(pairs, default=0)
            pairs.remove(pair)
            pair2 = max(pairs, default=0)
            if pair == 0 or pair2 == 0:
                return 0
            else:
                return pair * 2 + pair2 * 2
        case "Three of a Kind":
            triples = [value for value in range(1, 7) if dice_array.count(value) >= 3]
            triple = max(triples, default=0)
            return triple * 3
        case "Four of a Kind":
            fourth = [value for value in range(1, 7) if dice_array.count(value) >= 4]
            four = max(fourth, default=0)
            return four * 4
        case "Small Straight":
            dices_copy = dice_array.copy()
            dices_copy.sort()
            return 15 if dices_copy == [1, 2, 3, 4, 5] else 0
        case "Large Straight":
            dices_copy = dice_array.copy()
            dices_copy.sort()
            return 20 if dices_copy == [2, 3, 4, 5, 6] else 0
        case "Full House":
            triples = []
            pairs = []
            for value in range(1, 7):
                count = dice_array.count(value)
                if count >= 3:
                    triples.append(value)
                elif count >= 2:
                    pairs.append(value)
            triple = max(triples, default=0)
            pair = max(pairs, default=0)
            if triple == 0 or pair == 0:
                return 0
            else:
                return triple * 3 + pair * 2
        case "Chance":
            return sum(dice_array)
        case "Yatzy":
            five = max([value for value in range(1, 7) if dice_array.count(value) == 5], default=0)
            return 50 if five != 0 else 0


def bot_decision(dice):
    counts = {i: dice.count(i) for i in range(1, 7)}
    dice_to_keep = [die for die, count in counts.items() if count >= 2]
    if not dice_to_keep:
        dice_to_keep = [max(dice)]
    return [die for die in dice if die not in dice_to_keep], dice_to_keep


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
        for i in range(MAX_ROUND):
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

        self.user_score_text = QLabel("0")
        self.bot_score_text = QLabel("0")
        self.user_score_text.setAlignment(Qt.AlignCenter)
        self.bot_score_text.setAlignment(Qt.AlignCenter)
        self.user_score_text.setStyleSheet("background-color: darkgreen; font-size: 20px; color: lightgreen;")
        self.bot_score_text.setStyleSheet("background-color: crimson; font-size: 20px; color: lightpink;")
        left_column.addWidget(self.user_score_text)
        right_column.addWidget(self.bot_score_text)

    def init_titles(self):
        bot_name = QLabel(self)
        bot_name.setAlignment(Qt.AlignCenter)
        bot_name.setText("BOT-IVAN")
        bot_name.setStyleSheet("color: crimson; font-size: 30px; font-weight: bold;")
        bot_name.setGeometry(0, 0, WIDTH, HEIGHT // 16)

        user = QLabel(self)
        user.setAlignment(Qt.AlignCenter)
        user.setText("YOU")
        user.setStyleSheet("color: darkgreen; font-size: 30px; font-weight: bold;")
        user.setGeometry(0, HEIGHT - (HEIGHT // 16), WIDTH, HEIGHT // 16)

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
                                       background-color: white;
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

        self.roll = QPushButton(self)
        self.roll.setText("ROLL")
        self.roll.setFixedWidth(int(0.3 * WIDTH))
        self.roll.setFixedHeight(int(0.125 * HEIGHT))
        self.roll.setStyleSheet("""
                             QPushButton {
                                 border-radius: 20px;
                                 background-color: lightgreen;
                                 font-size: 30px;
                                 color: darkgreen;
                                 border: 2px solid #000;
                             }
                             QPushButton:hover {
                                 background-color: darkgreen;
                                 color: lightgreen;
                             }
                                     """)
        self.roll.clicked.connect(lambda: self.roll_button_pressed(False, None))
        roll_layout.addWidget(self.roll)

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
                combination.clicked.connect(lambda _, btn=combination, txt=text: self.combination_chosen(btn, txt))
                combination_bot = QPushButton(text)
                if i == 0:
                    first_row_user.addWidget(combination)
                else:
                    first_row_bot.addWidget(combination_bot)
                    bot_combinations_blocks.append(combination_bot)
            for text in COMBINATIONS_LOWER_1:
                combination = QPushButton(text)
                combination_bot = QPushButton(text)
                combination.clicked.connect(lambda _, btn=combination, txt=text: self.combination_chosen(btn, txt))
                if i == 0:
                    second_row_user.addWidget(combination)
                else:
                    second_row_bot.addWidget(combination_bot)
                    bot_combinations_blocks.append(combination_bot)
            for text in COMBINATIONS_LOWER_2:
                combination = QPushButton(text)
                combination_bot = QPushButton(text)
                combination.clicked.connect(lambda _, btn=combination, txt=text: self.combination_chosen(btn, txt))
                if i == 0:
                    third_row_user.addWidget(combination)
                else:
                    third_row_bot.addWidget(combination_bot)
                    bot_combinations_blocks.append(combination_bot)

    def combination_chosen(self, button, text):
        global is_move_finished, user_score
        if not is_move_finished and is_user_turn:
            is_move_finished = True
            score = count_points(text, dices)
            user_score += score
            self.user_score_text.setText(str(user_score))
            user_scores_blocks[round - 1].setText(str(score))
            button.hide()
            self.bots_turn()

    def roll_button_pressed(self, is_one_dice, dice_num):
        global is_rolling, round, rerolls, is_game_started, is_move_finished
        if not is_rolling and is_user_turn:
            is_rolling = True
            self.start_time = time.time()
            self.timer = QTimer(self)
            if is_one_dice:
                if rerolls >= 1 and is_game_started and not is_move_finished:
                    rerolls -= 1
                    self.reroll_text.setText("Re-Rolls: " + str(rerolls))
                    self.timer.timeout.connect(lambda: self.update_one_dice(dice_num))
                else:
                    is_rolling = False
                    return
            else:
                if is_move_finished:
                    is_game_started = True
                    round += 1
                    self.round_number_text.setText("ROUND # " + str(round))
                    rerolls = 2
                    self.reroll_text.setText("Re-Rolls: " + str(rerolls))
                    self.timer.timeout.connect(self.update_dice)
                else:
                    is_rolling = False
                    return
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
            global is_rolling, dices, is_move_finished
            dices = dice_randoms.copy()
            is_move_finished = False
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

    def bots_turn(self):
        self.roll.setStyleSheet(("""
                                     QPushButton {
                                         border-radius: 20px;
                                         background-color: lightpink;
                                         font-size: 30px;
                                         color: crimson;
                                         border: 2px solid #000;
                                     }
                                             """))
        self.roll.setEnabled(False)
        self.roll_button_bot(False, None)

    def roll_button_bot(self, is_one_dice, dice_num):
        global rerolls
        self.start_time = time.time()
        if hasattr(self, 'timer'):  # If the timer exists, stop it before starting a new one
            self.timer.stop()
        self.timer = QTimer(self)
        if is_one_dice:
            if rerolls >= 1:
                rerolls -= 1
                self.reroll_text.setText("Re-Rolls: " + str(rerolls))
                self.timer.timeout.connect(lambda: self.update_one_dice_bot(dice_num))
            else:
                self.calculate_bot_score()
                return
        else:
            rerolls = 2
            self.reroll_text.setText("Re-Rolls: " + str(rerolls))
            self.timer.timeout.connect(self.update_dice_bot)

        self.timer.start(70)  # Update every 100ms (10 times per second)

    def update_dice_bot(self):
        dice_randoms = []
        elapsed_time = time.time() - self.start_time
        for i in range(DICE_AMOUNT):
            random_dice = random.randint(1, 6)
            dice_randoms.append(random_dice)
            icon = QIcon("dice-" + str(random_dice) + ".png")
            dice_blocks[i].setIcon(icon)
        if elapsed_time >= DICE_SPINNING_ANIMATION_DURATION:
            global dices
            self.timer.stop()
            dices = dice_randoms.copy()
            reroll_dices, no_reroll_dices = bot_decision(dices)
            if reroll_dices:
                QTimer.singleShot(500, lambda: self.roll_button_bot(True, dices.index(reroll_dices[0])))
            else:
                self.calculate_bot_score()

    def update_one_dice_bot(self, dice_num):
        elapsed_time = time.time() - self.start_time
        random_dice = random.randint(1, 6)
        icon = QIcon("dice-" + str(random_dice) + ".png")
        dice_blocks[dice_num].setIcon(icon)
        if elapsed_time >= DICE_SPINNING_ANIMATION_DURATION:
            self.timer.stop()
            dices[dice_num] = random_dice
            reroll_dices, no_reroll_dices = bot_decision(dices)
            if reroll_dices:
                QTimer.singleShot(500, lambda: self.roll_button_bot(True, dices.index(reroll_dices[0])))
            else:
                self.calculate_bot_score()

    def calculate_bot_score(self):
        bots_combination = [combination.text() for combination in bot_combinations_blocks]
        scores = []
        for comb in bots_combination:
            scores.append(count_points(comb, dices))

        max_score = max(scores)
        max_index = scores.index(max_score)
        bot_combinations_blocks[max_index].hide()
        bot_combinations_blocks.pop(max_index)

        global bot_score, is_user_turn
        bot_score += max_score
        self.bot_score_text.setText(str(bot_score))
        bot_scores_blocks[round - 1].setText(str(max_score))

        is_user_turn = True
        self.roll.setStyleSheet("""
                                     QPushButton {
                                         border-radius: 20px;
                                         background-color: lightgreen;
                                         font-size: 30px;
                                         color: darkgreen;
                                         border: 2px solid #000;
                                     }
                                     QPushButton:hover {
                                         background-color: darkgreen;
                                         color: lightgreen;
                                     }
                                             """)
        if round != MAX_ROUND:
            self.roll.setEnabled(True)
        else:
            end_screen = QWidget(self)
            end_screen.setGeometry(0, 0, WIDTH, HEIGHT)
            end_screen_layout = QVBoxLayout(end_screen)
            end_screen_layout.setAlignment(Qt.AlignCenter)

            if user_score > bot_score:
                end_screen.setStyleSheet("background-color: darkgreen;")
                text = QLabel("YOU WIN <3")


            else:
                end_screen.setStyleSheet("background-color: crimson;")
                text = QLabel("YOU LOOSE HA HA HA")
            text.setStyleSheet("font-size: 30px; font-weight: bold;")
            end_screen_layout.addWidget(text)
            end_screen.show()


if __name__ == '__main__':
    app = QApplication([])
    window = GUI()
    app.exec_()