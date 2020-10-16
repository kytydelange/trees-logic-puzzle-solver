import pygame
import numpy as np
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'


class Board:

    def __init__(self, board):
        self.board = np.array([[color for color in row] for row in board])
        self.markers = np.array([[' '] * len(row) for row in board])
        self.trees = []
        self.sections = {}
        for color in set(self.board.flatten()):
            self.sections[color] = []
        for row in range(self.board.shape[0]):
            for column in range(self.board.shape[1]):
                self.sections[self.board[row, column]].append((row, column, ' '))

    def mark(self, row, column, symbol):
        currently = self.markers[row, column]
        if currently == 'T':
            self.trees.remove((row, column))
        self.sections[self.board[row, column]].remove((row, column, currently))
        self.sections[self.board[row, column]].append((row, column, symbol))
        self.markers[row, column] = symbol
        if symbol == 'T':
            self.trees.append((row, column))

    def in_bounds(self, tile):
        return tile[0] in range(0, self.board.shape[0]) and tile[1] in range(0, self.board.shape[1])

    def is_valid(self, tile, symbol):
        # check row
        if np.count_nonzero(self.markers[tile[0]] == 'T') > 1 or \
                np.count_nonzero(self.markers[tile[0]] == '-') == self.markers.shape[0]:
            return False

        # check column
        if [row[tile[1]] for row in self.markers].count('T') > 1 or \
                [row[tile[1]] for row in self.markers].count('-') == self.markers.shape[1]:
            return False

        # check adjacency
        if symbol == 'T':
            to_check = [(i, j) for i in range(tile[0] - 1, tile[0] + 2) for j in range(tile[1] - 1, tile[1] + 2)
                        if self.in_bounds((i, j))]
            to_check.remove((tile[0], tile[1]))
            for check in to_check:
                if check in self.trees:
                    return False

        # check section
        section = [a[-1] for a in self.sections[self.board[tile[0], tile[1]]]]
        if section.count('T') > 1:
            return False
        if section.count('-') == len(section):
            return False

        return True

    def find_next_tile(self):
        for row in range(self.markers.shape[0]):
            for column in range(self.markers.shape[1]):
                if self.markers[row, column] == ' ':
                    return row, column
        return None


