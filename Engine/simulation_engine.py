# simulation_engine.py
import random
import numpy as np
from Objects.player import Player  # if Player is in another file

def get_random_type():
    # You can change the probability distribution here
    return random.choices(
        ["idler", "casual", "pro"],
        weights=[0.3, 0.5, 0.2],  # 30% idlers, 50% casuals, 20% pros
        k=1
    )[0]
    
def get_spawn_rate(minute, base_rate=5, peak_rate=15, peak_minute=720, spread=200):
    """Returns estimated player spawn rate based on Gaussian curve"""
    rate = base_rate + (peak_rate - base_rate) * np.exp(-((minute - peak_minute) ** 2) / (2 * spread ** 2))
    return rate

def data_debug(total_players_online,
               total_happiness,
               avg_happiness,
               total_server_latency,
               server_max_capacity,
               disconnections,
               dropouts_by_type
               ):
    print(f"\nTotal players who joined the server: {total_players_online}")
    print(f"Total player happiness: {total_happiness}")
    print(f"Average player happiness: {avg_happiness}")
    print(f"Total server latency: {total_server_latency}")
    print(f"Server max capacity: {server_max_capacity}")
    print(f"Disconnections: {disconnections} || {dropouts_by_type}")


def simulate_game_day(workday_minutes, check_interval, server_max_capacity, SERVERS):
    total_players_online = 0
    new_players = 0
    disconnections = 0
    
    happiness_by_type = {"idler": [], "casual": [], "pro": []}
    dropouts_by_type = {"idler": 0, "casual": 0, "pro": 0}
    
    players = []
    active_log = []
    total_happiness = []
    total_server_latency = []
    
    for minute in range(workday_minutes):
        is_server_full = len(players) > server_max_capacity  
        
        current_server_latency = max(20, 40 + (len(players) / 5))
        if random.random() < 0.01:
            current_server_latency += random.randint(100, 300)
        
        if random.random() < 0.6:
            spawn_rate = get_spawn_rate(minute)
            new_players = np.abs(random.gauss(spawn_rate, 5)).astype(int)
            
            for _ in range(new_players):
                if random.random() <= 1 / SERVERS:
                    total_players_online += 1
                    player_type = get_random_type()
                    players.append(Player(player_type))
                
        active_players = []
        for player in players:
            if player.is_active():
                player.tick(is_server_full, current_server_latency)
                active_players.append(player)
            else:
                total_happiness.append(player.get_happiness())
                happiness_by_type[player.type].append(player.get_happiness())
                if player.is_rage_quit():
                    dropouts_by_type[player.type] += 1
                    disconnections += 1
        players = active_players
        
        if (minute + 1) % check_interval == 0:
            active_log.append(len(players))
            total_server_latency.append(current_server_latency)
        
    for player in players:
        total_happiness.append(player.get_happiness())
        happiness_by_type[player.type].append(player.get_happiness())
        if player.is_rage_quit():
            dropouts_by_type[player.type] += 1
            disconnections += 1
    
    avg_happiness = sum(total_happiness) / total_players_online

    return total_players_online, avg_happiness, active_log, total_server_latency, server_max_capacity, happiness_by_type, dropouts_by_type, disconnections