import numpy as np
import random
from Objects.player import Player
import matplotlib.pyplot as plt

# ---------------------------------------------------
# ---------------------------------------------------

AUTOSCALING = False
SERVERS = 5

# ---------------------------------------------------
# ---------------------------------------------------

def get_random_type(spawn_rate):
    # You can change the probability distribution here
    return random.choices(
        ["idler", "casual", "pro"],
        weights=[0.3, 0.5, 0.2*(spawn_rate/15)],  # 30% idlers, 50% casuals, 20% pros
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

def simulate_game_day(workday_minutes, check_interval, server_max_capacity):
    total_players_online = 0
    new_players = 0
    disconnections = 0
    
    happiness_by_type = {"idler": [], "casual": [], "pro": []}
    dropouts_by_type = {"idler": 0, "casual": 0, "pro": 0}
    
    # Player stack
    players = []
    active_log = []
    total_happiness = []
    total_server_latency = []
    
    for minute in range(workday_minutes):
        is_server_full = len(players) > server_max_capacity
        
        if is_server_full and AUTOSCALING:
            server_max_capacity += 50.0  # fake autoscaling
        
        # latency_noise = np.random.normal(loc=0, scale=10)  # Random jitter ±10ms
        current_server_latency = max(20, 40 + (len(players) / 5))
        if random.random() < 0.01:  #! 1% chance of a spike
            current_server_latency += random.randint(100, 300)
        
        if random.random() < 0.6:
            spawn_rate = get_spawn_rate(minute)
            new_players = np.abs(random.gauss(spawn_rate, 5)).astype(int)
            
            for _ in range(new_players):
                if random.random() <= 1 / SERVERS:
                    total_players_online += 1
                    player_type = get_random_type(spawn_rate)
                    players.append(Player(player_type))
                
        # (Non-pythonic Code) Tick all players and remove those who are done
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
        
        # Optional: print status every 10 minutes
        if (minute + 1) % check_interval == 0:
            #! print(f"Minute {minute + 1}: {len(players)} active players | {dropouts_by_type} | {server_max_capacity} | {current_server_latency}")
            active_log.append(len(players))
            total_server_latency.append(current_server_latency)
        
        
    # Final status
    for player in players:
        total_happiness.append(player.get_happiness())
        happiness_by_type[player.type].append(player.get_happiness())
        if player.is_rage_quit():
            dropouts_by_type[player.type] += 1
            disconnections += 1
    
    avg_happiness = sum(total_happiness) / total_players_online
    
    data_debug(total_players_online,
               sum(total_happiness),
               avg_happiness,
               sum(total_server_latency)/len(total_server_latency),
               server_max_capacity,
               disconnections,
               dropouts_by_type)
    
    return total_players_online, avg_happiness, active_log, total_server_latency, server_max_capacity, happiness_by_type, dropouts_by_type, disconnections


if __name__ == "__main__":
    # Simulation Parameters
    SIMULATIONS = 10
    WORKDAY_MINUTES = 1440
    CHECK_INTERVAL = 10  # Every 10 minutes
    SERVER_MAX_CAPACITY_SAMPLE = np.random.uniform(100, 300, SIMULATIONS)
    SPAWN_BASE = 5
    SPAWN_PEAK = 15

    # Run and collect data for all simulations
    all_simulations = []
    all_dropouts_per_run = []  
    all_dropouts_by_type = {"idler": 0, "casual": 0, "pro": 0}
    all_happiness_by_type = {"idler": [], "casual": [], "pro": []}
    
    for sim in range(SIMULATIONS):
        print(f"Simulating day {sim + 1}/{SIMULATIONS}")
        tpo, avg_happy, log, tsl, smc, hbt, dbt, drop_out = simulate_game_day(
            WORKDAY_MINUTES, 
            CHECK_INTERVAL, 
            np.round(SERVER_MAX_CAPACITY_SAMPLE[sim])
        )
        all_simulations.append((tpo, avg_happy, log, tsl, smc))
        all_dropouts_per_run.append(drop_out)
        for key in all_happiness_by_type:
            all_happiness_by_type[key].extend(hbt[key])
            all_dropouts_by_type[key] += dbt[key]

    minutes = np.arange(144)
    hour_ticks = np.arange(0, 144, 6)
    hour_labels = [f"{h}" for h in range(24)]
    
    fig, axs = plt.subplots(2, 2, figsize=(17, 8))  # 2 rows x 2 cols
    
    # First figure: Line plot
    for _, _, sim_log, sim_tsl, _ in all_simulations:
        axs[1, 0].plot(minutes, sim_log, alpha=0.5, color='blue')  # Light opacity for visibility
        axs[1, 0].plot(minutes, sim_tsl, alpha=0.5, color='red')  # Light opacity for visibility
    axs[1, 0].plot([], [], color='blue', alpha=0.5, label='Expected Spawn Rate')
    axs[1, 0].plot([], [], color='red', alpha=0.5, label='Total Server Latency')
    axs[1, 0].axvline(48, color='red', linestyle='--', label='08:00')
    axs[1, 0].axvline(72, color='green', linestyle='--', label='12:00 (Peak)')
    axs[1, 0].axvline(96, color='red', linestyle='--', label='16:00')
    axs[1, 0].set_title(f"{SIMULATIONS} Simulated Game Days - Player Spawn Rate Over a Day")
    axs[1, 0].set_xticks(hour_ticks, hour_labels)
    axs[1, 0].set_xlabel("Time (1-hour intervals)")
    axs[1, 0].set_ylabel("Online Players log per interval")
    axs[1, 0].grid(True)
    axs[1, 0].legend()
    
    # Second figure: Scatter plot
    for _, avg_happy, _, _, smc in all_simulations:
        axs[1, 1].scatter(avg_happy, smc, color='red')
    axs[1, 1].scatter([], [], color='red', label='Scatter Plot')
    axs[1, 1].axvline(100, color='red', linestyle='--', label='Max Happiness')
    axs[1, 1].set_title(f"{SIMULATIONS} Simulated Game Days - Average Happiness vs. Server Max Capacity")
    axs[1, 1].set_xlabel("Average Player Happiness")
    axs[1, 1].set_ylabel("Server Max Capacity")
    axs[1, 1].grid(True)
    axs[1, 1].legend()
    
    # Third Figure: Bar Chart
    types = list(all_dropouts_by_type.keys())
    values = [all_dropouts_by_type[t] for t in types]
    axs[0, 0].bar(types, values, color=['gray', 'orange', 'green'])
    axs[0, 0].set_title("Total Dropouts by Player Type")
    axs[0, 0].set_ylabel("Dropout Count")
    axs[0, 0].set_xlabel("Player Type")
    axs[0, 0].grid(axis='y')

    # Fourth Figure: Boxplot Chart
    axs[0, 1].boxplot([all_happiness_by_type[t] for t in types], tick_labels=types)
    axs[0, 1].set_title("Final Happiness Distribution by Player Type")
    axs[0, 1].set_ylabel("Happiness")
    axs[0, 1].set_xlabel("Player Type")
    axs[0, 1].grid(True)
    
    
    server_caps = [smc for _, _, _, _, smc in all_simulations]
    avg_latencies = [np.mean(tsl) for _, _, _, tsl, _ in all_simulations]
    dropout_counts = [dropouts for dropouts in all_dropouts_per_run]  # you should track this in simulate_game_day


    plt.figure(figsize=(10, 5))
    plt.scatter(server_caps, avg_latencies, c='red')
    plt.xlabel("Server Max Capacity")
    plt.ylabel("Average Latency")
    plt.title("Server Capacity vs. Average Latency")
    plt.grid(True)
    plt.axhline(100, color='orange', linestyle='--', label="Latency Danger Threshold (100ms)")
    plt.legend()
    
    plt.figure(figsize=(10, 5))
    plt.scatter(server_caps, dropout_counts, c='blue')
    plt.xlabel("Server Max Capacity")
    plt.ylabel("Player Dropouts")
    plt.title("Server Capacity vs. Player Dropouts")
    plt.grid(True)

    latency_diffs = np.diff(avg_latencies)
    spike_index = np.argmax(latency_diffs)  # where the biggest jump occurs
    overload_capacity = server_caps[spike_index]
    print(f"🧠 Estimated overload point: Server capacity ≈ {overload_capacity}")

    plt.tight_layout()
    plt.show()