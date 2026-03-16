import pulp

# 1. Setup the Problem
model = pulp.LpProblem("Pipeline_Leveling", pulp.LpMinimize)

# Existing elevations provided in the case study
E = {1: 51, 2: 67, 3: 61, 4: 55, 5: 40, 6: 45, 7: 20, 8: 22, 
     9: 20, 10: 42, 11: 60, 12: 42, 13: 25, 14: 28, 15: 22}
stations = list(range(1, 16))

# --- COST SAVING CHANGE #1 ---
# Reduced Right-of-Way width from 20m to 10m (100m length * 10m width)
area_multiplier = 2000  

# 2. Decision Variables
x = pulp.LpVariable.dicts("x", stations, lowBound=0) # Proposed elevation
cut = pulp.LpVariable.dicts("cut", stations, lowBound=0)
fill = pulp.LpVariable.dicts("fill", stations, lowBound=0)
v_cut = pulp.LpVariable("v_cut", lowBound=0)
v_fill = pulp.LpVariable("v_fill", lowBound=0)
dump = pulp.LpVariable("dump", lowBound=0)
borrow = pulp.LpVariable("borrow", lowBound=0)

# 3. Objective Function (Minimize Cost)
model += 150 * v_cut + 100 * v_fill + 70 * dump + 120 * borrow

# 4. Constraints

# Volumetric aggregations (Stations 1 and 15 are fixed endpoints)
model += v_cut == area_multiplier * pulp.lpSum([cut[i] for i in range(2, 15)]) #from 2 to 14
model += v_fill == area_multiplier * pulp.lpSum([fill[i] for i in range(2, 15)]) #from 2 to 14

# Mass-Haul Balance Equation
model += v_cut + borrow == v_fill + dump

# Station Elevation Definitions
for i in stations:
    model += x[i] - E[i] == fill[i] - cut[i]

# Fixed Boundary Conditions (BUG FIX APPLIED)
model += x[1] == 51
model += x[15] == 22

# --- COST SAVING CHANGE #2 ---
# Increased Maximum Allowable Grade to 8% (was 5%)
for i in range(1, 15):
    model += x[i+1] - x[i] <= 8, f"Grade_Max_Pos_{i}"
    model += x[i] - x[i+1] <= 8, f"Grade_Max_Neg_{i}"

# --- COST SAVING CHANGE #3 ---
# Increased Maximum Allowable Change in Grade to 10% (was 6%)
for i in range(2, 15):
    model += (x[i+1] - x[i]) - (x[i] - x[i-1]) <= 10, f"Grade_Change_Pos_{i}"
    model += (x[i] - x[i-1]) - (x[i+1] - x[i]) <= 10, f"Grade_Change_Neg_{i}"

# Boundary Grade Changes (BUG FIX APPLIED & ALIGNED WITH CHANGE #3)
model += (x[2] - x[1]) - 4 <= 10, "Bound_In_Pos"
model += 4 - (x[2] - x[1]) <= 10, "Bound_In_Neg"
model += -3 - (x[15] - x[14]) <= 10, "Bound_Out_Pos"
model += (x[15] - x[14]) - (-3) <= 10, "Bound_Out_Neg"

# 5. Solve the Model
model.solve()

# 6. Output Results
print(f"Status: {pulp.LpStatus[model.status]}")
print(f"Total Minimum Cost: ₹{pulp.value(model.objective):,.2f}")

print("\n--- Final Elevations ---")
for i in stations:
    print(f"Station {i}: {x[i].varValue}m (Cut: {cut[i].varValue}m, Fill: {fill[i].varValue}m)")

print("\n--- Sensitivity Analysis Data ---")
print("Constraint Shadow Prices (Dual Values):")
for name, c in model.constraints.items():
    if c.pi != 0:
        print(f"{name}: {c.pi}")

print("\nVariable Reduced Costs:")
for v in model.variables():
    if v.dj != 0:
        print(f"{v.name}: {v.dj}")