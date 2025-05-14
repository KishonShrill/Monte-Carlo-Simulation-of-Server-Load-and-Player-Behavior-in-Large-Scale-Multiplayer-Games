import random
import numpy as np

class Player:
    def __init__(self, player_type):
        self.type = player_type
        self.happiness = 100
        self.quit_rate = 0
        self.rage_quit = False
        
        match player_type:
            case "idler": self.session_duration = max(1, int(random.gauss(10, 10))) # Easy Gamer
            case "casual": self.session_duration = max(1, int(random.gauss(55, 25))) # Casual Gamer
            case "pro": self.session_duration = max(1, int(random.gauss(240, 30))) # Pro Gamer
            case _: raise ValueError("Unknown player type")
        
    def tick(self, is_server_full, current_server_latency):
        """Reduces the player's session by 1."""
        if self.session_duration > 0:
            self.session_duration -= 1
        
        """Controls player happiness score according to server capacity"""
        if is_server_full and self.happiness > 0:
            self.happiness -= random.randint(1, 2)
            if self.happiness < 0:
                self.happiness = 0
        elif not is_server_full and self.happiness < 100:
            self.happiness += random.randint(1, 2)
            if self.happiness > 100:
                self.happiness = 100
            
        """Controls player happiness score according to server capacity"""
        if current_server_latency >= 100 and is_server_full:
            self.quit_rate += 0.01
            if random.random() < self.quit_rate:
                self.rage_quit = True
                self.session_duration = 0  # Simulate rage quit
                # print(f"I QUIT: {self.quit_rate} | {self.happiness}")
                self.happiness = 0
        else:
            if self.quit_rate > 0.00:
                self.quit_rate -= 0.02

    def is_rage_quit(self):
        return self.rage_quit       
    
    def is_active(self):
        """Check if the player is still active."""
        return self.session_duration > 0
    
    def get_happiness(self):
        return self.happiness

    def __repr__(self):
        return f"<Player session_duration={self.session_duration}>"
