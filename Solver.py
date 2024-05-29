import gurobipy as gp
from gurobipy import GRB
import numpy as np
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
        R = testcase.Rg
        H = testcase.Hg
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
        x = self.model.addVars(num_groups, T_star, vtype=GRB.BINARY, name="x")

        # Objective function
        wait_time = gp.quicksum(
            (1 - R[g]) * N[g] * (gp.quicksum(t * x[g, t] for t in range(T_star)) + S[g])
            for g in range(num_groups)
        )
        table_minimization = gp.quicksum(
            alpha * (H[g] - gp.quicksum(b[g, d] for d in range(num_tables)))
            for g in range(num_groups)
        )

        self.model.setObjective(wait_time - table_minimization, GRB.MINIMIZE)

        # Constraints
        # sum_d M[d] * b[g, d] >= N[g]
        self.model.addConstrs(
            (
                gp.quicksum(M[d] * b[g, d] for d in range(num_tables)) >= N[g]
                for g in range(num_groups)
            ),
            name="seating_capacity",
        )
        # b[g, i] + b[g, j] <= C[i, j] + 1
        self.model.addConstrs(
            (
                b[g, i] + b[g, j] <= C[i, j] + 1
                for g in range(num_groups)
                for i in range(num_tables)
                for j in range(num_tables)
            ),
            name="table_combination",
        )
        # a[g, d, t] <= b[g, d]
        self.model.addConstrs(
            (
                a[g, d, t] <= b[g, d]
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(T_star)
            ),
            name="assignment_match",
        )
        # sum_t' a[g, d, t'] >= P[g] * b[g, d]
        self.model.addConstrs(
            (
                gp.quicksum(a[g, d, t] for t in range(T_star)) == P[g] * b[g, d]
                for g in range(num_groups)
                for d in range(num_tables)
            ),
            name="meal_duration",
        )
        # sum_t' a[g, d, t'] >= P[g] * x[g, t]
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
        # sum_d b[g, d] <= H[g]
        self.model.addConstrs(
            (
                gp.quicksum(b[g, d] for d in range(num_tables)) == 1
                for g in range(num_groups)
            ),
            name="max_tables",
        )
        # 2 * x[g, t] <= a[g, d, t] - a[g, d, t - 1] + 1
        self.model.addConstrs(
            (
                x[g, 0] <= a[g, d, 0] + 9999 * (1 - b[g, d])
                for g in range(num_groups)
                for d in range(num_tables)
            ),
            name="start_time_0",
        )
        self.model.addConstrs(
            (
                2 * x[g, t] <= a[g, d, t] - a[g, d, t - 1] + 1 + 9999 * (1 - b[g, d])
                for g in range(num_groups)
                for d in range(num_tables)
                for t in range(2, T_star)
            ),
            name="start_time",
        )
        # x[g, t] <= 0
        self.model.addConstrs(
            (
                x[g, t] <= 0
                for g in range(num_groups)
                for t in range(max(0, U[g] - S[g] + 1), T_star)
            ),
            name="max_wait",
        )
        # sum_g a[g, d, t] <= 1
        self.model.addConstrs(
            (
                gp.quicksum(a[g, d, t] for g in range(num_groups)) <= 1
                for t in range(T_star)
                for d in range(num_tables)
            ),
            name="single_assignment",
        )
        # sum_t x[g, t] = 1
        self.model.addConstrs(
            (
                gp.quicksum(x[g, t] for t in range(T_star)) == 1
                for g in range(num_groups)
            ),
            name="single_start",
        )

        # Optimize the model
        self.model.optimize()

        # Store the solution
        self.solution = {"a": a, "b": b, "x": x}

    def report(self):
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            for v in self.model.getVars():
                if v.x > 0.0001:  # Only print non-zero variables
                    print(f"{v.varName}: {v.x}")
        else:
            print("No optimal solution found")

    def to_solution(self, testcase):
        # Extract data from testcase
        N = testcase.Ng
        M = testcase.Md
        C = testcase.Cij
        P = testcase.Pg
        U = testcase.Ug
        S = testcase.Sg
        R = testcase.Rg
        H = testcase.Hg
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
            }
            return solution
        else:
            return None


if __name__ == "__main__":
    # Load data from CSV and create Testcase object
    testcase = Testcase.from_csv("testcase_data.csv")

    # Solve the testcase
    solver = Solver()
    solver.solve(testcase)
    solver.report()
    solution = solver.to_solution(testcase)
    if solution:
        print("Solution:", solution)
    else:
        print("No solution found")
