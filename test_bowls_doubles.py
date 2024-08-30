import bowls_doubles as rr

def print_schedule(schedule, sitting_out):
    # Print the final schedule and players sitting out each round
    for round_num, round_games in enumerate(schedule):
        print(f"Round {round_num + 1}:")
        if sitting_out and len(sitting_out[round_num]) > 0:
            print(f"  Players sitting out: {', '.join(map(str, sitting_out[round_num]))}")
        for game_num, (team1, team2) in enumerate(round_games):
            # Format and print the match details
            team1_str = f"{team1[0]} and {team1[1]}"
            team2_str = f"{team2[0]} and {team2[1]}"
            print(f"  Game {game_num + 1}: {team1_str} vs {team2_str}")
        print()

def print_grid(grid):
    header = ["Player"] + [f"Round {i + 1}" for i in range(len(grid[0]))]
    print(" | ".join(header))
    print("-" * len(" | ".join(header)))

    for i, row in enumerate(grid):
        row_data = [str(i + 1)] + row
        print(" | ".join(row_data))

# Example usage
num_players = 17
random_seed = 44
schedule, sitting_out, warning, opponent_tolerance, tolerance_violations = rr.monte_carlo_schedule(num_players, random_seed)

if schedule:
    print_schedule(schedule, sitting_out)
    # grid = rr.generate_grid(schedule, sitting_out)
    # print_grid(grid)

    print("\nFinal Opponent Tolerance:", opponent_tolerance)
    # if tolerance_violations:
    #     print("Games that required tolerance > 0:")
    #     for round_num, tolerance, team1, team2 in tolerance_violations:
    #         print(f"  Round {round_num}: {tuple(team1)} vs {tuple(team2)} (Tolerance: {tolerance})")
else:
    print("No valid schedule found.")