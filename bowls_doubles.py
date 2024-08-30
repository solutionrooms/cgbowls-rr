import random
import numpy as np
from collections import defaultdict

num_players = 14


def distribute_sit_outs(num_players, num_rounds):
    # Calculate how many players should sit out in total
    total_sit_outs = num_players

    # first available sit out value
    sit_out_q1 = total_sit_outs % 4
    # first available sit out value
    sit_out_q2 = sit_out_q1 + 4

    # return empty array if num_players is multiple of 4
    if sit_out_q1 == 0:
        return [[] for _ in range(num_rounds)]  # No sit-outs needed if players are already a multiple of 4

    # Create an array with base sit-outs for each round
    sit_out_distribution = [sit_out_q1] * num_rounds

    # Distribute the extra sit-outs across some rounds
    for i in range(num_rounds):
        if sum(sit_out_distribution) == total_sit_outs:
            continue
        if sum(sit_out_distribution) > total_sit_outs:
            print(f'Failed to distribute with {num_players} players')
            return 'Fail'
        else:
            sit_out_distribution[i] = sit_out_q2

    # Track players who have already sat out
    all_players = np.arange(1, num_players + 1)
    players_sitting_out = set()

    # List to store the sit-out selection for each round
    sit_outs_each_round = []

    for num_sit_out in sit_out_distribution:
        available_players = np.setdiff1d(all_players, list(players_sitting_out))

        # Ensure no player sits out more than once
        if len(available_players) >= num_sit_out:
            selected_sit_outs = np.random.choice(available_players, num_sit_out, replace=False)
        else:
            selected_sit_outs = available_players

        # Add the selected players to the tracking set
        players_sitting_out.update(selected_sit_outs)

        # Append the selected sit-outs for the current round
        sit_outs_each_round.append(selected_sit_outs.tolist())

    return sit_outs_each_round


def generate_random_schedule(num_players, opponent_tolerance, current_round, random_seed):
    print(f'random seed: {random_seed}')
    random.seed(random_seed)
    np.random.seed(random_seed)

    # Validate the number of players
    if num_players < 4 or num_players > 50:
        raise ValueError("Number of players must be between 4 and 50")

    # Determine the number of rounds: 4 rounds if num_players is a multiple of 4, otherwise 5 rounds
    num_rounds = 4 if num_players % 4 == 0 else 5

    # Create an array of players (1 through num_players)
    players = np.arange(1, num_players + 1)

    # Initialize history matrices and tracking arrays
    partner_history = np.zeros((num_players, num_players), dtype=int)
    opponent_history = np.zeros((num_players, num_players), dtype=int)
    games_per_player = np.zeros(num_players, dtype=int)
    rounds_sat_out = np.zeros(num_players, dtype=int)

    # Lists to store the final schedule, players sitting out, and tolerance violations
    schedule = []
    tolerance_violations = []

    # Distribute sit-outs for each round
    sit_outs_each_round = distribute_sit_outs(num_players, num_rounds)

    def is_valid_game(team1, team2):
        p1, p2 = team1
        p3, p4 = team2

        # Ensure no player plays more than 4 games
        if any(games_per_player[[p1 - 1, p2 - 1, p3 - 1, p4 - 1]] >= 4):
            return False

        # Ensure no player has the same partner more than once
        if partner_history[p1 - 1, p2 - 1] or partner_history[p3 - 1, p4 - 1]:
            return False

        # Ensure no player has played against the same opponents more than the allowed tolerance
        if any(opponent_history[p1 - 1, [p3 - 1, p4 - 1]] > opponent_tolerance) or \
                any(opponent_history[p2 - 1, [p3 - 1, p4 - 1]] > opponent_tolerance):
            return False

        return True

    def record_game(team1, team2):
        p1, p2 = team1
        p3, p4 = team2

        # Update partner and opponent history
        partner_history[p1 - 1, p2 - 1] = partner_history[p2 - 1, p1 - 1] = 1
        partner_history[p3 - 1, p4 - 1] = partner_history[p4 - 1, p3 - 1] = 1
        opponent_history[p1 - 1, [p3 - 1, p4 - 1]] += 1
        opponent_history[p2 - 1, [p3 - 1, p4 - 1]] += 1
        opponent_history[p3 - 1, [p1 - 1, p2 - 1]] += 1
        opponent_history[p4 - 1, [p1 - 1, p2 - 1]] += 1

        # Track games that required a tolerance > 0 (for reporting later)
        max_opponent_tolerance = max(opponent_history[p1 - 1, [p3 - 1, p4 - 1]].max(),
                                     opponent_history[p2 - 1, [p3 - 1, p4 - 1]].max())
        if max_opponent_tolerance > 1:
            tolerance_violations.append((current_round + 1, max_opponent_tolerance - 1, team1, team2))

        # Increment game count for each player in the current game
        games_per_player[[p1 - 1, p2 - 1, p3 - 1, p4 - 1]] += 1

    while len(schedule) < num_rounds:
        round_games = []
        available_players = players.copy()

        # Remove players who are sitting out in the current round
        sit_out_players = sit_outs_each_round[len(schedule)]
        available_players = available_players[~np.isin(available_players, sit_out_players)]

        attempts = 0

        # Create games for the round
        while len(available_players) >= 4 and attempts < 100:
            # Randomly select teams of 2 players each
            team1 = np.random.choice(available_players, 2, replace=False)
            available_players = available_players[~np.isin(available_players, team1)]

            team2 = np.random.choice(available_players, 2, replace=False)
            available_players = available_players[~np.isin(available_players, team2)]

            # Validate and record the game if it meets all criteria
            if is_valid_game(team1, team2):
                round_games.append((team1, team2))
                record_game(team1, team2)
            else:
                # If the game isn't valid, return the players to the pool and try again
                available_players = np.append(available_players, team1)
                available_players = np.append(available_players, team2)
                attempts += 1

        # Ensure that the number of games created matches the expected number
        expected_games = len(available_players) // 4
        if len(round_games) != expected_games:
            warning = "Warning: Optimization compromised to meet constraints."
        schedule.append(round_games)

    return schedule, sit_outs_each_round, warning, opponent_tolerance, tolerance_violations


