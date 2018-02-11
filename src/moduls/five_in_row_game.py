from answer import AssistantAnswer
from enum import Enum
from PIL import Image, ImageFont, ImageDraw
from string import ascii_uppercase
from io import BytesIO
import random
from moduls.tic_tac_toe import Board
from configs.config_constants import TicTacToeFontPath

MAX_SCORE = 100000


class XOModule:

    def __init__(self, config):
        self.is_started = False
        self.__game = None
        self.__config = config

    @property
    def is_active(self):
        return self.is_started


    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Start XO Game":
            answer = self.start(assistant, parameters_dict)
        elif intent == "Turn":
            answer = self.turn(assistant, parameters_dict)
        return answer

    def start(self, assistant, parameters_dict):
        self.is_started = True
        self.__game = XOLogics(font_path=self.__config[TicTacToeFontPath])
        board = self.__game.get_image_board()
        if self.__game.is_bot_first:
            message_key = "XO.start_game_key.bot_turn"
        else:
            message_key = "XO.start_game_key.user_turn"
        return AssistantAnswer(message_key, picture=board)

    def turn(self, assistant, parameters_dict):
        pos = parameters_dict["Position"].lower()
        self.__game.move(pos)
        game_status, xo_message_key = self.__game.get_status()
        board = self.__game.get_image_board()
        par = {}
        if game_status == GameStatus.PLAYING:
            message_key = "XO_bot_turn"
        elif game_status == GameStatus.WIN:
            message_key = "XO_win"
            self.is_started = False
        elif game_status == GameStatus.LOSE:
            message_key = "XO_lose"
            self.is_started = False
        elif game_status == GameStatus.ERROR:
            message_key = xo_message_key
        else:
            message_key = "XO_draw_error"

        return AssistantAnswer(message_key, par, picture=board)


class GameStatus(Enum):
    PLAYING, WIN, LOSE, DRAW, ERROR = range(5)


class XOLogics:
    _FIGURES = ["X", "O"]

    def __init__(self, field_size=10, font_path=""):
        self.is_bot_first = random.randint(0, 1)
        self.__field_size = field_size
        self.status = GameStatus.PLAYING
        self.state = XO(font_path=font_path)
        if self.is_bot_first:
            self.ai_move()

    def move(self, pos):
        """
        pos is string where pos[0] is letter, pos[1] is number
        Return JPG picture of field
        """
        y_pos = (ord(pos[0]) - ord("a"))
        x_pos = int(pos[1]) - 1
        self.state.human_move(y_pos, x_pos)
        status = self.get_status()[0]
        if status == GameStatus.PLAYING:
            self.ai_move()

    def ai_move(self):
        self.state.ai_move()

    def get_status(self):
        """
        Return GameStatus
        """
        s = self.state.win()
        if s == "Continue":
            self.status = GameStatus.PLAYING
        elif s == "X won":
            self.status = GameStatus.LOSE
        elif s == "O won":
            self.status = GameStatus.WIN
        elif s == "Draw":
            self.status = GameStatus.DRAW
        else:
            self.status = GameStatus.ERROR
        return self.status, s

    def get_image_board(self):
        out = BytesIO()
        out.name = "Board"
        im = self.state.draw()
        im.save(out, format="PNG")
        out.seek(0)
        return out

    @property
    def field_size(self):
        return self.__field_size


# class Board:
#     def __init__(self, rows=3):
#         self.cell = 100
#         self.rows = rows
#         self.pad = 20
#         self.board = self.cell * rows
#         self.header = int(self.cell / 2)
#         self.pix = self.header + self.board
#         self.width = 10
#
#         self.centers = []
#         for j in range(rows):
#             centers = []
#             for i in range(rows):
#                 posx = self.header + i * self.cell + self.cell / 2
#                 posy = self.header + j * self.cell + self.cell / 2
#                 centers.append((posx, posy))
#             self.centers.append(centers)
#
#         self.im = Image.new('RGBA', (self.pix, self.pix), (255, 255, 255, 0))
#         draw = ImageDraw.Draw(self.im)
#
#         common = {
#             "fill": "blue",
#             "width": self.width
#         }
#
#         draw.line((0, self.header, self.pix, self.header), **common)
#         draw.line((self.header, 0, self.header, self.pix), **common)
#
#         for i in range(1, self.rows):
#             pos = i * (self.board / self.rows) + self.header
#             draw.line((0, pos, self.pix, pos), **common)
#             draw.line((pos, 0, pos, self.pix), **common)
#
#         font = ImageFont.truetype("FreeMono.ttf", 30)
#
#         for i in range(self.rows):
#             pos = i * (self.board / self.rows) + self.header + self.cell / 2
#             fsize = font.getsize(str(i + 1))
#             draw.text((pos - fsize[0] / 2, self.header / 2 - fsize[1]), str(i + 1), fill="red", font=font)
#             letter = ascii_uppercase[i]
#             fsize2 = font.getsize(letter)
#             draw.text((self.header / 2 - fsize2[0] / 2, pos - fsize2[1] / 2), letter, fill="red", font=font)
#
#     def put(self, xy, kind):
#         x, y = xy
#         cen = self.centers[x][y]
#
#         lcx, lcy = cen[0] - self.cell / 2 + self.pad, cen[1] - self.cell / 2 + self.pad
#         rcx, rcy = cen[0] + self.cell / 2 - self.pad, cen[1] + self.cell / 2 - self.pad
#
#         draw = ImageDraw.Draw(self.im)
#         if kind == "O":
#             draw.ellipse((lcx, lcy, rcx, rcy), fill="red")
#             draw.ellipse((lcx + self.width, lcy + self.width, rcx - self.width, rcy - self.width), fill="white")
#         elif kind == "X":
#             draw.line((lcx, lcy, rcx, rcy), fill="red", width=10)
#             draw.line((lcx, rcy, rcx, lcy), fill="red", width=10)
#
#     def straight_line(self, from_xy, to_xy):
#         draw = ImageDraw.Draw(self.im)
#         fx, fy = from_xy
#         tx, ty = to_xy
#         lcx, lcy = self.centers[fx][fy]
#         rcx, rcy = self.centers[tx][ty]
#         draw.line((lcx, lcy, rcx, rcy), fill="yellow", width=10)


