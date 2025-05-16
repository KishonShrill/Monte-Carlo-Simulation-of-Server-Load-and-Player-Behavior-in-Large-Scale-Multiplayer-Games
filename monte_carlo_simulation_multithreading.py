import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from Engine.simulation_engine import simulate_game_day
from threading import Thread, Lock
import time

# Simulation Parameters
SIMULATIONS = 1000
WORKDAY_MINUTES = 1440  # Minutes over 24 hours
CHECK_INTERVAL = 10  # Debug Print Every 10 minutes

# Agent Based Parameters (Players)
SPAWN_BASE = 5
SPAWN_PEAK = 15

# Server Capability Parameters 
SERVERS = 1
MINIMUM_SERVER_CAPACITY = 100
MAXIMUM_SERVER_CAPACITY = 300
SERVER_MAX_CAPACITY_SAMPLE = np.random.uniform(MINIMUM_SERVER_CAPACITY, 
                                                MAXIMUM_SERVER_CAPACITY, 
                                                SIMULATIONS)

if __name__ == "__main__":
    # Run and collect data for all simulations
    all_simulations = []
    all_dropouts_per_run_by_type = []  
    all_dropouts_by_type = {"idler": 0, "casual": 0, "pro": 0}
    all_happiness_by_type = {"idler": [], "casual": [], "pro": []}
    
    def simulation_thread(sim):
        # print(f"Simulating day {sim + 1}/{SIMULATIONS}")
        tpo, avg_happy, log, tsl, smc, hbt, dbt, drop_out = simulate_game_day(
            WORKDAY_MINUTES, 
            CHECK_INTERVAL, 
            np.round(SERVER_MAX_CAPACITY_SAMPLE[sim]),
            SERVERS
        )
        all_simulations.append((tpo, avg_happy, log, tsl, smc))
        all_dropouts_per_run_by_type.append(dbt)
        for key in all_happiness_by_type:
            all_happiness_by_type[key].extend(hbt[key])
            all_dropouts_by_type[key] += dbt[key]
                
                
    threads = []

    for sim in range(SIMULATIONS):
        thread = Thread(target=simulation_thread, args=(sim,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()