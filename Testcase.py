import csv
import random
import numpy as np


class Testcase:
    def __init__(self, Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, Odt, alpha):
        self.Ng = Ng
        self.Md = Md
        self.Cij = Cij
        self.Pg = Pg
        self.Ug = Ug
        self.Sg = Sg
        self.Rg = Rg
        self.Hg = Hg
        self.Odt = Odt
        self.alpha = alpha

    @staticmethod
    def generate_data(
        number_people,
        num_groups,
        num_tables,
        max_seats,
        max_duration,
        max_wait,
        max_tables,
    ):
        Ng = np.random.randint(1, number_people, num_groups)
        Md = np.random.randint(2, max_seats + 1, num_tables)
        Cij_upper = np.triu(np.random.randint(0, 2, (num_tables, num_tables)))
        Cij = Cij_upper + Cij_upper.T - np.diag(Cij_upper.diagonal())
        for i in range(num_tables):
            Cij[i, i] = 1

        Pg = np.random.randint(1, max_duration + 1, num_groups)
        Ug = np.random.randint(max_duration, max_wait + 1, num_groups)
        Sg = np.random.randint(0, max_wait / 2 + 1, num_groups)
        Rg = np.random.randint(0, 1, num_groups)
        Hg = np.random.randint(max_tables, max_tables + 1, num_groups)
        Odt = np.random.randint(0, 2, (num_tables, max_duration * num_groups))
        Odt = np.random.choice(
            [0, 1], size=(num_tables, max_duration * num_groups), p=[0.9, 0.1]
        )
        alpha = random.uniform(0, 1)

        return Testcase(Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, Odt, alpha)

    def save_to_csv(self, filename):
        data = {
            "Ng": self.Ng,
            "Md": self.Md,
            "Cij": self.Cij.flatten(),
            "Pg": self.Pg,
            "Ug": self.Ug,
            "Sg": self.Sg,
            "Rg": self.Rg,
            "Hg": self.Hg,
            "Odt": self.Odt.flatten(),
            "alpha": [self.alpha],
        }

        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            for key, value in data.items():
                writer.writerow([key] + list(value))

    @staticmethod
    def from_csv(filename):
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            data = {rows[0]: np.array(rows[1:], dtype=float) for rows in reader}

        Ng = data["Ng"].astype(int)
        Md = data["Md"].astype(int)
        Cij = data["Cij"].reshape((len(Md), len(Md))).astype(int)
        Pg = data["Pg"].astype(int)
        Ug = data["Ug"].astype(int)
        Sg = data["Sg"].astype(int)
        Rg = data["Rg"].astype(int)
        Hg = data["Hg"].astype(int)
        Odt = data["Odt"].reshape((len(Md), -1)).astype(int)
        alpha = round(data["alpha"][0], 2)

        return Testcase(Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, Odt, alpha)
    
    def dapu(number_people, num_groups, max_duration, max_wait):
        max_seats = 1
        num_tables =10
        Ng = np.random.randint(1, number_people, num_groups)
        Md = np.random.randint(1, max_seats + 1, num_tables)
        Cij = np.zeros((num_tables, num_tables), dtype=int)
        for i in range(num_tables):
            Cij[i, i] = 1
        for i in range(num_tables-1):
            Cij[i, i+1] = 1
            Cij[i+1, i] = 1

        Pg = np.random.randint(1, max_duration + 1, num_groups)
        Ug = np.random.randint(max_duration, max_wait + 1, num_groups)
        Sg = np.random.randint(0, max_wait / 2 + 1, num_groups)
        Rg = np.random.randint(0, 1, num_groups)
        Hg = np.random.randint(10, 10 + 1, num_groups)
        Odt = np.random.randint(0, 2, (num_tables, max_duration * num_groups))
        Odt = np.random.choice(
            [0, 1], size=(num_tables, max_duration * num_groups), p=[1, 0]
        )
        alpha = random.uniform(0, 1)

        return Testcase(Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, Odt, alpha)


if __name__ == "__main__":
    # Generate data and save to CSV
    testcase = Testcase.dapu(
        number_people=5,
        num_groups=5,
        max_duration=5,
        max_wait=30
    )
    testcase.save_to_csv("testcase_data.csv")

    # Load data from CSV and create Testcase object
    loaded_testcase = Testcase.from_csv("testcase_data.csv")
    print("Loaded Testcase:")
    print("Ng - Number of customer in group g:", loaded_testcase.Ng)
    print("Md - Number of seats of table d:", loaded_testcase.Md)
    print(
        "Cij - Binary variable, 1 if tables i and j can be combined for larger groups, 0 otherwise:"
    )
    print(loaded_testcase.Cij)
    print(
        "Pg - Meal duration for group g, measured in time periods:", loaded_testcase.Pg
    )
    print(
        "Ug - Maximum waiting time allowed for group g before seating, measured in time periods.:"
    )
    print(loaded_testcase.Ug)
    print("Sg - Number of time periods group g has already waited:", loaded_testcase.Sg)
    print("Rg - Binary variable indicates if group g has a reservation:")
    print(loaded_testcase.Rg)
    print("Hg - Maximum number of tables group g is willing to be assigned to:")
    print(loaded_testcase.Hg)
    print("Odt - Binary variable, 1 if table d is available at time t, 0 otherwise:")
    print(loaded_testcase.Odt)
    print("alpha:", loaded_testcase.alpha)
