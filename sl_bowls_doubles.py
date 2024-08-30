import bowls_doubles as rr
import streamlit as st


def print_schedule(schedule, sitting_out):
    # Print the final schedule and players sitting out each round
    for round_num, round_games in enumerate(schedule):
        st.write(f"Round {round_num + 1}:")
        if sitting_out and len(sitting_out[round_num]) > 0:
            st.write(f"  Players sitting out: {', '.join(map(str, sitting_out[round_num]))}")
        for game_num, (team1, team2) in enumerate(round_games):
            # Format and print the match details
            team1_str = f"{team1[0]} and {team1[1]}"
            team2_str = f"{team2[0]} and {team2[1]}"
            st.write(f"  Game {game_num + 1}: {team1_str} vs {team2_str}")
        st.write('\n')


def print_grid(grid):
    header = ["Player"] + [f"Round {i + 1}" for i in range(len(grid[0]))]
    st.write(" | ".join(header))
    st.write("-" * len(" | ".join(header)))

    for i, row in enumerate(grid):
        row_data = [str(i + 1)] + row
        st.write(" | ".join(row_data))


# Example usage
# Streamlit app
st.title("Bowls Doubles Scheduler")

# Input for number of players
num_players = st.number_input("Enter the number of players:", min_value=11, max_value=30, value=16, step=1)
# Input for random number sed
random_seed = st.number_input("Enter a random seed:", min_value=1, max_value=100, value=42, step=1)

# Generate the schedule when the user enters the number of players
if st.button("Generate Schedule"):
    schedule, sitting_out, warning, opponent_tolerance, tolerance_violations = rr.monte_carlo_schedule(num_players, random_seed)

    if schedule:
        print_schedule(schedule, sitting_out)
        # grid = rr.generate_grid(schedule, sitting_out)
        # print_grid(grid)

        st.write("\nFinal Opponent Tolerance:", opponent_tolerance)
        # if tolerance_violations:
        #     print("Games that required tolerance > 0:")
        #     for round_num, tolerance, team1, team2 in tolerance_violations:
        #         st.write(f"  Round {round_num}: {tuple(team1)} vs {tuple(team2)} (Tolerance: {tolerance})")
    else:
        st.write("No valid schedule found.")