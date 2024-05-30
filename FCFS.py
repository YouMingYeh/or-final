from Testcase import Testcase
import numpy as np

class FCFS:
    def solve(self, testcase):
        # Number of customers in group g
        N = testcase.Ng
        # Number of seats of table d
        M = testcase.Md
        # Binary variable, 1 if tables i and j can be combined for larger groups, 0 otherwise.
        C = testcase.Cij
        # Meal duration for group g, measured in time periods.
        P = testcase.Pg
        # Maximum waiting time allowed for group g before seating, measured in time periods.
        U = testcase.Ug
        # Number of time periods group g has already waited.
        S = testcase.Sg
        # Binary variable indicates if group g has a reservation.
        R = testcase.Rg
        # Maximum number of tables group g is willing to be assigned to.
        H = testcase.Hg
        # Binary variable, 1 if table d is occupied at time t, 0 otherwise.
        O = testcase.Odt
        alpha = testcase.alpha

        G = len(N)  # Number of groups
        D = len(M)  # Number of tables
        T = len(O[0])  # Number of time periods

        # Sort groups by their waiting time S in descending order
        zipped_lists = zip(S, N, P, U, R, H)
        sorted_zipped_lists = sorted(zipped_lists, reverse=True, key=lambda x: x[0])
        S, N, P, U, R, H = [list(t) for t in zip(*sorted_zipped_lists)]

        # Initialize a_{gdt} as a 3D array of zeros
        a = np.zeros((G, D, T), dtype=int)

        # Function to check if the tables form a connected component
        def is_connected(tables):
            if len(tables) <= 1:
                return True
            visited = set()
            to_visit = [tables[0]]
            while to_visit:
                current = to_visit.pop()
                visited.add(current)
                for neighbor in tables:
                    if neighbor != current and C[current][neighbor] == 1 and neighbor not in visited:
                        to_visit.append(neighbor)
            return len(visited) == len(tables)

        # Function to check if the group can be seated at the given tables
        def can_seat_group_at_tables(g, t, tables):
            total_seats = sum(M[d] for d in tables)
            if total_seats < N[g]:
                return False
            if t + P[g] > T:
                return False
            for d in tables:
                if any(O[d][t:t+P[g]] == 1):
                    return False
            return is_connected(tables)

        # Function to seat group at the given tables
        def seat_group_at_tables(g, t, tables):
            for d in tables:
                for duration in range(P[g]):
                    a[g][d][t + duration] = 1
                    O[d][t + duration] = 1

        # Recursive function to find combinations of tables
        def find_table_combinations(g, t, current_tables, start_index):
            if can_seat_group_at_tables(g, t, current_tables):
                seat_group_at_tables(g, t, current_tables)
                return True
            for i in range(start_index, D):
                if len(current_tables) < H[g]:
                    new_tables = current_tables + [i]
                    if find_table_combinations(g, t, new_tables, i + 1):
                        return True
            return False

        # Attempt to allocate groups to tables based on FCFS
        for g in range(G):
            allocated = False
            for t in range(T):
                if allocated:
                    break
                for d in range(D):
                    if O[d][t] == 0 and N[g] <= M[d]:
                        # Check if the table is available for the entire duration of the meal
                        if t + P[g] <= T and all(O[d][t:t+P[g]] == 0):
                            # Allocate table d to group g at time t for the entire meal duration
                            seat_group_at_tables(g, t, [d])
                            allocated = True
                            break
                    if not allocated:
                        if find_table_combinations(g, t, [d], d + 1):
                            allocated = True
                            break

        print("Sorted Wait Times (S):", S)
        print("Group Sizes (N):", N)
        print("Meal Durations (P):", P)
        print("Occupancy Matrix (O):", O)
        print("Allocation Matrix (a):")
        for m in a:
            print(m)

if __name__ == "__main__":
    testcase = Testcase.from_csv("testcase_data.csv")
    solver = FCFS()
    solver.solve(testcase)
