import numpy as np
import random
from Objects.player import Player
import matplotlib.pyplot as plt

# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------

def get_random_type(weights):
    # You can change the probability distribution here
    return random.choices(
        ["idler", "casual", "pro"],
        weights=weights,  # 30% idlers, 50% casuals, 20% pros
        k=1
    )[0]
    
def get_spawn_rate(minute, base_rate=5, peak_rate=15, peak_minute=1200, spread=200):
    """Returns estimated player spawn rate based on Gaussian curve"""
    rate = base_rate + (peak_rate - base_rate) * np.exp(-((minute - peak_minute) ** 2) / (2 * spread ** 2))
    return rate

def data_debug(total_players_online,
               total_happiness,
               avg_happiness,
               total_server_latency,
               server_max_capacity
               ):
    print(f"\nTotal players who joined the server: {total_players_online}")
    print(f"Total player happiness: {total_happiness}")
    print(f"Average player happines: {avg_happiness}")
    print(f"Total server latency: {total_server_latency}")
    print(f"Server max capacity: {server_max_capacity}")

def simulate_game_day(workday_minutes, check_interval, server_max_capacity):
    total_players_online = 0
    total_happiness = 0
    new_players = 0
    rejected_players = 0
    disconnections = 0
    matches_started = 0
    
    # Player stack
    players = []
    active_log = []
    total_server_latency = []
    
    # Stochastic Player Spawn Rates
    # idler_weight = np.random.uniform(0.2, 0.4)
    # pro_weight = np.random.uniform(0.6, 1)
    # casual_weight = 1.0 - idler_weight - pro_weight
    # weights = [idler_weight, max(0, casual_weight), pro_weight]
    weights = [0.3, 0.5, 0.2]
    
    for minute in range(workday_minutes):
        is_server_full = len(players) > server_max_capacity
        
        latency_noise = np.random.normal(loc=0, scale=10)  # Random jitter ±10ms
        current_server_latency = max(20, 40 + (len(players) / 5) + latency_noise)
        if random.random() < 0.01:  # 1% chance of a spike
            current_server_latency += random.randint(100, 300)
        
        if random.random() < 0.6:
            new_players = np.abs(np.round(random.gauss(get_spawn_rate(minute), 5))).astype(int)
            total_players_online += new_players
            
            for _ in range(new_players):
                player_type = get_random_type(weights)
                players.append(Player(player_type))
                
        # (Non-pythonic Code) Tick all players and remove those who are done
        active_players = []
        for player in players:
            if player.is_active():
                player.tick(is_server_full, current_server_latency)
                active_players.append(player)
            else:
                total_happiness += player.get_happiness()
        players = active_players
        
        # Optional: print status every 10 minutes
        if (minute + 1) % check_interval == 0:
            print(f"Minute {minute + 1}: {len(players)} active players")
            active_log.append(len(players))
            total_server_latency.append(current_server_latency)
        
        
    # Final status
    total_happiness += sum(player.get_happiness() for player in players)
    avg_happiness = total_happiness / total_players_online
    
    data_debug(total_players_online,
               total_happiness,
               avg_happiness,
               sum(total_server_latency)/len(total_server_latency),
               server_max_capacity)
    
    return total_players_online, avg_happiness, active_log, total_server_latency, server_max_capacity


if __name__ == "__main__":
    # Simulation Parameters
    SIMULATIONS = 100
    WORKDAY_MINUTES = 1440
    CHECK_INTERVAL = 10  # Every 10 minutes
    SERVER_MAX_CAPACITY_SAMPLE = np.random.uniform(100, 1000, SIMULATIONS)

    # Run and collect data for all simulations
    all_simulations = []
    for sim in range(SIMULATIONS):
        print(f"Simulating day {sim + 1}/{SIMULATIONS}")
        
        tpo, avg_happy, log, tsl, smc = simulate_game_day(
            WORKDAY_MINUTES, 
            CHECK_INTERVAL, 
            int(SERVER_MAX_CAPACITY_SAMPLE[sim]), 
        )
        
        all_simulations.append((tpo, avg_happy, log, tsl, smc))

    minutes = np.arange(144)
    hour_ticks = np.arange(0, 144, 6)
    hour_labels = [f"{h}:00" for h in range(24)]
    
    # First figure: Line plot
    plt.figure(figsize=(14, 7))
    for _, _, sim_log, sim_tsl, _ in all_simulations:
        plt.plot(minutes, sim_log, alpha=0.05, color='blue')  # Light opacity for visibility
        plt.plot(minutes, sim_tsl, alpha=0.05, color='#FFA500')  # Light opacity for visibility
    plt.plot([], [], color='blue', alpha=0.5, label='Expected Spawn Rate')
    plt.plot([], [], color='#FFA500', alpha=0.5, label='Total Server Latency')
    plt.axvline(108, color='red', linestyle='--', label='18:00')
    plt.axvline(120, color='green', linestyle='--', label='20:00 (Peak)')
    plt.axvline(132, color='red', linestyle='--', label='22:00')
    plt.title(f"{SIMULATIONS} Simulated Game Days - Player Spawn Rate Over a Day")
    plt.xticks(hour_ticks, hour_labels)
    plt.xlabel("Time (1-hour intervals)")
    plt.ylabel("Estimated Player Spawns per Minute")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    # Second figure: Scatter plot
    plt.figure(figsize=(14, 7))
    for _, avg_happy, _, _, smc in all_simulations:
        plt.scatter(avg_happy, smc, color='red')
    plt.scatter([], [], color='red', label='Scatter Plot')
    plt.axvline(100, color='red', linestyle='--', label='Max Happiness')
    plt.title(f"{SIMULATIONS} Simulated Game Days - Average Happiness vs. Server Max Capacity")
    plt.xlabel("Average Player Happiness")
    plt.ylabel("Server Max Capacity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    plt.show()