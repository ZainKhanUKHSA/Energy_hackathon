from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Sample data (replace with actual data):
locations = ["L1", "L2", "L3"]  # Green space locations
demand_centres = ["C1", "C2", "C3"]  # Demand centres
demand = {"C1": 100, "C2": 150, "C3": 200}  # Demand at each centre
capacity = {"L1": 300, "L2": 200, "L3": 400}  # Capacity of each location
resource_potential = {"L1": 300, "L2": 200, "L3": 400}  # Resource potential at each location
distance = {  # Distance from locations to demand centres
    ("L1", "C1"): 10, ("L1", "C2"): 15, ("L1", "C3"): 20,
    ("L2", "C1"): 12, ("L2", "C2"): 10, ("L2", "C3"): 25,
    ("L3", "C1"): 30, ("L3", "C2"): 20, ("L3", "C3"): 10
}
green_space_availability = {"L1": 1, "L2": 1, "L3": 1}  # 1 if available, 0 otherwise

# Weights for the objective function
lambda_1 = 1  # Weight for maximising energy supply
lambda_2 = 0.5  # Weight for minimising distance costs

# Define the problem
problem = LpProblem("Renewable_Energy_Plant_Optimization", LpMaximize)

# Decision variables
x = LpVariable.dicts("Build", locations, cat="Binary")  # 1 if a plant is built, 0 otherwise
y = LpVariable.dicts("Supply", [(i, j) for i in locations for j in demand_centres], lowBound=0)  # Energy supplied

# Objective function
problem += (
    lambda_1 * lpSum(y[i, j] for i in locations for j in demand_centres) -
    lambda_2 * lpSum(distance[i, j] * y[i, j] for i in locations for j in demand_centres)
), "Total Objective"

# Constraints
# 1. Demand satisfaction
for j in demand_centres:
    problem += lpSum(y[i, j] for i in locations) >= demand[j], f"Demand_Satisfaction_{j}"

# 2. Plant capacity
for i in locations:
    problem += lpSum(y[i, j] for j in demand_centres) <= capacity[i] * x[i], f"Plant_Capacity_{i}"

# 3. Green space availability
for i in locations:
    problem += x[i] <= green_space_availability[i], f"Green_Space_{i}"

# 4. Resource potential
for i in locations:
    problem += lpSum(y[i, j] for j in demand_centres) <= resource_potential[i], f"Resource_Potential_{i}"

# Solve the problem
problem.solve()

# Output the results
print("Status:", problem.status)
print("Optimal Objective Value:", problem.objective.value())
print("Plant Locations:")
for i in locations:
    print(f"  Build at {i}: {x[i].value()}")
print("Energy Supply:")
for i, j in y:
    print(f"  Supply from {i} to {j}: {y[i, j].value()} MW")