class XO:
    def __init__(self, field_size=10, font_path=""):
        self.__field_size = field_size
        self.board = self.generate_board()
        # self.status = "Continue"
        self.__font_path = font_path
        self.__error_message_key = None

    def draw(self):
        img = Board(len(self.board), self.__font_path)
        for x in range(len(self.board)):
            for y in range(len(self.board[x])):
                img.put((x, y), self.board[x][y])
        return img.im

    def alpha_beta_search(self, board, move_y, move_x, depth, a, b, maximizing, player):
        if player == "O":
            opponent = "X"
        else:
            opponent = "O"

        if depth == 0:
            if maximizing:
                return self.get_heuristic(board, player), move_y, move_x
            else:
                return self.get_heuristic(board, opponent), move_y, move_x

        if maximizing:
            score = -MAX_SCORE
            for y in range(len(board)):
                for x in range(len(board[y])):
                    if board[y][x] != "." or not self.detect_neighbours(board, y, x, 2):
                        continue

                    # New node: move made by maximizing player
                    board[y][x] = player
                    s, my, mx = self.alpha_beta_search(board, y, x, depth - 1, a, b, False, opponent)

                    if s > score:
                        score = s
                        move_y = y
                        move_x = x

                    board[y][x] = "."
                    a = max(a, score)

                    if b <= a:
                        break
                if b <= a:
                    break

            return score, move_y, move_x

        else:
            score = MAX_SCORE
            for y in range(len(board)):
                for x in range(len(board[y])):
                    if board[y][x] != "." or not self.detect_neighbours(board, y, x, 2):
                        continue

                    # New node: move made by minimizing player
                    board[y][x] = player
                    s, my, mx = self.alpha_beta_search(board, y, x, depth - 1, a, b, True, opponent)
                    if s < score:
                        score = s
                        move_y = y
                        move_x = x

                    board[y][x] = "."
                    b = min(b, score)

                    if b <= a:
                        break

                if b <= a:
                    break

            return score, move_y, move_x

    def get_heuristic(self, board, player):
        cross = (player == "X")

        free_x, semi_x, blocked_x = self.state_game(board, "X")
        free_o, semi_o, blocked_o = self.state_game(board, "O")

        if free_x[5] >= 1 or free_x[4] >= 1 or semi_x[5] >= 1 or blocked_x[5] >= 1:
            if cross:
                return MAX_SCORE
            else:
                return -MAX_SCORE

        elif free_o[5] >= 1 or free_o[4] >= 1 or semi_o[5] >= 1 or blocked_o[5] >= 1:
            if cross:
                return -MAX_SCORE
            else:
                return MAX_SCORE

        cross_all, circle_all = 0, 0

        # Add 4^n for sequence of length n

        for i in range(2, 5):
            cross_all += 4 ** semi_x[i - 2]
            circle_all += 4 ** semi_o[i - 2]
            if i != 4:
                cross_all += 4 ** free_x[i - 1]
                circle_all += 4 ** free_o[i - 1]

        # Defensive
        if cross:
            return 1 * cross_all - 2 * circle_all
        else:
            return 1 * circle_all - 2 * cross_all

    def detect_neighbour_in_row(self, board, y, x, dx, dy, dist):
        while dist >= 0:
            if self.check_bounder(y, x) and board[y][x] != ".":
                return True
            dist -= 1
            y += dy
            x += dx
        return False

    def detect_neighbours(self, board, y, x, dist):
        found = False

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if self.detect_neighbour_in_row(board, y, x, dy, dx, dist):
                    found = True

        return found

    def basic_search(self, board, player, move_y, move_x):
        max_score = -MAX_SCORE

        for j in range(len(board)):
            for i in range(len(board[j])):
                if board[j][i] == ".":
                    board[j][i] = player
                    score = self.get_heuristic(board, player)
                    if score > max_score:
                        max_score = score
                        move_y, move_x = j, i
                    board[j][i] = "."

        return move_y, move_x

    def ai_move(self):
        aux_board = self.board
        score, move_y, move_x = self.alpha_beta_search(aux_board, -1, -1, 2, -MAX_SCORE * self.__field_size, MAX_SCORE * self.__field_size, True, "X")
        if not self.check_bounder(move_y, move_x):
            move_y, move_x = self.basic_search(self.board, "X", move_y, move_x)
        self.board[move_y][move_x] = "X"

    def check_bounder(self, y, x):
        return 0 <= y < self.__field_size and 0 <= x < self.__field_size

    def human_move(self, y_coord, x_coord):
        if self.check_bounder(y_coord, x_coord):
            if self.board[y_coord][x_coord] == ".":
                self.board[y_coord][x_coord] = "O"
            else:
                self.__error_message_key = "XO_not_empty_cell"
        else:
            self.__error_message_key = "XO_wrong_field"

    def generate_board(self):
        board = []
        for i in range(self.__field_size):
            board.append(["."] * self.__field_size)
        return board

    def print_board(self, board):
        for i in range(10):
            row = str(i) + " "
            for j in range(10):
                row += board[i][j] + " "
            print(row + "\n")
        print("  0 1 2 3 4 5 6 7 8 9")

    def check_limits(self, y, x, ini_y, ini_x, player):
        beginning, end = False, False
        if 0 <= ini_y < self.__field_size and 0 <= ini_x < self.__field_size:
            beginning = self.board[ini_y][ini_x] != "."
        end = self.board[y][x] != player
        if beginning and end:
            return "free"
        elif beginning or end:
            return "semi"
        else:
            return "blocked"

    def state_game(self, board, player):
        free, semi, blocked = [0] * 6, [0] * 6, [0] * 6

        # Horizontal move
        seq = False
        ini_y = -1
        ini_x = -1
        count = 0
        for y in range(self.__field_size):
            for x in range(self.__field_size):
                if board[y][x] == player and seq:
                    count += 1
                if board[y][x] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = y
                    ini_x = x
                elif (board[y][x] != player or x == 9) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(y, x, ini_y, ini_x - 1, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0

        # Vertical move
        for x in range(self.__field_size):
            for y in range(self.__field_size):
                if board[y][x] == player and seq:
                    count += 1
                if board[y][x] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = y
                    ini_x = x
                elif (board[y][x] != player or y == 9) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(y, x, ini_y - 1, ini_x, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0

        # Left Diagonal
        for y in range(5, 0, -1):
            dy = y
            dx = 0
            seq = False
            count = 0
            while dy < self.__field_size:
                if board[dy][dx] == player and seq:
                    count += 1
                if board[dy][dx] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = dy
                    ini_x = dx
                elif (board[dy][dx] != player or dy == 9) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(dy, dx, ini_y - 1, ini_x - 1, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0
                dy += 1
                dx += 1
        for x in range(0, 6):
            dy = 0
            dx = x
            seq = False
            count = 0
            while dx < self.__field_size:
                if board[dy][dx] == player and seq:
                    count += 1
                if board[dy][dx] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = dy
                    ini_x = dx
                elif (board[dy][dx] != player or dx == 9) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(dy, dx, ini_y - 1, ini_x - 1, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0
                dy += 1
                dx += 1

        # Right Diagonal
        for x in range(5, 0, -1):
            dy = 9
            dx = x
            seq = False
            count = 0
            while dx < self.__field_size:
                if board[dy][dx] == player and seq:
                    count += 1
                if board[dy][dx] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = dy
                    ini_x = dx
                elif (board[dy][dx] != player or dx == 9) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(dy, dx, ini_y - 1, ini_x - 1, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0
                dy -= 1
                dx += 1
        for y in range(9, 4, -1):
            dy = y
            dx = 0
            seq = False
            count = 0
            while dy >= 0:
                if board[dy][dx] == player and seq:
                    count += 1
                if board[dy][dx] == player and not seq:
                    count += 1
                    seq = True
                    ini_y = dy
                    ini_x = dx
                elif (board[dy][dx] != player or dy == 0) and seq:
                    seq = False
                    if count > 1:
                        result = self.check_limits(dy, dx, ini_y - 1, ini_x - 1, player)
                        if result == "free":
                            free[count] += 1
                        elif result == "semi":
                            semi[count] += 1
                        else:
                            blocked[count] += 1
                    count = 0
                dy -= 1
                dx += 1
        return free, semi, blocked

    def is_full(self, board):
        for y in range(self.__field_size):
            for x in range(self.__field_size):
                if board[y][x] == ".":
                    return False
        return True

    def win(self):
        if self.__error_message_key is None:
            results = self.state_game(self.board, "X")
            for i in results:
                if i[5] > 0:
                    return "X won"
            results = self.state_game(self.board, "O")
            for i in results:
                if i[5] > 0:
                    return "O won"
            if self.is_full(self.board):
                return "Draw"
            return "Continue"
        else:
            mes = self.__error_message_key
            self.__error_message_key = None
            return mes