class Solver:

    def __init__(self, board):
        self.exit = False
        self.board = board
        self.font = pygame.font.SysFont('arial', 50, bold=True)

        size = len(self.board)
        self.dx = 80
        self.dy = 80
        self.screen_width = self.dx * size
        self.screen_height = self.dy * size
        self.extra_height = 100
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height + self.extra_height])

        pygame.display.set_caption('Trees puzzle solver')

        self.rgb = {
            0: (153, 102, 0),
            1: (77, 148, 255),
            2: (255, 77, 77),
            3: (51, 204, 51),
            4: (153, 51, 255),
            5: (255, 153, 51),
            6: (255, 102, 153),
            7: (255, 255, 102),
            8: (102, 255, 204),
            9: (102, 153, 153),
            10: (255, 255, 255),
        }

    def draw_board(self, empty_board):
        size = len(empty_board)

        # draw colored boxes
        for i in range(size):
            for j in range(size):
                pygame.draw.rect(self.screen, self.rgb[empty_board[i][j]], (j * self.dx, i * self.dy,
                                                                            self.dx, self.dy))

        # draw grid
        grid_color_1 = (102, 102, 102)
        grid_color_2 = (16, 16, 16)

        for i in range(size):
            for j in range(size):
                if not j == size - 1:
                    if empty_board[i][j] == empty_board[i][j + 1]:
                        pygame.draw.line(self.screen, grid_color_1,
                                         ((j + 1) * self.dx, i * self.dy),
                                         ((j + 1) * self.dx, (i + 1) * self.dy), 2)
                    else:
                        pygame.draw.line(self.screen, grid_color_2,
                                         ((j + 1) * self.dx, i * self.dy),
                                         ((j + 1) * self.dx, (i + 1) * self.dy), 3)
                if not i == size - 1:
                    if empty_board[i][j] == empty_board[i + 1][j]:
                        pygame.draw.line(self.screen, grid_color_1,
                                         (j * self.dx, (i + 1) * self.dy),
                                         ((j + 1) * self.dx, (i + 1) * self.dy), 2)
                    else:
                        pygame.draw.line(self.screen, grid_color_2,
                                         (j * self.dx, (i + 1) * self.dy),
                                         ((j + 1) * self.dx, (i + 1) * self.dy), 3)

        # draw borders
        border_color = (16, 16, 16)
        for i in range(2):
            pygame.draw.line(self.screen, border_color, (0, i * self.screen_height),
                             (self.screen_width, i * self.screen_height), 6)
            pygame.draw.line(self.screen, border_color, (i * self.screen_width, 0),
                             (i * self.screen_width, self.screen_height), 6)

    def draw_symbols(self, markers):
        def draw_symbol(symbols_array, row, column, symbol):
            text = self.font.render(symbol, 1, (0, 0, 0))
            text_rect = text.get_rect(center=(round(((column + 0.5) * self.screen_width) // symbols_array.shape[1]),
                                              round(((row + 0.5) * self.screen_height) // symbols_array.shape[1])))
            self.screen.blit(text, text_rect)
        for i in range(markers.shape[0]):
            for j in range(markers.shape[1]):
                draw_symbol(markers, i, j, markers[i, j])

    def start(self, board_object):
        next_tile = board_object.find_next_tile()
        if not next_tile:
            return True
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
                return True
        for symbol in ['T', '-']:
            board_object.mark(next_tile[0], next_tile[1], symbol)
            self.screen.fill((255, 255, 255))
            self.draw_board(self.board)
            self.draw_symbols(board_object.markers)
            pygame.display.update()
            if board_object.is_valid(next_tile, symbol):
                if self.start(board_object):
                    return True
            board_object.mark(next_tile[0], next_tile[1], ' ')
            self.screen.fill((255, 255, 255))
            self.draw_board(self.board)
            self.draw_symbols(board_object.markers)
            pygame.display.update()
        return False

    def solve(self):
        running = True
        done = False
        b = Board(self.board)
        while running:
            if not done:
                self.screen.fill((255, 255, 255))
                self.draw_board(self.board)
                text = self.font.render('Press enter', 1, (0, 0, 0))
                text_rect = text.get_rect(center=(self.screen_width // 2,
                                                  round(self.screen_height + self.extra_height // 2)))
                self.screen.blit(text, text_rect)
                pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_RETURN]:
                        if event.key == pygame.K_RETURN:
                            self.start(b)
                            self.draw_symbols(b.markers)
                            if self.exit:
                                running = False
                                break
                            if np.count_nonzero(b.markers == ' ') == b.markers.size:
                                text = self.font.render('No solution', 1, (0, 0, 0))
                            else:
                                text = self.font.render('Done!', 1, (0, 0, 0))
                            text_rect = text.get_rect(center=(self.screen_width // 2,
                                                              round(self.screen_height + self.extra_height // 2)))
                            self.screen.blit(text, text_rect)
                            done = True
                            pygame.display.update()
        pygame.quit()


class Picker:

    def __init__(self):
        self.screen_width = 300
        self.screen_height = 100
        self.extra_height = 0
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        self.screen.fill((255, 255, 255))
        self.font = pygame.font.SysFont('arial', 20, bold=True)
        self.board = None
        self.rgb = {
            0: (153, 102, 0),
            1: (77, 148, 255),
            2: (255, 77, 77),
            3: (51, 204, 51),
            4: (153, 51, 255),
            5: (255, 153, 51),
            6: (255, 102, 153),
            7: (255, 255, 102),
            8: (102, 255, 204),
            9: (102, 153, 153),
            10: (255, 255, 255),
        }

        self.dx = 80
        self.dy = 80

        text = self.font.render('Choose size of board (1-10)', 1, (0, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2,
                                          self.screen_height // 2))
        self.screen.blit(text, text_rect)

        pygame.display.set_caption('Trees puzzle solver')
        pygame.display.update()

    def get_board_size(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                else:
                    if event.type == pygame.KEYDOWN:
                        if pygame.key.name(event.key).isnumeric():
                            if int(pygame.key.name(event.key)) in range(1, 10):
                                dim = int(pygame.key.name(event.key))
                                self.board = np.full((dim, dim), 10)
                                return dim
                            elif int(pygame.key.name(event.key)) == 0:
                                dim = 10
                                self.board = np.full((10, 10), 10)
                                return dim
        pass

    def get_board(self):
        size = self.get_board_size()
        if not size:
            return None
        self.screen_width = size*self.dx
        self.screen_height = size * self.dy
        self.extra_height = 100
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height + self.extra_height])
        self.screen.fill((255, 255, 255))
        i, j = 0, 0
        running = True
        pygame.display.update()
        while running:
            self.screen.fill((255, 255, 255))
            self.draw_board(self.board)
            self.draw_symbols(self.board)
            text = self.font.render(f'Fill in board (1-{size}), press enter', 1, (0, 0, 0))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height + self.extra_height // 2))
            self.screen.blit(text, text_rect)
            self.draw_cursor(i, j)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                else:
                    if event.type == pygame.KEYDOWN:
                        if pygame.key.name(event.key) == 'return':
                            running = False
                            break
                        elif pygame.key.name(event.key).isnumeric():
                            if int(pygame.key.name(event.key)) in range(size + 1):
                                self.board[j, i] = int(pygame.key.name(event.key))
                        elif pygame.key.name(event.key) in ['up', 'down', 'left', 'right']:
                            if pygame.key.name(event.key) == 'up':
                                if j - 1 in range(0, size):
                                    j -= 1
                            elif pygame.key.name(event.key) == 'down':
                                if j + 1 in range(0, size):
                                    j += 1
                            elif pygame.key.name(event.key) == 'left':
                                if i - 1 in range(0, size):
                                    i -= 1
                            elif pygame.key.name(event.key) == 'right':
                                if i + 1 in range(0, size):
                                    i += 1
        return self.board

    def draw_cursor(self, i, j):
        pygame.draw.line(self.screen, (255, 0, 0),
                         (i * self.dx, j * self.dy),
                         (i * self.dx, (j + 1) * self.dy), 6)
        pygame.draw.line(self.screen, (255, 0, 0),
                         ((i + 1) * self.dx, j * self.dy),
                         ((i + 1) * self.dx, (j + 1) * self.dy), 6)
        pygame.draw.line(self.screen, (255, 0, 0),
                         (i * self.dx, j * self.dy),
                         ((i + 1) * self.dx, j * self.dy), 6)
        pygame.draw.line(self.screen, (255, 0, 0),
                         (i * self.dx, (j + 1) * self.dy),
                         ((i + 1) * self.dx, (j + 1) * self.dy), 6)

    def draw_symbol(self, markers, row, column, symbol):
        if not symbol == 10:
            text = self.font.render(str(symbol), 1, (0, 0, 0))
            text_rect = text.get_rect(center=(round(((column + 0.5) * self.screen_width) // markers.shape[1]),
                                              round(((row + 0.5) * self.screen_height) // markers.shape[1])))
            self.screen.blit(text, text_rect)

    def draw_symbols(self, markers):
        for i in range(markers.shape[0]):
            for j in range(markers.shape[1]):
                self.draw_symbol(markers, i, j, markers[i, j])

    def draw_board(self, empty_board):
        size = len(empty_board)

        # draw colored boxes
        for i in range(size):
            for j in range(size):
                pygame.draw.rect(self.screen, self.rgb[empty_board[i][j]], (j * self.dx, i * self.dy,
                                                                            self.dx, self.dy))

        # draw grid
        grid_color_1 = (102, 102, 102)
        grid_color_2 = (16, 16, 16)

        for i in range(size):
            for j in range(size - 1):
                if empty_board[i][j] == empty_board[i][j + 1]:
                    pygame.draw.line(self.screen, grid_color_1,
                                     ((j + 1) * self.dx, i * self.dy),
                                     ((j + 1) * self.dx, (i + 1) * self.dy), )
        for i in range(size - 1):
            for j in range(size):
                if empty_board[i][j] == empty_board[i + 1][j]:
                    pygame.draw.line(self.screen, grid_color_1,
                                     (j * self.dx, (i + 1) * self.dy),
                                     ((j + 1) * self.dx, (i + 1) * self.dy), 2)

        for i in range(size):
            for j in range(size - 1):
                if not empty_board[i][j] == empty_board[i][j + 1]:
                    pygame.draw.line(self.screen, grid_color_2,
                                     ((j + 1) * self.dx, i * self.dy),
                                     ((j + 1) * self.dx, (i + 1) * self.dy), 3)

        for i in range(size - 1):
            for j in range(size):
                if not empty_board[i][j] == empty_board[i + 1][j]:
                    pygame.draw.line(self.screen, grid_color_2,
                                     (j * self.dx, (i + 1) * self.dy),
                                     ((j + 1) * self.dx, (i + 1) * self.dy), 3)

        # draw borders
        border_color = (16, 16, 16)
        for i in range(2):
            pygame.draw.line(self.screen, border_color, (0, i * self.screen_height),
                             (self.screen_width, i * self.screen_height), 6)
            pygame.draw.line(self.screen, border_color, (i * self.screen_width, 0),
                             (i * self.screen_width, self.screen_height), 6)


def run():
    pygame.init()
    pygame.font.init()
    picker = Picker()
    board = picker.get_board()
    if board is not None:
        solver = Solver(board)
        solver.solve()
