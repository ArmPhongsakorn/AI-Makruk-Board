import serial
import time
import subprocess
import os
import RPi.GPIO as GPIO

print("[DEBUG] CWD:", os.getcwd())
print("[DEBUG] User:", os.getlogin())


# setup GPIO on  raspi
GREE_BUTTON_PIN = 23 # for start the game
GPIO.setmode(GPIO.BCM)
GPIO.setup(GREE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BLUE_BUTTON_PIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(BLUE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RED_BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

esp_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"]

baud_rate = 115200
ser_list = [serial.Serial(port, baud_rate, timeout=1) for port in esp_ports]

# open esp32 port
ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)
time.sleep(2) # wait for esp32

def send_message(message):
    # Add text in final line
    message += '\n'
    ser.write(message.encode())
    print(f"Send data: {message.strip()}")
    time.sleep(0.5)  # wait for response

def check_fen():
    data_from_esp = read_fen_from_esp() # raw data of position
    raw_to_array = change_raw_data_to_array(data_from_esp) # raw data to only number (0&1) be arry 4 row
    array_to_row = flatten_sensor_data(raw_to_array) # array 4 row spilt to 8 x 8
    array_to_row.reverse()
    fen_data = sensor_to_fen(array_to_row) # array 8 x 8 map to fen pattern
    print(fen_data)
    if fen_data == "rnsmksnr/8/pppppppp/8/8/PPPPPPPP/8/RNSKMSNR": # init value
        print(fen_data)
        return True
    else:
        return False

def sensor_to_board(sensor_data, board_state):
    # 1. Flatten 4x16 -> 64
    flat = sum(sensor_data, [])
    if len(flat) != 64:
        raise ValueError("Sensor data must contain 64 values")

    board_8x8 = [flat[i:i+8] for i in range(0, 64, 8)]

    board_state_binary = board_to_binary(board_state)

    # 2. Initialize current_board as board_state
    current_board = [row[:] for row in board_state]
    
    # 3. Find the location that has changed
    moved_from = []  # Collect the position where the piece was moved.
    moved_to = []    # Keep the position where the piece was moved.
    
    for i in range(8):
        for j in range(8):
            prev = board_state_binary[i][j]  # 0= Has a piece, 1= No piece
            curr = board_8x8[i][j]           # 0= Has a piece, 1= No piece
            
            if prev == 0 and curr == 1:
                # Originally there was a piece -> Now there is no piece (the piece has been moved out)
                moved_from.append((i, j, board_state[i][j]))  # Keep the position and type of pieces.
                current_board[i][j] = None  # Remove the piece from its original position.
            
            elif prev == 1 and curr == 0:
                # Originally there were no pieces -> Now there are pieces (the pieces have been moved in)
                moved_to.append((i, j))  # Save destination location
    
    # 4. Move the piece from the origin to the destination.
    if moved_from and moved_to:
        for dest_i, dest_j in moved_to:
            if moved_from:  # If there are still pieces left that were removed
                src_i, src_j, piece = moved_from.pop(0)  # Use the first piece that was moved.
                current_board[dest_i][dest_j] = piece  # Move the piece to its destination position.
    
    print(f"current_board549854: {current_board}")
    return current_board

def sensor_to_fen(sensor_data):
    # 1. Check sensor (4x16) or 8x8
    flat = sum(sensor_data, [])  # flatten data 4x16 is 64 values
    if len(flat) != 64:
        raise ValueError("Sensor data must contain 64 values")
    board_8x8 = [flat[i:i+8] for i in range(0, 64, 8)]

    # board_8x8.reverse()

    # print(f"Reverse Board: {board_8x8}")

    # 2. Initial board (Makruk)
    initial_board = [
        ['r', 'n', 's', 'm', 'k', 's', 'n', 'r'],  # row 1 ( Black )
        [None] * 8,                                # row 2
        ['p'] * 8,                                 # row 3 
        [None] * 8,                                # row 4
        [None] * 8,                                # row 5
        ['P'] * 8,                                 # row 6 
        [None] * 8,                                # row 7
        ['R', 'N', 'S', 'K', 'M', 'S', 'N', 'R']   # row 8 ( White)
    ]
    
    # Create the board from sensor
    current_board = [[None for _ in range(8)] for _ in range(8)]
    
    # # Detect curent pieces
    moved_pieces = []  # Collect the position of the removed piece.
    
    # Start with all pieces in their starting position.
    for i in range(8):
        for j in range(8):
            if board_8x8[i][j] == 0:  # There is a chess piece.
                current_board[i][j] = initial_board[i][j]
            else:  # No piece
                if initial_board[i][j] is not None:
                    moved_pieces.append((i, j, initial_board[i][j]))
    
    # # Find the destination position of the removed piece.
    for i in range(8):
        for j in range(8):
            if board_8x8[i][j] == 0 and current_board[i][j] is None:  # There are pieces but none in the starting position.
                if moved_pieces:
                    # Use the first removed piece.
                    row, col, piece = moved_pieces.pop(0)
                    current_board[i][j] = piece
    
    # Convert current board to FEN
    fen_rows = []
    for row in current_board:
        fen_row = ''
        empty_count = 0
        for piece in row:
            if piece is not None:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece
            else:
                empty_count += 1
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    
    fen = '/'.join(fen_rows)
    return fen

def update_board_to_fen(board):
    fen_rows = []
    for row in board:
        fen_row = ''
        empty_count = 0
        for piece in row:
            if piece is not None:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece
            else:
                empty_count += 1
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    
    fen = '/'.join(fen_rows)
    return fen

def flatten_sensor_data(raw_data):
    flat = []
    for row in raw_data:
        flat.append(row[:8])   
        flat.append(row[8:])   
    return flat  

def change_raw_data_to_array(all_data):
    sensor_data = []
    for line in all_data:
        try:
            if "Sensor values:" in line:
                line = line.replace("Sensor values:", "").strip()
            row = list(map(int, line.split()))
            if len(row) == 16:
                sensor_data.append(row)
        except:
            pass
    return sensor_data    


def read_fen_from_esp():
    raw_data = [] # To contain the raw data (magnet detect position) from esp32

    while True:
        for i, ser in enumerate(ser_list):
            try:
                ser.reset_input_buffer()               
                ser.write(b'R') # Sent R to all esp32 to start to sent data to raspi                        
                time.sleep(0.5)                       

                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    raw_data.append(line)
                    # msg = f"ESP{i} ({esp_ports[i]}): {line}"
                    # print(msg)
            except Exception as e:
                # error_msg = f"ESP{i} ({esp_ports[i]}) ERROR: {e}"
                # print(error_msg)
                raw_data.append(f"ERROR: {e}")
        time.sleep(1)

        return raw_data

def get_fen():
    data_from_esp = read_fen_from_esp() # raw data of position
    raw_to_array = change_raw_data_to_array(data_from_esp) # raw data to arry 4 row
    array_to_row = flatten_sensor_data(raw_to_array) # array 4 row spilt to 8 x 8
    array_to_row.reverse()
    fen_data = sensor_to_fen(array_to_row) # array 8 x 8 map to fen pattern
    
    return fen_data

def get_sensor_data():
    data_from_esp = read_fen_from_esp() # raw data of position
    raw_to_array = change_raw_data_to_array(data_from_esp) # raw data to arry 4 row
    array_to_row = flatten_sensor_data(raw_to_array) # array 4 row spilt to 8 x 8
    array_to_row.reverse()

    return array_to_row

def get_best_move_from_engine(fen_with_skill: str) -> str:
    engine_path = os.path.expanduser("/home/admin/AI-Makruk-Board/src/engine/stockfish")  # path of engine

    try:
        # separate FEN and skill level
        if "--skill" in fen_with_skill:
            fen_part, skill_part = fen_with_skill.split("--skill")
            fen = fen_part.strip()
            skill_level = int(skill_part.strip())
        else:
            fen = fen_with_skill.strip()
            skill_level = 20  # default 
        print(f"skill of engine : {skill_level}")
        # open subprocess of engine
        engine = subprocess.Popen(
            [engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # send the command to engine
        cmds = [
            "uci",
            f"setoption name Skill Level value {skill_level}",
            "isready",
            f"position fen {fen}",
            "go"
        ]

        for cmd in cmds:
            engine.stdin.write(cmd + "\n")
            engine.stdin.flush()

        # read the result
        bestmove = ""
        while True:
            line = engine.stdout.readline().strip()
            if line.startswith("bestmove"):
                bestmove = line.split(" ")[1]
                break

        engine.terminate()
        return bestmove

    except Exception as e:
        return f"Error: {e}"

def fen_to_board(fen):
    rows = fen.split()[0].split('/')
    board = []
    for row in rows:
        expanded_row = []
        for c in row:
            if c.isdigit():
                expanded_row.extend([None] * int(c))
            else:
                expanded_row.append(c)
        board.append(expanded_row)
    return board

def board_to_fen(board_state):
    fen_rows = []
    for row in board_state:
        count = 0
        fen_row = ''
        for c in row:
            if c is None:  # Blank
                count += 1
            else:
                if count > 0:
                    fen_row += str(count)
                    count = 0
                fen_row += c
        if count > 0:
            fen_row += str(count)
        fen_rows.append(fen_row)
    return '/'.join(fen_rows)

def algebraic_to_index(move):
    files = 'abcdefgh'
    return (8 - int(move[1]), files.index(move[0]))

def update_fen(fen_prefix, bestmove):
    board = fen_to_board(fen_prefix)
    move_from = bestmove[:2]
    move_to = bestmove[2:]

    r1, c1 = algebraic_to_index(move_from)
    r2, c2 = algebraic_to_index(move_to)

    piece = board[r1][c1]
    board[r1][c1] = None
    board[r2][c2] = piece

    new_fen_board = update_board_to_fen(board)

    return new_fen_board

def update_fen_from_move(fen, move):
    # ?????????? FEN
    parts = fen.split()
    board = parts[0]
    
    # ?????????????? algebraic notation ???? indices abcdefgh
    # files = "hgfedcba"
    files = "abcdefgh"
    ranks = "87654321"
    
    from_file = files.index(move[0])
    from_rank = ranks.index(move[1])
    to_file = files.index(move[2])
    to_rank = ranks.index(move[3])
    
    # ???? FEN board ???? 2D array
    board_array = []
    for rank in board.split('/'):
        rank_array = []
        for char in rank:
            if char.isdigit():
                rank_array.extend([None] * int(char))
            else:
                rank_array.append(char)
        board_array.append(rank_array)
    
    # ???????????????????????????????????????????
    piece = board_array[from_rank][from_file]
    board_array[from_rank][from_file] = None
    board_array[to_rank][to_file] = piece
    
    # ???? board array ???????? FEN
    new_board = []
    for rank in board_array:
        new_rank = ""
        empty_count = 0
        for square in rank:
            if square is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    new_rank += str(empty_count)
                    empty_count = 0
                new_rank += square
        if empty_count > 0:
            new_rank += str(empty_count)
        new_board.append(new_rank)
    
    new_board_fen = '/'.join(new_board)
    
    return new_board_fen

def detect_move(prev_board, curr_board):
    source = None
    destination = None
    count_to_capture = 0

    while True:
        count_to_capture += 1
        if count_to_capture <=8:
            send_message(f"lift-up-for {8 - count_to_capture} to-eat-mode")
        time.sleep(0.1)
        print(f"[DEBUG] source: {source}, destination: {destination}")

        for i in range(8):
            for j in range(8):
                prev_piece = prev_board[i][j]
                curr_piece = curr_board[i][j]

                if prev_piece != curr_piece:
                    if prev_piece is not None and curr_piece is None:
                        source = (i, j)
                    elif curr_piece is not None and (prev_piece is None or prev_piece != curr_piece):
                        destination = (i, j)

        temp_current_board, fen_current = get_current_board_and_fen(prev_board)

        # In the case of lifting a chess piece in 8 seconds (normal walking)
        if count_to_capture <= 8 and destination is None:
            print(f"[DEBUG] temp_current_board: {temp_current_board}, curr_board: {curr_board}")
            if temp_current_board != curr_board: # Player placed the piece
                print("[DEBUG] HEllo")
                for i in range(8):
                    for j in range(8):
                        curr_piece = temp_current_board[i][j] # newest
                        prev_piece = curr_board[i][j]

                        if prev_piece != curr_piece:
                            if prev_piece is None and curr_piece is not None:
                                destination = (i, j)
                                break
                    if destination is not None:
                        break

        # In case of entering "capturing" mode
        elif count_to_capture > 8 and destination is None:
            for i in range(8):
                for j in range(8):
                    prev_piece = prev_board[i][j]
                    curr_piece = curr_board[i][j]

                    if prev_piece != curr_piece:
                        if prev_piece is not None and curr_piece is None:
                            source = (i, j)
                        elif curr_piece is not None and (prev_piece is None or prev_piece != curr_piece):
                            destination = (i, j)

            # If there is no destination You must wait for the player to pick up the target to eat.
            if destination is None:
                send_message(f"liftup-the-target {15 - count_to_capture}")

                if temp_current_board != curr_board:  # Players raise the target piece.
                    time_put_down = 0
                    for i in range(10):  # Wait to reposition in 10 seconds.
                        time_put_down += 1
                        time.sleep(1)
                        send_message(f"putdownpiecereplaceontarget {5 - time_put_down}s left")

                        temp_current_board_2, _ = get_current_board_and_fen(prev_board)
                        if temp_current_board_2 != temp_current_board:  # players are placed
                            for i in range(8):
                                for j in range(8):
                                    curr_piece = temp_current_board_2[i][j]
                                    prev_piece = temp_current_board[i][j]

                                    if prev_piece != curr_piece:
                                        if prev_piece is None and curr_piece is not None:
                                            destination = (i, j)
                                            break
                                if destination is not None:
                                    break
                            break  # leave forlopp in 10 sec
                else:
                    if count_to_capture >= 15:
                        send_message("timeout: restart detection")
                        count_to_capture = 0  # reset to new count

        if source is not None and destination is not None:
            break  # Found them all, loop complete!

    # leave while loop here
    print(f"Source: {source}, Destination: {destination}")
    if source is None or destination is None:
        raise ValueError(f"Cannot detect valid move on board. Source: {source}, Destination: {destination}")

    return source, destination

def find_piece_moved(prev_board, curr_board, moved_piece):
    for i in range(8):
        for j in range(8):
            if prev_board[i][j] == moved_piece and curr_board[i][j] is None:
                return (i, j)
    return None

def update_board_state(board, source, destination):
    piece = board[source[0]][source[1]]
    board[destination[0]][destination[1]] = piece
    board[source[0]][source[1]] = None

        # --- Handle promotion ---
    dest_row = destination[0]

    if piece == 'p' and dest_row == 2:  # p move to row 3 rd (index 2)
        board[dest_row][destination[1]] = 'm'  # promoted
    elif piece == 'P' and dest_row == 5:  # P move to row 6 th (index 5)
        board[dest_row][destination[1]] = 'M'  # promoted
    return board

def square_to_coords(square):
    file_to_col = {'a': 0, 'b': 1, 'c': 2, 'd': 3,'e': 4, 'f': 5, 'g': 6, 'h': 7}
    col = file_to_col[square[0]]
    row = 8 - int(square[1])  # On the top of row (8) be index 0
    return row, col

def check_engine_move(board_state, bestmove):
    # print(f"Boardddstate {board_state}")
    from_square = bestmove[:2]  
    print(f"from square {from_square}")
    row, col = square_to_coords(from_square)
    # print(f"rowwww colll {board_state[row][col]}")
    if (board_state[row][col] == None):
        return False
    else:
        return True
    
def wait_for_fen_match(fen_update, board_state, bestmove):
    print("Waiting for correct move on board...")

    current_board, fen_current = get_current_board_and_fen(board_state)

    while board_state == current_board:
        send_message(f"please lift a piece {bestmove}")
        time.sleep(0.5)
        current_board, fen_current = get_current_board_and_fen(board_state)
        continue

    print(f"current_board54956: {current_board}, board_state789465: {board_state}")
    source, destination = detect_move(board_state, current_board)
    updated_board = update_board_state(board_state, source, destination)

    print(f"Board update4324: {updated_board}")

    # Convert board to FEN
    fen_from_sensor = update_board_to_fen(updated_board)

    # print(f"[DEBUG] Current FEN: {fen_from_sensor}")
    # print(f"[DEBUG] Expected FEN: {fen_update}")

    while(True):
        if fen_from_sensor == fen_update:
            print("Correct move detected on board.")
            return updated_board  # Send a new board back to the main() to use.
        else:
            print("Incorrect move. Waiting...")
            time.sleep(1)
            continue
            

def get_current_board_and_fen(board_state):
    sensor_data = get_sensor_data()
    board = sensor_to_board(sensor_data, board_state)
    
    return board, board_to_fen(board)

def handle_player_move(previous_board):
    while True:
        current_board, fen_current = get_current_board_and_fen(previous_board)
        if fen_current.strip().split(" ")[0] == board_to_fen(previous_board).strip().split(" ")[0]:
            print("white please lift up the piece!")
            send_message("white please lift up the piece!")
            continue

        print("White moved.")
        send_message("white moved")
        current_board, fen_current = get_current_board_and_fen(previous_board)

        source, destination = detect_move(previous_board, current_board)
        updated_board = update_board_state(previous_board, source, destination)
        fen_current = board_to_fen(updated_board)
        

        # Detect move
        capture_pos, captured_piece = detect_capture(previous_board, current_board)
        if capture_pos:
            print(f"White captured piece at {capture_pos}: {captured_piece}")
        else:
            print("No capture detected.")

        return updated_board, fen_current

def detect_capture(previous_board, current_board):
    for r in range(8):
        for c in range(8):
            prev_piece = previous_board[r][c]
            curr_piece = current_board[r][c]
            if prev_piece and curr_piece and prev_piece != curr_piece:
                if is_opponent(prev_piece, curr_piece):
                    return (r, c), prev_piece
    return None, None

def is_opponent(piece1, piece2):
    return (piece1.isupper() and piece2.islower()) or (piece1.islower() and piece2.isupper())

def handle_engine_move(fen_prefix, board_state, fullmove_count, halfmove_count, skill_level):
    player_turn = 'b'
    fen_suffix = f"{player_turn} - - {halfmove_count} {fullmove_count} --skill {skill_level}"
    fen_full = f"{fen_prefix} {fen_suffix}"

    best_move = get_best_move_from_engine(fen_full)
    fen_expected = update_fen(fen_prefix, best_move)

    print(f"Engine's best move: {best_move}")
    msg = f"next move is:        {best_move}"
    send_message(msg)
    board_after_engine_move = wait_for_fen_match(fen_expected, board_state, best_move)
    send_message("black move!")

    # detect capture
    capture_pos, captured_piece = detect_capture(board_state, board_after_engine_move)
    if capture_pos:
        print(f"Engine captured piece at {capture_pos}: {captured_piece}")
    else:
        print("Engine moved without capturing.")

    return board_after_engine_move, update_board_to_fen(board_after_engine_move)

def board_to_binary(board):
    """Convert a normal board to binary (0 = checkers, 1 = empty)."""
    binary_board = []
    for row in board:
        binary_row = []
        for piece in row:
            if piece is None:
                binary_row.append(1)
            else:
                binary_row.append(0)
        binary_board.append(binary_row)
    return binary_board

def wait_for_button_press(pin):
    while GPIO.input(pin) == GPIO.HIGH:
        time.sleep(0.05)
    time.sleep(0.2)  # Debounce

def get_engine_level(): 
    while True:
        line = read_line_from_serial()
        if "Engine's level:" in line:
            try:
                level = int(line.split(":")[1].strip())
                return level
            except:
                continue

def read_line_from_serial():
    ser.reset_input_buffer()               
    ser.write(b'L') # Sent L to esp32 for request level then sent back to raspi                      
    time.sleep(0.05)
    line = ser.readline().decode('utf-8').strip()

    return line

def is_king_missing(fen: str) -> bool:
    board_part = fen.split(" ")[0]
    # print(f"board_part334534 : {board_part}")
    return 'k' not in board_part or 'K' not in board_part

def main():
    state = 0 # state to waiting for start button player each side have to settel the chess correctly
    engine_level = 0
    while(True):
        if (state == 0):
            while(True):
                if check_fen():
                    state = 1 # state to ready 
                    break
                else:
                    print("scanning")
                    send_message("scanning") # sent to lcd not ready
                    time.sleep(0.5)
                    continue

        elif (state == 1):
            print("Board ready. Press green button to start the game.")
            send_message("ready! press green button")  # send to lcd
            choose_level_mode = False
            while True:
                if GPIO.input(BLUE_BUTTON_PIN) == GPIO.LOW:
                    wait_for_button_press(BLUE_BUTTON_PIN)

                    if not choose_level_mode:
                        print("Entering engine level selection mode...")
                        ser.reset_input_buffer()               
                        ser.write(b'S') # Sent S to esp32 for request to display choose level on lcd                  
                        time.sleep(0.05) 
                        choose_level_mode = True

                    else:
                        print("Confirming engine level...")
                        engine_level = get_engine_level()
                        print(f"Engine level set to: {engine_level}")
                        choose_level_mode = False
                        send_message("press green button to start")

                        continue

                if GPIO.input(GREE_BUTTON_PIN) == GPIO.LOW:
                    print("Green Button Pressed. Starting game...")
                    send_message("game started!")  
                    state = 2
                    time.sleep(0.5)  # Delay to prevent multiple key presses
                    break
                time.sleep(0.1)  # Check every 100ms to save CPU.

        elif (state == 2): # 1 is state that player settel the chess was correctly
            #Waiting for player move
            player_turn_count_fullMove = 1 #count when the black side move
            player_turn_count_halfMove = 0
            temp_fen = get_fen()
            previous_board = fen_to_board(temp_fen)

            while(True):
                print(f"Engine's Level {engine_level}")

                # --- Handle player move (White) ---
                updated_board, fen_prefix = handle_player_move(previous_board)
                previous_board = updated_board

                #----------------- undo process ---------------------------
                # previous_board_before_move = previous_board.copy()
                
                # updated_board, fen_prefix = handle_player_move(previous_board)

                # while True:
                #     count_undo = 0

                #     # Check the undo button within 10 seconds.
                #     while count_undo <= 10:
                #         if GPIO.input(RED_BUTTON_PIN) == GPIO.LOW:
                #             send_message("You pressed undo button. Undoing move.")
                #             previous_board = previous_board_before_move.copy()
                #             break  # confirm to undo
                #         else:
                #             count_undo += 1
                #             send_message(f"you have {10 - count_undo} to undo")
                #             continue

                #     previous_board = updated_board
                #     break
                #-------------------------------------------------------------

                if is_king_missing(fen_prefix): # check king's white 
                    print("game over!")
                    send_message("game over!")
                    time.sleep(5)
                    send_message("new game")
                    state = 0
                    break

                # --- Handle engine move (Black) ---
                updated_board, fen_current = handle_engine_move(
                    fen_prefix, previous_board, 
                    player_turn_count_fullMove, 
                    player_turn_count_halfMove, 
                    engine_level
                    )
                player_turn_count_fullMove += 1
                previous_board = updated_board

                if is_king_missing(fen_prefix): # check king's black 
                    print("game over!")
                    send_message("game over!")
                    time.sleep(5)
                    send_message("new game")
                    state = 0
                    break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up GPIO...")
        GPIO.cleanup()