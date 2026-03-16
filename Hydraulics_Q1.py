import pulp

# ==========================================
# PART 1: SOLVE THE ORIGINAL OPTIMIZATION
# ==========================================

# 1. Setup the Problem
model = pulp.LpProblem("Pipeline_Leveling", pulp.LpMinimize)

# Existing elevations provided in the case study
E = {1: 51, 2: 67, 3: 61, 4: 55, 5: 40, 6: 45, 7: 20, 8: 22, 
     9: 20, 10: 42, 11: 60, 12: 42, 13: 25, 14: 28, 15: 22}
stations = list(range(1, 16))

# Area multiplier based on 10m Right-of-Way width (100m length * 10m width)
area_multiplier = 2000  

# 2. Decision Variables
x = pulp.LpVariable.dicts("x", stations, lowBound=0) # Proposed elevation
cut = pulp.LpVariable.dicts("cut", stations, lowBound=0)
fill = pulp.LpVariable.dicts("fill", stations, lowBound=0)
v_cut = pulp.LpVariable("v_cut", lowBound=0)
v_fill = pulp.LpVariable("v_fill", lowBound=0)
dump = pulp.LpVariable("dump", lowBound=0)
borrow = pulp.LpVariable("borrow", lowBound=0)

# 3. Original Objective Function (Minimize Cost)
model += 150 * v_cut + 100 * v_fill + 70 * dump + 120 * borrow, "Total_Cost_Objective"

# 4. Constraints
# Volumetric aggregations 
model += v_cut == area_multiplier * pulp.lpSum([cut[i] for i in range(2, 15)])
model += v_fill == area_multiplier * pulp.lpSum([fill[i] for i in range(2, 15)])

# Mass-Haul Balance Equation
model += v_cut + borrow == v_fill + dump

# Station Elevation Definitions
for i in stations:
    model += x[i] - E[i] == fill[i] - cut[i]

# Fixed Boundary Conditions
model += x[1] == 51
model += x[15] == 22

# 8% Maximum Allowable Grade Constraints
for i in range(1, 15):
    model += x[i+1] - x[i] <= 8, f"Grade_Max_Pos_{i}"
    model += x[i] - x[i+1] <= 8, f"Grade_Max_Neg_{i}"

# 10% Maximum Allowable Change in Grade Constraints
for i in range(2, 15):
    model += (x[i+1] - x[i]) - (x[i] - x[i-1]) <= 10, f"Grade_Change_Pos_{i}"
    model += (x[i] - x[i-1]) - (x[i+1] - x[i]) <= 10, f"Grade_Change_Neg_{i}"

# Boundary Grade Changes
model += (x[2] - x[1]) - 4 <= 10, "Bound_In_Pos"
model += 4 - (x[2] - x[1]) <= 10, "Bound_In_Neg"
model += -3 - (x[15] - x[14]) <= 10, "Bound_Out_Pos"
model += (x[15] - x[14]) - (-3) <= 10, "Bound_Out_Neg"

# 5. Solve the Original Model
model.solve()

# 6. Output Original Results
print(f"--- ORIGINAL OPTIMAL SOLUTION ---")
print(f"Status: {pulp.LpStatus[model.status]}")
original_cost = pulp.value(model.objective)
print(f"Total Minimum Cost: ₹{original_cost:,.2f}\n")

print("Elevations:")
for i in stations:
    print(f"Station {i}: {x[i].varValue}m (Cut: {cut[i].varValue}m, Fill: {fill[i].varValue}m)")


# ==========================================
# PART 2: FIND ALTERNATIVE OPTIMAL SOLUTION
# ==========================================

print("\n\n--- SEARCHING FOR ALTERNATIVE OPTIMAL PROFILE ---")

# 1. Lock the cost so the solver CANNOT spend more money than the original minimum
model += (150 * v_cut + 100 * v_fill + 70 * dump + 120 * borrow) == original_cost, "Lock_Min_Cost"

# 2. Set a new Objective Function
# We are changing the goal: Instead of minimizing cost (which is now locked), 
# we want to maximize the pipeline's elevation at Station 5.
model.setObjective(x[5])
model.sense = pulp.LpMaximize

# 3. Solve the model again with the new objective
model.solve()

# 4. Output Alternative Results
print(f"Alternative Status: {pulp.LpStatus[model.status]}")
alternative_cost = 150 * v_cut.varValue + 100 * v_fill.varValue + 70 * dump.varValue + 120 * borrow.varValue
print(f"Alternative Total Cost: ₹{alternative_cost:,.2f} (Should match Original exactly)\n")

print("Alternative Elevations:")
for i in stations:
    print(f"Station {i}: {x[i].varValue}m (Cut: {cut[i].varValue}m, Fill: {fill[i].varValue}m)")