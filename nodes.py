# avg_latency = 30
# disconnect_rate = 0
# unhappy_player_rate = 0
# overloaded_server_rate = 0

# score = 100 - (avg_latency * 0.3) - (disconnect_rate * 50) - (unhappy_player_rate * 40) - (overloaded_server_rate * 30)

# print(f"Score: {score}")


import math
import matplotlib.pyplot as plt
import numpy as np
import random

print(f"{random.random()}")

# # Function to calculate spawn rate
# def get_spawn_rate(minute, base_rate=3, peak_rate=15, peak_minute=1200, spread=200):
#     """Returns estimated player spawn rate based on Gaussian curve"""
#     rate = base_rate + (peak_rate - base_rate) * math.exp(-((minute - peak_minute) ** 2) / (2 * spread ** 2))
#     return rate

# # # Generate data for each minute in a day
# spawn_rates = []
# minutes = list(range(1440))
# for minute in minutes:
#     spawn = np.abs(random.gauss(get_spawn_rate(minute), 5)).astype(int)
#     spawn_rates.append(spawn)
#     print(f"\t{spawn}")

# # # Plot the spawn rate curve
# plt.figure(figsize=(12, 6))
# plt.plot(minutes, spawn_rates, label='Expected Spawn Rate', color='blue')
# plt.axvline(1080, color='red', linestyle='--', label='18:00')
# plt.axvline(1200, color='green', linestyle='--', label='20:00 (Peak)')
# plt.axvline(1320, color='red', linestyle='--', label='22:00')
# plt.title("Player Spawn Rate Over a Day (Gaussian Curve)")
# plt.xlabel("Minute of Day")
# plt.ylabel("Estimated Player Spawns per Minute")
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()
