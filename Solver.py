import gurobipy as gp
from gurobipy import GRB
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from Testcase import Testcase


class Solver:
    def __init__(self):
        self.model = None
        self.solution = None

    def solve(self, testcase):
        # Create a new model
        self.model = gp.Model("restaurant_seating")

        # Extract data from testcase
        N = testcase.Ng
        M = testcase.Md
        C = testcase.Cij
        P = testcase.Pg
        U = testcase.Ug
        S = testcase.Sg
        H = testcase.Hg
        O = testcase.Odt
        alpha = testcase.alpha

        num_groups = int(len(N))
        num_tables = int(len(M))
        T_star = int(max(U) + max(P)) * num_groups
        print(f"Number of groups: {num_groups}")
        print(f"Number of tables: {num_tables}")
        print(f"Total time periods: {T_star}")

        # Decision variables
        a = self.model.addVars(
            num_groups, num_tables, T_star, vtype=GRB.BINARY, name="a"
        )
        b = self.model.addVars(num_groups, num_tables, vtype=GRB.BINARY, name="b")
        c = self.model.addVars(
            num_groups, num_tables, num_tables, vtype=GRB.BINARY, name="c"
        )
        x = self.model.addVars(num_groups, T_star, vtype=GRB.BINARY, name="x")

        # Objective function
        wait_time = gp.quicksum(
            N[g] * (gp.quicksum(t * x[g, t] for t in range(T_star)) + S[g])
            for g in range(num_groups)
        )
        table_minimization = gp.quicksum(
            alpha * (-gp.quicksum(b[g, d] for d in range(num_tables)))
            for g in range(num_groups)
        )

        # self.model.setObjective(wait_time - table_minimization, GRB.MINIMIZE)
        self.model.setObjective(wait_time, GRB.MINIMIZE)

        # Constraints
        self.model.addConstrs(
            (
                gp.quicksum(M[d] * b[g, d] for d in range(num_tables)) >= N[g]
                for g in range(num_groups)
            ),
            name="seating_capacity",
        )
        # self.model.addConstrs(
        #     (
        #         b[g, i]
        #         <= gp.quicksum(C[i, j] * b[g, j] for j in range(num_tables) if i != j)
        #         for g in range(num_groups)
        #         for i in range(num_tables)
        #     ),
        #     name="table_combination",
        # )

        self.model.addConstrs(
            (
                2 * c[g, i, j] <= b[g, i] + b[g, j]
                for g in range(num_groups)
                for i in range(num_tables)
                for j in range(num_tables)
            ),
            name="table_combination_2",
        )

        self.model.addConstrs(
            (
                gp.quicksum(
                    C[i, j] * c[g, i, j]
                    for i in range(num_tables)
                    for j in range(i + 1, num_tables)
                )
                >= gp.quicksum(b[g, i] for i in range(num_tables)) - 1
                for g in range(num_groups)
            ),
            name="table_combination_3",
        )

        self.model.addConstrs(
            (
                a[g, d, t] <= b[g, d]
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(T_star)
            ),
            name="assignment_match",
        )
        self.model.addConstrs(
            (
                gp.quicksum(a[g, d, t] for t in range(T_star)) == P[g] * b[g, d]
                for g in range(num_groups)
                for d in range(num_tables)
            ),
            name="meal_duration",
        )
        self.model.addConstrs(
            (
                gp.quicksum(a[g, d, t2] for t2 in range(t, t + P[g]))
                + 9999 * (1 - b[g, d])
                >= P[g] * x[g, t]
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(T_star - P[g] + 1)
            ),
            name="continuous_assignment",
        )
        self.model.addConstrs(
            (
                gp.quicksum(b[g, d] for d in range(num_tables)) <= H[g]
                for g in range(num_groups)
            ),
            name="max_tables",
        )
        self.model.addConstrs(
            (
                x[g, 0] <= a[g, d, 0] + (1 - b[g, d])
                for g in range(num_groups)
                for d in range(num_tables)
            ),
            name="start_time_0",
        )
        self.model.addConstrs(
            (
                2 * x[g, t] <= a[g, d, t] - a[g, d, t - 1] + 1 + 2 * (1 - b[g, d])
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(1, T_star)
            ),
            name="start_time",
        )
        self.model.addConstrs(
            (
                x[g, t] <= 0
                for g in range(num_groups)
                for t in range(max(0, U[g] - S[g] + 1), T_star)
            ),
            name="max_wait",
        )
        self.model.addConstrs(
            (
                gp.quicksum(a[g, d, t] for g in range(num_groups)) <= 1
                for t in range(T_star)
                for d in range(num_tables)
            ),
            name="single_assignment",
        )
        self.model.addConstrs(
            (
                gp.quicksum(x[g, t] for t in range(T_star)) == 1
                for g in range(num_groups)
            ),
            name="single_start",
        )
        self.model.addConstrs(
            (
                a[g, d, t] <= 0
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(len(O[d]))
                if O[d, t] == 1
            ),
            name="table_unavailability",
        )

        # Optimize the model
        self.model.optimize()

        # Store the solution
        self.solution = {"a": a, "b": b, "x": x, "c": c}

    def report(self):
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            for v in self.model.getVars():
                if v.x > 0.0001:  # Only print non-zero variables
                    print(f"{v.varName}: {v.x}")
        else:
            print("No optimal solution found")

    def to_solution(self, testcase):
        N = testcase.Ng
        M = testcase.Md
        C = testcase.Cij
        P = testcase.Pg
        U = testcase.Ug
        S = testcase.Sg
        H = testcase.Hg
        O = testcase.Odt
        alpha = testcase.alpha

        num_groups = int(len(N))
        num_tables = int(len(M))
        T_star = int(max(U) + max(P)) * num_groups

        if self.model.status == GRB.OPTIMAL:
            solution = {
                "a": np.array(
                    [
                        [
                            [self.solution["a"][g, d, t].x for t in range(T_star)]
                            for d in range(num_tables)
                        ]
                        for g in range(num_groups)
                    ]
                ),
                "b": np.array(
                    [
                        [self.solution["b"][g, d].x for d in range(num_tables)]
                        for g in range(num_groups)
                    ]
                ),
                "x": np.array(
                    [
                        [self.solution["x"][g, t].x for t in range(T_star)]
                        for g in range(num_groups)
                    ]
                ),
                "c": np.array(
                    [
                        [
                            [[self.solution["c"][g, i, j].x for j in range(num_tables)]]
                            for i in range(num_tables)
                        ]
                        for g in range(num_groups)
                    ]
                ),
            }
            return solution
        else:
            return None

    def draw_solution(self, solution):
        x = solution["x"]
        a = solution["a"]
        b = solution["b"]
        num_groups = len(x)
        num_tables = len(b[0])
        T_star = len(x[0])

        fig, gnt = plt.subplots()

        gnt.set_xlabel("Time")
        gnt.set_ylabel("Tables")

        gnt.set_xticks(np.arange(0, T_star, step=1))
        gnt.set_yticks(np.arange(0, num_tables, step=1))
        gnt.set_xticklabels(np.arange(0, T_star, step=1))
        gnt.set_yticklabels(np.arange(0, num_tables, step=1))

        gnt.grid(True)

        colors = plt.cm.get_cmap("tab20", num_groups)

        for g in range(num_groups):
            for d in range(num_tables):
                for t in range(T_star):
                    if a[g, d, t] > 0.5:
                        gnt.broken_barh([(t, 1)], (d - 0.4, 0.8), facecolors=colors(g))

        plt.show()


if __name__ == "__main__":
    # Load data from CSV and create Testcase object
    testcase = Testcase.from_csv("testcase_data.csv")

    # Solve the testcase
    solver = Solver()
    solver.solve(testcase)
    solver.report()
    solution = solver.to_solution(testcase)
    if solution:
        solver.draw_solution(solution)
    else:
        print("No solution found")
