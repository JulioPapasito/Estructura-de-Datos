import copy

#la neta me quedo bien feo profe
# --- CONSTANTES ---
SIZE = 8
EMPTY = '.'
RED_PIECE = 'r'
RED_KING = 'R'
WHITE_PIECE = 'w'
WHITE_KING = 'W'

# --- CLASE MOVIMIENTO ---
class Move:
    def __init__(self, from_r, from_c, to_r, to_c, cap_r=-1, cap_c=-1):
        self.from_r = from_r
        self.from_c = from_c
        self.to_r = to_r
        self.to_c = to_c
        self.cap_r = cap_r
        self.cap_c = cap_c

    def __str__(self):
        txt = f"Mover de ({self.from_r},{self.from_c}) a ({self.to_r},{self.to_c})"
        if self.cap_r != -1:
            txt += f" [¡Come ficha en ({self.cap_r},{self.cap_c})!]"
        return txt

# --- CLASE TABLERO ---
class Board:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
        self.red_left = 12
        self.white_left = 12
        self.create_board()

    def create_board(self):
        for r in range(SIZE):
            for c in range(SIZE):
                if (r + c) % 2 != 0:
                    if r < 3:
                        self.grid[r][c] = WHITE_PIECE
                    elif r > 4:
                        self.grid[r][c] = RED_PIECE

    def print_board(self):
        print("\n   0 1 2 3 4 5 6 7  (Columnas)")
        print("  -----------------")
        for r in range(SIZE):
            row_str = f"{r} |"
            for c in range(SIZE):
                row_str += f"{self.grid[r][c]} "
            print(row_str + "|")
        print("  -----------------")
        print(" (Filas)")

    def make_move(self, move):
        p = self.grid[move.from_r][move.from_c]
        self.grid[move.from_r][move.from_c] = EMPTY

        # Coronación a Dama
        if p == RED_PIECE and move.to_r == 0:
            p = RED_KING
        elif p == WHITE_PIECE and move.to_r == SIZE - 1:
            p = WHITE_KING

        self.grid[move.to_r][move.to_c] = p

        if move.cap_r != -1:
            cap = self.grid[move.cap_r][move.cap_c]
            if cap in (RED_PIECE, RED_KING):
                self.red_left -= 1
            elif cap in (WHITE_PIECE, WHITE_KING):
                self.white_left -= 1
            self.grid[move.cap_r][move.cap_c] = EMPTY

    def get_valid_moves(self, is_red):
        captures = []
        simple = []

        for r in range(SIZE):
            for c in range(SIZE):
                p = self.grid[r][c]
                is_piece_red = p in (RED_PIECE, RED_KING)
                is_piece_white = p in (WHITE_PIECE, WHITE_KING)

                if (is_red and is_piece_red) or (not is_red and is_piece_white):
                    if p in (RED_KING, WHITE_KING):
                        dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                    elif p == RED_PIECE:
                        dirs = [(-1, -1), (-1, 1)]
                    else:
                        dirs = [(1, -1), (1, 1)]

                    for dr, dc in dirs:
                        mr, mc = r + dr, c + dc
                        jr, jc = r + 2 * dr, c + 2 * dc

                        # Movimiento con captura
                        if 0 <= jr < SIZE and 0 <= jc < SIZE:
                            target = self.grid[mr][mc]
                            is_enemy = (target in (WHITE_PIECE, WHITE_KING)) if is_red else (target in (RED_PIECE, RED_KING))
                            if is_enemy and self.grid[jr][jc] == EMPTY:
                                captures.append(Move(r, c, jr, jc, mr, mc))

                        # Movimiento simple
                        if 0 <= mr < SIZE and 0 <= mc < SIZE and self.grid[mr][mc] == EMPTY:
                            simple.append(Move(r, c, mr, mc))

        # En Damas Inglesas las capturas son obligatorias si existen
        return captures if len(captures) > 0 else simple

    def evaluate(self):
        red_kings = sum(row.count(RED_KING) for row in self.grid)
        white_kings = sum(row.count(WHITE_KING) for row in self.grid)
        return (self.white_left - self.red_left) + (white_kings * 0.5 - red_kings * 0.5)

# --- IA MINIMAX ---
def minimax(board, depth, max_player):
    if depth == 0 or board.red_left == 0 or board.white_left == 0:
        return board.evaluate(), None

    valid_moves = board.get_valid_moves(not max_player)
    if not valid_moves:
        return (-1000, None) if max_player else (1000, None)

    best_move = None

    if max_player:  # Turno CPU (Blancas)
        max_eval = float('-inf')
        for move in valid_moves:
            temp_board = copy.deepcopy(board)
            temp_board.make_move(move)
            evaluation, _ = minimax(temp_board, depth - 1, False)
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            temp_board = copy.deepcopy(board)
            temp_board.make_move(move)
            evaluation, _ = minimax(temp_board, depth - 1, True)
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
        return min_eval, best_move

