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
        print("Occupancy Matrix (O):", O)

        G = len(N)  # Number of groups
        D = len(M)  # Number of tables
        T = len(O[0])  # Number of time periods

        # Sort groups by their waiting time S in descending order
        zipped_lists = zip(S, N, P, U, R, H)
        sorted_zipped_lists = sorted(zipped_lists, reverse=True, key=lambda x: x[0])
        S, N, P, U, R, H = [list(t) for t in zip(*sorted_zipped_lists)]

        # Initialize a_{gdt} as a 3D array of zeros
        a = np.zeros((G, D, T), dtype=int)

        # Function to check if the group can be seated at the given tables
        def can_seat_group_at_tables(g, t, tables):
            total_seats = sum(M[d] for d in tables)
            if total_seats < N[g]:
                return False
            for d in tables:
                if t + P[g] > T or any(O[d][t:t+P[g]] == 1):
                    return False
            for i in range(len(tables)):
                for j in range(i + 1, len(tables)):
                    if C[tables[i]][tables[j]] == 0:
                        return False
            return True

        # Function to seat group at the given tables
        def seat_group_at_tables(g, t, tables):
            for d in tables:
                for duration in range(P[g]):
                    a[g][d][t + duration] = 1
                    O[d][t + duration] = 1

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
                    if not allocated and N[g] > M[d]:
                        for d2 in range(d + 1, D):
                            if can_seat_group_at_tables(g, t, [d, d2]):
                                seat_group_at_tables(g, t, [d, d2])
                                allocated = True
                                break

        print("Sorted Wait Times (S):", S)
        print("Group Sizes (N):", N)
        print("Meal Durations (P):", P)
        # print("Occupancy Matrix (O):", O)
        print("Allocation Matrix (a):", a)

if __name__ == "__main__":
    testcase = Testcase.from_csv("testcase_data.csv")
    solver = FCFS()
    solver.solve(testcase)
