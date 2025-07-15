import random

class Ship:
    def __init__(self,size, vertical, start_pos):
        self.size = size
        self.vertical = vertical
        self.start_pos = start_pos
        self.hits = []
        self.status = 'цел'

    def is_attaked(self, x, y):
        ship_cells = []
        for i in range(self.size):
            if self.vertical:
                ship_cells.append((self.start_pos[0], self.start_pos[1]+i))
            else:
                ship_cells.append((self.start_pos[0]+i, self.start_pos[1]))

        return (x, y) in ship_cells

    def update_status(self):
        if len(self.hits) == self.size:
            self.status = 'убит'
        elif len(self.hits) > 0:
            self.status = 'ранен'

    def all_coordinates(self):
        ship_cells = []
        for i in range(self.size):
            if self.vertical:
                ship_cells.append((self.start_pos[0], self.start_pos[1] + i))
            else:
                ship_cells.append((self.start_pos[0] + i, self.start_pos[1]))

        return ship_cells

    def get_border(self):
        border_cells = set()
        ship_cells = self.all_coordinates()
        for (x,y) in ship_cells:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    bx = dx + x
                    by = dy + y
                    if (bx,by) not in ship_cells:
                        border_cells.add((bx,by))

        return border_cells




class Board:
    def __init__(self, size=6):
        self.size = size
        self.grid = [['○' for i in range(self.size)]for i in range(self.size)]
        self.ships = []
        self.hits = set()
        self.misses = set()

    def add_ship(self,ship):
        for x,y in ship.all_coordinates():
            if not(0 <= x < self.size and 0 <= y < self.size):
                raise ValueError('Корабль выходит за границы поля!')

        for stationed_ship in self.ships:
            if set(ship.all_coordinates()) & set(stationed_ship.all_coordinates()):
                raise ValueError('Корабль пересекается с другим!')

        for stationed_ship in self.ships:
            if set(ship.get_border()) & set(stationed_ship.all_coordinates()):
                raise ValueError('Корабль касается существующего!')

        self.ships.append(ship)
        self._change_grid()

    def _change_grid(self):
        self.grid = [['○' for i in range(self.size)]for i in range(self.size)]
        for ship in self.ships:
            for x,y in ship.all_coordinates():
                self.grid[y][x] = '■'
            for x,y in self.hits:
                self.grid[y][x] = 'X'
            for x,y in self.misses:
                self.grid[y][x] = 'T'

    def attack(self,x,y):
        if (x,y) in self.hits or (x,y) in self.misses:
            raise ValueError('Вы уже стреляли в эту точку!')

        for ship in self.ships:
            if ship.is_attaked(x,y):
                ship.hits.append((x,y))
                ship.update_status()
                self.hits.add((x,y))
                self._change_grid()
                return 'Попадание'

        self.misses.add((x,y))
        self._change_grid()
        return 'Промах'

    def board_display(self,hide_ships = False):
        print(" | " + " | ".join(str(i+1) for i in range(self.size)))
        for y in range(self.size):
            row = []
            for x in range(self.size):
                cell = self.grid[y][x]
                if hide_ships and cell == '■':
                    row.append('○')
                else:
                    row.append(cell)
            print(f"{y+1}| " + " | ".join(row))


    def print_grid(self):
        print(self.grid)


class AIPlayer:
    def __init__(self, board_size=6):
        self.board_size = board_size
        self.possible_shots = [(x, y) for x in range(board_size) for y in range(board_size)]

    def make_attack(self):
        if not self.possible_shots:
            raise ValueError("Нет доступных ходов")
        x, y = random.choice(self.possible_shots)

        self.possible_shots.remove((x, y))

        return x, y


class Game:
    def __init__(self, size=6):
        self.size = size
        self.player_board = Board(size)
        self.ai_board = Board(size)
        self.ai = AIPlayer(size)

    def setup_game(self):
        print('Расставьте ваши корабли')
        ships_to_place = [('3-палубный',3),
                          ('2-палубный',2),
                          ('2-палубный',2),
                          ('1-палубный',1),
                          ('1-палубный',1),
                          ('1-палубный',1),
                          ]

        for name, size in ships_to_place:
            while True:
                try:
                    print(f"\nРазмещение {name} корабля (размер {size})")
                    x = int(input("Введите X координату: ")) - 1
                    y = int(input("Введите Y координату: ")) - 1
                    vertical = input("Вертикально? (y/n): ").lower() == 'y'
                    ship = Ship(size,vertical,(x,y))
                    self.player_board.add_ship(ship)
                    self.player_board.board_display()
                    break
                except ValueError as e:
                    print(f"Ошибка: {e}. Попробуйте еще раз.")

    def auto_setup_ai(self):
        ships = [3,2,2,1,1,1]
        for size in ships:
            placed = False
            while not placed:
                try:
                    x = random.randint(0, self.size-1)
                    y = random.randint(0, self.size-1)
                    vertical = random.choice([True,False])
                    ship = Ship(size,vertical,(x,y))
                    self.ai_board.add_ship(ship)
                    placed = True
                except ValueError:
                    continue
    def player_turn(self):
        print("\n Ващ ход!")
        while True:
            try:
                x = int(input('Введите Х координату для выстрела'))-1
                y = int(input('Введите Y координату для выстрела'))-1
                result = self.ai_board.attack(x,y)
                print(f'\nРезульат: {result}!')
                self.ai_board.board_display(hide_ships=False)
                return result == 'Попадание'
            except ValueError as e:
                print(f'Ошибка: {e}. Попробуйте еще раз.')

    def ai_turn(self):
        print("\nХод противника...")
        x, y = self.ai.make_attack()
        print(f"Противник стреляет в ({x + 1}, {y + 1})")
        result = self.player_board.attack(x, y)
        print(f"Результат: {result}!")
        self.player_board.board_display()
        return result == 'Попадание'

    def check_win(self):
        player_wins = all(ship.status == 'убит' for ship in self.ai_board.ships)
        ai_wins = all(ship.status == 'убит' for ship in self.player_board.ships)

        if player_wins:
            print("\nПоздравляем! Вы победили!")
            return True
        elif ai_wins:
            print("\nВы проиграли. Попробуйте еще раз!")
            return True
        return False

    def start(self):
        print("=== МОРСКОЙ БОЙ ===")
        self.setup_game()
        self.auto_setup_ai()

        while True:
            hit = self.player_turn()
            if self.check_win():
                break
            if not hit:
                self.ai_turn()
                if self.check_win():
                    break


if __name__ == "__main__":
    game = Game()
    game.start()





