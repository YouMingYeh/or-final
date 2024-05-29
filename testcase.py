import csv
import random
import numpy as np

class Testcase:
    def __init__(self, Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, alpha):
        self.Ng = Ng
        self.Md = Md
        self.Cij = Cij
        self.Pg = Pg
        self.Ug = Ug
        self.Sg = Sg
        self.Rg = Rg
        self.Hg = Hg
        self.alpha = alpha

    @staticmethod
    def generate_data(num_groups, num_tables, max_seats, max_duration, max_wait, max_tables):
        Ng = np.random.randint(1, 11, num_groups)
        Md = np.random.randint(2, max_seats + 1, num_tables)
        Cij = np.random.randint(0, 2, (num_tables, num_tables))
        Pg = np.random.randint(1, max_duration + 1, num_groups)
        Ug = np.random.randint(1, max_wait + 1, num_groups)
        Sg = np.random.randint(0, max_wait + 1, num_groups)
        Rg = np.random.randint(0, 2, num_groups)
        Hg = np.random.randint(1, max_tables + 1, num_groups)
        alpha = random.uniform(0, 1)

        return Testcase(Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, alpha)

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
            "alpha": [self.alpha]
        }

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for key, value in data.items():
                writer.writerow([key] + list(value))

    @staticmethod
    def from_csv(filename):
        with open(filename, mode='r') as file:
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
        alpha = int(data["alpha"][0])

        return Testcase(Ng, Md, Cij, Pg, Ug, Sg, Rg, Hg, alpha)

if __name__ == "__main__":
    # Generate data and save to CSV
    testcase = Testcase.generate_data(num_groups=10, num_tables=5, max_seats=6, max_duration=10, max_wait=5, max_tables=3)
    testcase.save_to_csv("testcase_data.csv")

    # Load data from CSV and create Testcase object
    loaded_testcase = Testcase.from_csv("testcase_data.csv")
    print("Loaded Testcase:")
    print("Ng:", loaded_testcase.Ng)
    print("Md:", loaded_testcase.Md)
    print("Cij:", loaded_testcase.Cij)
    print("Pg:", loaded_testcase.Pg)
    print("Ug:", loaded_testcase.Ug)
    print("Sg:", loaded_testcase.Sg)
    print("Rg:", loaded_testcase.Rg)
    print("Hg:", loaded_testcase.Hg)
    print("alpha:", loaded_testcase.alpha)