# --- MODO REPETICIÓN ---
def run_replay(history):
    index = 0
    while True:
        print("\n=== MODO REPETICIÓN (REPLAY) ===")
        print(f"Movimiento {index + 1} de {len(history)}")
        history[index].print_board()

        cmd = input("Comandos: [a] Anterior | [d] Siguiente | [s] Salir del Replay: ").lower().strip()

        if cmd == 'a' and index > 0:
            index -= 1
        elif cmd == 'd' and index < len(history) - 1:
            index += 1
        elif cmd == 's':
            break

# --- FUNCIÓN PARA ABANDONAR CON MENSAJE DE RESULTADO ---
def end_game_early(history, red_turn, vs_cpu):
    print("\n" + "=" * 40)
    print(" 🏳️ SE HA ABANDONADO LA PARTIDA 🏳️")
    print("=" * 40)

    if vs_cpu:
        # En vs CPU el jugador siempre es Rojas
        print(" 💀 ¡DERROTA! 💀")
        print(" Te has rendido. La CPU gana esta partida.")
    else:
        # En modo 2 jugadores gana el rival del que abandonó
        winner = "Blancas" if red_turn else "Rojas"
        quitter = "Rojas" if red_turn else "Blancas"
        print(f" El jugador de las {quitter} se ha retirado.")
        print(f" 🎉 ¡VICTORIA DE LAS {winner.upper()}! 🎉")
    
    print("=" * 40)
    
    opcion = input("\n¿Quieres revisar el Replay de tus jugadas? (s/n): ").strip().lower()
    if opcion == 's':
        run_replay(history)

# --- BUCLE PRINCIPAL ---
def main():
    print("=== JUEGO DE DAMAS INGLESAS EN PYTHON ===")
    print("1. Modo 1 Jugador (vs CPU)")
    print("2. Modo 2 Jugadores (Local en la misma PC)")
    
    game_mode = ""
    while game_mode not in ('1', '2'):
        game_mode = input("Selecciona el modo de juego (1 o 2): ").strip()

    vs_cpu = (game_mode == '1')
    
    board = Board()
    history = [copy.deepcopy(board)]
    red_turn = True
    winner = None

    if vs_cpu:
        print("\nJugando vs CPU: Tú eres Rojas ('r'/'R') y la CPU es Blancas ('w'/'W').")
    else:
        print("\nModo 2 Jugadores: Jugador 1 es Rojas ('r'/'R') y Jugador 2 es Blancas ('w'/'W').")

    while board.red_left > 0 and board.white_left > 0:
        board.print_board()

        current_color_name = "Rojas ('r'/'R')" if red_turn else "Blancas ('w'/'W')"
        player_label = "Jugador 1" if red_turn else ("CPU" if vs_cpu else "Jugador 2")

        # Turno de Humano (siempre en Rojas, o en Blancas si es modo 2 jugadores)
        if red_turn or not vs_cpu:
            valid_moves = board.get_valid_moves(is_red=red_turn)

            if not valid_moves:
                winner = "Blancas" if red_turn else "Rojas"
                break

            print(f"\n--- TURNO DE {player_label.upper()} ({current_color_name}) ---")
            print("Movimientos disponibles:")
            for i, move in enumerate(valid_moves):
                print(f"{i + 1}. {move}")

            user_input = input("\nSelecciona tu jugada ('r' para Replay, 'f' para Abandonar): ").strip().lower()

            if user_input == 'r':
                run_replay(history)
                continue
            elif user_input == 'f':
                end_game_early(history, red_turn, vs_cpu)
                return

            try:
                choice = int(user_input)
                if 1 <= choice <= len(valid_moves):
                    selected_move = valid_moves[choice - 1]
                    board.make_move(selected_move)
                    history.append(copy.deepcopy(board))
                    red_turn = not red_turn  # Cambia el turno
                else:
                    print(">> Opción fuera de rango. Selecciona un número de la lista.")
            except ValueError:
                print(">> Entrada no válida. Introduce el número de la opción.")

        # Turno de la CPU (solo en modo 1 jugador cuando le toca a las Blancas)
        else:
            print("\nTurno de la CPU (Blancas)...")
            valid_moves = board.get_valid_moves(is_red=False)

            if not valid_moves:
                winner = "Rojas"
                break

            _, best_move = minimax(board, 3, max_player=True)

            if best_move:
                board.make_move(best_move)
                history.append(copy.deepcopy(board))
                print(f"CPU realizó: {best_move}")
            
            red_turn = True

    # Determinar ganador si terminó por quedarse sin piezas
    if not winner:
        if board.white_left == 0:
            winner = "Rojas"
        elif board.red_left == 0:
            winner = "Blancas"

    # --- MENSAJES DE FIN DE JUEGO (POR DERROTA/VICTORIA NORMAL) ---
    print("\n" + "=" * 40)
    if vs_cpu:
        if winner == "Rojas":
            print(" 🎉 ¡VICTORIA! Has derrotado a la CPU. 🎉")
        else:
            print(" 💀 ¡DERROTA! La CPU ha ganado esta partida. 💀")
    else:
        print(f" 🎉 ¡VICTORIA DE LAS {winner.upper()}! 🎉")
    print("=" * 40)

    print("\nIniciando modo repetición automáticamente...")
    run_replay(history)

if __name__ == "__main__":
    main()