import numpy as np
from Engine.simulation_engine import simulate_game_day
from multiprocessing import Pool, cpu_count
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
    start_seq = time.perf_counter()
    
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
    
    args_list = [(i, np.round(SERVER_MAX_CAPACITY_SAMPLE[i]), SERVERS) for i in range(SIMULATIONS)]

    end_seq = time.perf_counter()
    sequential_time = end_seq - start_seq
    print(f"[Sequential] Total time: {sequential_time:.2f} seconds")

    # Run simulations in parallel
    start_par = time.perf_counter()
    results = []
    with Pool(processes=cpu_count()) as pool:
        pool.map(simulate_worker, args_list)
    end_par = time.perf_counter()
    parallel_time = end_par - start_par
    print(f"[Parallel] Total time: {parallel_time:.2f} seconds")
    
    # Estimate P and 1 - P
    T_total = parallel_time  # total wall clock time of parallel version
    T_seq = sequential_time
    P = 1 - (T_seq / T_total)
    print(f"\nEstimated Parallelizable Portion (P): {P:.4f}")
    print(f"Estimated Sequential Portion (1 - P): {1 - P:.4f}")
            
    # Now use Amdahl's Law for a few cores
    for N in range(1, 16):
        S_N = 1 / ((1 - P) + (P / N))
        print(f"Speedup with {N} cores: {S_N:.2f}x")