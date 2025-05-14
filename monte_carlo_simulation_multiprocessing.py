import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from Engine.simulation_engine import simulate_game_day
from multiprocessing import Pool, cpu_count


# Simulation Parameters
SIMULATIONS = 1000
WORKDAY_MINUTES = 1440  # Minutes over 24 hours
CHECK_INTERVAL = 10  # Debug Print Every 10 minutes

# Agent Based Parameters (Players)
SPAWN_BASE = 5
SPAWN_PEAK = 15

# Server Capability Parameters 
SERVERS = 3
MINIMUM_SERVER_CAPACITY = 100
MAXIMUM_SERVER_CAPACITY = 300
SERVER_MAX_CAPACITY_SAMPLE = np.random.uniform(MINIMUM_SERVER_CAPACITY, 
                                                MAXIMUM_SERVER_CAPACITY, 
                                                SIMULATIONS)

if __name__ == "__main__":
    # Worker function to simulate one day
    def simulate_worker(args):
        sim_idx, smc_value, servers = args
        print(f"[Worker] Simulating day {sim_idx + 1}")
        tpo, avg_happy, log, tsl, smc, hbt, dbt, drop_out = simulate_game_day(
            WORKDAY_MINUTES,
            CHECK_INTERVAL,
            smc_value,
            servers
        )
        return {
            "tpo": tpo,
            "avg_happy": avg_happy,
            "log": log,
            "tsl": tsl,
            "smc": smc,
            "hbt": hbt,
            "dbt": dbt,
            "drop_out": drop_out,
        }
        
    # Prepare simulation inputs
    args_list = [(i, np.round(SERVER_MAX_CAPACITY_SAMPLE[i]), SERVERS) for i in range(SIMULATIONS)]

    # Run simulations in parallel
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(simulate_worker, args_list)
   
    # Run and collect data for all simulations
    all_simulations = []
    all_dropouts_per_run_by_type = []  
    all_dropouts_by_type = {"idler": 0, "casual": 0, "pro": 0}
    all_happiness_by_type = {"idler": [], "casual": [], "pro": []}
    
    for result in results:
        all_simulations.append((
            result["tpo"], result["avg_happy"], result["log"], result["tsl"], result["smc"]
        ))
        all_dropouts_per_run_by_type.append(result["dbt"])
        for key in all_happiness_by_type:
            all_happiness_by_type[key].extend(result["hbt"][key])
            all_dropouts_by_type[key] += result["dbt"][key]

    minutes = np.arange(144)
    hour_ticks = np.arange(0, 144, 6)
    hour_labels = [f"{h}" for h in range(24)]
    
    
    fig, axs = plt.subplots(2, 2, figsize=(19, 10))  # 2 rows x 2 cols
    
    # Third figure: Line plot
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
    
    # Fourth figure: Scatter plot
    passed = 0
    failed = 0
    for _, avg_happy, _, _, smc in all_simulations:
        if avg_happy >= 75:
            axs[1, 1].scatter(avg_happy, smc, color='green')
            passed += 1
        else:
            axs[1, 1].scatter(avg_happy, smc, color='red')
            failed += 1
            
    # Percentages
    total = passed + failed
    pass_percent = round((passed / total) * 100, 1)
    fail_percent = round((failed / total) * 100, 1)
    
    # Dummy points for legend
    axs[1, 1].scatter([], [], color='green', label=f'Pass: {passed} ({pass_percent}%)')
    axs[1, 1].scatter([], [], color='red', label=f'Fail: {failed} ({fail_percent}%)')
    axs[1, 1].axvline(75, color='orange', linestyle='--', label='Passable Happiness')
    axs[1, 1].axvline(100, color='red', linestyle='--', label='Max Happiness')
    
    axs[1, 1].set_title(f"{SIMULATIONS} Simulated Game Days - Average Happiness vs. Server Max Capacity")
    axs[1, 1].set_xlabel("Average Player Happiness")
    axs[1, 1].set_ylabel("Server Max Capacity")
    axs[1, 1].grid(True)
    axs[1, 1].legend()
    
    # First Figure: Bar Chart
    types = list(all_dropouts_by_type.keys())
    values = [all_dropouts_by_type[t] for t in types]
    colors = ['gray', 'orange', 'green']
    bars = axs[0, 0].bar(types, values, color=colors)
    for bar, t, v in zip(bars, types, values): # Add legend with dropout count per type
        bar.set_label(f"{t.capitalize()}: {v} dropped out")
                
    axs[0, 0].legend()
    axs[0, 0].set_title("Total Dropouts by Player Type")
    axs[0, 0].set_ylabel("Dropout Count")
    axs[0, 0].set_xlabel("Player Type")
    axs[0, 0].grid(axis='y')
    

    # Second Figure: Boxplot Chart
    axs[0, 1].boxplot([all_happiness_by_type[t] for t in types], tick_labels=types)
    axs[0, 1].set_title("Final Happiness Distribution by Player Type")
    axs[0, 1].set_ylabel("Happiness")
    axs[0, 1].set_xlabel("Player Type")
    axs[0, 1].grid(True)
    
    for t in types: # Compute stats and build legend
        values = all_happiness_by_type[t]
        mean_val = round(np.mean(values), 2)
        median_val = round(np.median(values), 2)
        axs[0, 1].scatter([], [], label=f"{t.capitalize()} - Mean: {mean_val}, Median: {median_val}")
    axs[0, 1].legend()
    
  
    
    # Track how many overloads happen per server capacity
    # Figure 1 - Server Capacity vs. % of Overloaded Runs
    overload_counts = defaultdict(int)
    total_counts = defaultdict(int)
    dropouts_by_type_across_runs = defaultdict(list)  # type -> list of dropouts per run
    latency_by_cap = []

    for _, _, _, tsl, smc in all_simulations:
        avg_latency = round(np.mean(tsl), 2)
                
        above_critical_value = 0
        for latency in tsl:
            if latency >= 100.0:
                above_critical_value += 1
                
        pct_latency = round(above_critical_value / len(tsl), 2) * 100
        # print(f"Avg: {avg_latency} | Pct: %{pct_latency}")
        latency_by_cap.append((smc, avg_latency, pct_latency))
        

 
    # Figure 2 - Average Dropouts per Player Type Across All Runs
    pct_by_cap = defaultdict(list)
    avg_by_cap = defaultdict(list)
    
    types = ['idler', 'casual', 'pro']
    for run_dropouts in all_dropouts_per_run_by_type:  # example: [{'idler': 3, 'casual': 5, 'pro': 1}, {...}]
        for ptype in types:
            dropouts_by_type_across_runs[ptype].append(run_dropouts[ptype])
    averages = [np.mean(dropouts_by_type_across_runs[t]) for t in types]
        
    # Create a single figure with 1 row and 2 columns
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
        
    # --- Subplot 1: Line plot of overload percentages ---
    for smc, avg_latency, pct_latency in latency_by_cap:
        axs[0].plot(smc, pct_latency, marker='o', color='crimson')
        axs[0].plot(smc, avg_latency, marker='x', color='gold')
    
    axs[0].plot([], [], marker='o', color='crimson')
    axs[0].plot([], [], marker='x', color='gold', label='Mean Latency')
    axs[0].plot([], [], marker='s', color='crimson', linestyle='--', label='Max Latency')
    
    axs[0].set_xlabel("Server Max Capacity")
    axs[0].set_ylabel("% of Runs with Overload (Latency > 100ms)")
    axs[0].set_title("Server Capacity vs. % of Overloaded Runs")
    axs[0].grid(True)
    axs[0].set_ylim(0, 100)
    axs[0].axhline(50, color='orange', linestyle='--', label='50% Threshold')
    axs[0].legend()

    # --- Subplot 2: Bar chart of average dropouts by player type ---
    bars = axs[1].bar(types, averages, color=['gray', 'orange', 'green'])
    axs[1].set_title("Average Dropouts per Player Type Across All Runs")
    axs[1].set_xlabel("Player Type")
    axs[1].set_ylabel("Average Dropouts")
    axs[1].grid(axis='y')

    # Add value labels to bars
    for bar in bars:
        yval = bar.get_height()
        axs[1].text(bar.get_x() + bar.get_width() / 2, yval + 0.05, f"{yval:.2f}", ha='center', va='bottom')

    plt.tight_layout()
    plt.show()