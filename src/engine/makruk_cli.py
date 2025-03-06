import argparse
import subprocess
import sys
import time

class MakrukCLI:
    def __init__(self, skill_level=15):
        self.engine = None
        self.skill_level = skill_level
        self.current_fen = "rnsmksnr/8/pppppppp/8/8/PPPPPPPP/8/RNSKMS1R w - - 0 1"  # เริ่มต้น FEN สำหรับหมากรุกไทย
        self.move_history = []
        self.initialize_engine()
    
    def initialize_engine(self):
        skill_level = self.skill_level
        try:
            self.engine = subprocess.Popen(
                ["/usr/local/bin/stockfish"],  # ปรับเส้นทางตามที่คุณติดตั้ง stockfish
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            # ตั้งค่าเริ่มต้นสำหรับ engine
            self.send_command("uci")
            self.wait_for_response("uciok")  
            self.send_command("setoption name UCI_Variant value makruk")
            time.sleep(0.1)  # ต้องสั่งพักสักครู่เพื่อให้คำสั่งมีผล

            # ตั้งค่า Skill Level แบบ dynamic
            self.send_command(f"setoption name Skill Level value {skill_level}")
            time.sleep(0.1)

            if not self.check_option_value():
                print("Warning: Could not verify Skill Level setting")

            self.send_command("isready")
            self.wait_for_response("readyok")
            print(f"The engine's level is {skill_level}")
            
        except Exception as e:
            print(f"Error initializing engine: {e}")
            sys.exit(1)
    
    def send_command(self, command):
        print(f"Sending: {command}")  # Debug output
        if self.engine and self.engine.stdin:
            self.engine.stdin.write(command + "\n")
            self.engine.stdin.flush()

    def check_option_value(self):
        self.send_command("uci")
        responses = []
        while True:
            line = self.engine.stdout.readline().strip()
            if line:
                responses.append(line)
                if "uciok" in line:
                    break
    
        # ค้นหาและพิมพ์ค่าที่เกี่ยวข้องกับ Skill Level
        for line in responses:
            if "Skill Level" in line:
                print(f"Skill Level option: {line}")
                return True
        return False

    
    def wait_for_response(self, expected_response):
        """ อ่านผลลัพธ์จาก Stockfish จนกว่าจะเจอ expected_response """
        while True:
            output = self.engine.stdout.readline().strip()
            print("Received:", output)
            if expected_response in output:
                break
    
    def get_engine_response(self):
        responses = []
        while True:
            if self.engine and self.engine.stdout:
                line = self.engine.stdout.readline().strip()
                if line:
                    print(f"Received: {line}")  # Debug output
                    responses.append(line)
                    if line in ["uciok", "readyok"] or line.startswith("bestmove"):
                        break
                elif not line and len(responses) > 0:
                    break
        return responses
    
    def process_position(self, fen):
        # ส่งตำแหน่งปัจจุบันไปยัง engine
        self.send_command(f"position fen {fen}")
        self.send_command("go movetime 1000")
        
        # รับการตอบกลับจาก engine
        responses = self.get_engine_response()
        
        # หาการเดินที่ดีที่สุด
        best_move = None
        for line in responses:
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break
        
        return best_move

    def process_position_with_stats(self, fen): # เอาไว้ Test ว่า Skill Level ของ Engine เปลี่ยนจริงหรือไม่
        stats = {
            'depth': 0,
            'nodes': 0,
            'time': 0,
            'score': None
        }
        
        self.send_command(f"position fen {fen}")
        self.send_command("go movetime 1000")
        
        best_move = None
        while True:
            line = self.engine.stdout.readline().strip()
            if line:
                if line.startswith('info'):
                    # เก็บข้อมูลสถิติจาก info line
                    if 'depth' in line:
                        stats['depth'] = int(line.split('depth')[1].split()[0])
                    if 'nodes' in line:
                        stats['nodes'] = int(line.split('nodes')[1].split()[0])
                    if 'time' in line:
                        stats['time'] = int(line.split('time')[1].split()[0])
                    if 'score cp' in line:
                        stats['score'] = int(line.split('score cp')[1].split()[0])
                
                if line.startswith('bestmove'):
                    best_move = line.split()[1]
                    break

        return best_move, stats

    def test_skill_level(self): # เอาไว้ Test ว่า Skill Level ของ Engine เปลี่ยนจริงหรือไม่
        test_fen = "rnsmksnr/8/pppppppp/8/8/PPPPPPPP/8/RNSKMS1R w - - 0 1"
        
        # ทดสอบที่ Skill Level ต่ำ
        self.send_command("setoption name Skill Level value 0")
        time.sleep(0.1)
        move_low, stats_low = self.process_position_with_stats(test_fen)
        
        # ทดสอบที่ Skill Level สูง
        self.send_command("setoption name Skill Level value 10")
        time.sleep(0.1)
        move_high, stats_high = self.process_position_with_stats(test_fen)
        
        print(f"\nSkill Level 1:")
        print(f"Move: {move_low}")
        print(f"Final depth: {stats_low['depth']}")
        print(f"Nodes searched: {stats_low['nodes']}")
        print(f"Time used: {stats_low['time']}ms")
        print(f"Position score: {stats_low['score']}")
        
        print(f"\nSkill Level 10:")
        print(f"Move: {move_high}")
        print(f"Final depth: {stats_high['depth']}")
        print(f"Nodes searched: {stats_high['nodes']}")
        print(f"Time used: {stats_high['time']}ms")
        print(f"Position score: {stats_high['score']}")
    
    def run(self):
        parser = argparse.ArgumentParser(description="Makruk Chess CLI")
        parser.add_argument("--fen", help="Current position in FEN notation", default=None) 
        parser.add_argument("--skill", type=int, help="Set engine skill level (0-20)", default=15)              
        parser.add_argument("--test-skill", action="store_true", help="Test different skill levels") # เอาไว้ Test ว่า Skill Level ของ Engine เปลี่ยนจริงหรือไม่
        
        args = parser.parse_args()

        try:
            if args.test_skill:
                self.test_skill_level()
                return
                
            if args.fen:
                self.current_fen = args.fen
            
            # ตั้งค่า skill level ที่รับจาก command-line argument
            self.skill_level = args.skill  
            self.initialize_engine()  # รีสตาร์ท Engine ด้วยค่า skill_level ใหม่

            engine_move = self.process_position(self.current_fen)
            
            if engine_move:
                print(f"Engine's best move: {engine_move}")
            else:
                print("No valid move found")
                
        except Exception as e:
            print(f"Error processing position: {e}")
        finally:
            if self.engine:
                self.engine.terminate()

def main():
    cli = MakrukCLI()
    cli.run()

if __name__ == "__main__":
    main()