def validate_schedule(schedule, sitting_out, num_players):
    games_per_player = np.zeros(num_players, dtype=int)
    rounds_sat_out = np.zeros(num_players, dtype=int)

    # Validate the schedule to ensure all rules are followed
    for round_num, round_games in enumerate(schedule):
        for team1, team2 in round_games:
            players = np.concatenate((team1, team2)) - 1
            games_per_player[players] += 1
        if len(sitting_out) > round_num:
            for player in sitting_out[round_num]:
                rounds_sat_out[player - 1] += 1

    # Check that each player plays exactly 4 games if possible
    if not np.all(games_per_player == 4):
        return False

    # Check that no player sits out more than once
    if not np.all(rounds_sat_out <= 1):
        return False

    return True


def monte_carlo_schedule(num_players, random_seed, iterations=1000, ):
    opponent_tolerance = 0
    for i in range(iterations):
        current_round = len(schedule) if 'schedule' in locals() else 0
        schedule, sitting_out, warning, opponent_tolerance, tolerance_violations = generate_random_schedule(num_players,
                                                                                                            opponent_tolerance,
                                                                                                            current_round,
                                                                                                            random_seed)
        if validate_schedule(schedule, sitting_out, num_players):
            return schedule, sitting_out, warning, opponent_tolerance, tolerance_violations
        if (i + 1) % 10 == 0:
            opponent_tolerance += 1

    return None, [], "Warning: No valid schedule found.", opponent_tolerance, []




def generate_game_labels(num_games):
    labels = []
    for i in range(num_games):
        labels.append(chr(65 + i))  # ASCII 65 is 'A'
    return labels


def generate_grid(schedule, sitting_out):
    num_players = len(schedule[0][0][0]) * 2 * len(schedule[0])  # number of players from schedule
    num_rounds = len(schedule)

    grid = [['X' for _ in range(num_rounds)] for _ in range(num_players)]

    for round_num, round_games in enumerate(schedule):
        game_labels = generate_game_labels(len(round_games))

        for game_index, (team1, team2) in enumerate(round_games):
            label = game_labels[game_index]
            for p in team1:
                grid[p - 1][round_num] = label + '1'
            for p in team2:
                grid[p - 1][round_num] = label + '2'

        for p in sitting_out[round_num]:
            grid[p - 1][round_num] = 'X'

    return grid

# # Test the function with any number of players from 4 to 50
# schedule, sitting_out, warning, opponent_tolerance, tolerance_violations = monte_carlo_schedule(num_players,
#                                                                                                 iterations=100000)
# if schedule:
#     print_schedule(schedule, sitting_out)
#     print(f"\nFinal Opponent Tolerance: {opponent_tolerance}")
#     if tolerance_violations:
#         print("Games that required tolerance > 0:")
#         for round_num, tolerance, team1, team2 in tolerance_violations:
#             print(f"  Round {round_num}: {tuple(team1)} vs {tuple(team2)} (Tolerance: {tolerance})")
#     if warning:
#         print(warning)
# else:
#     print("No valid schedule found.")
