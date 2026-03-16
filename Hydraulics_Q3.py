import pulp

# 1. Setup the Problem
model = pulp.LpProblem("Pipeline_Boundary_Analysis", pulp.LpMinimize)

# Existing elevations provided in the case study
E = {1: 51, 2: 67, 3: 61, 4: 55, 5: 40, 6: 45, 7: 20, 8: 22, 
     9: 20, 10: 42, 11: 60, 12: 42, 13: 25, 14: 28, 15: 22}
stations = list(range(1, 16))
area_multiplier = 2000  

# 2. Decision Variables
x = pulp.LpVariable.dicts("x", stations, lowBound=0) 
cut = pulp.LpVariable.dicts("cut", stations, lowBound=0)
fill = pulp.LpVariable.dicts("fill", stations, lowBound=0)
v_cut = pulp.LpVariable("v_cut", lowBound=0)
v_fill = pulp.LpVariable("v_fill", lowBound=0)
dump = pulp.LpVariable("dump", lowBound=0)
borrow = pulp.LpVariable("borrow", lowBound=0)

# 3. Objective Function (Minimize Cost)
model += 150 * v_cut + 100 * v_fill + 70 * dump + 120 * borrow

# 4. Constraints
model += v_cut == area_multiplier * pulp.lpSum([cut[i] for i in range(2, 15)])
model += v_fill == area_multiplier * pulp.lpSum([fill[i] for i in range(2, 15)])
model += v_cut + borrow == v_fill + dump

for i in stations:
    model += x[i] - E[i] == fill[i] - cut[i]

# *** WE NAME THE BOUNDARY CONSTRAINTS HERE SO WE CAN ANALYZE THEM ***
model += x[1] == 51, "Boundary_Elevation_Start"
model += x[15] == 22, "Boundary_Elevation_End"

# Grade Constraints (Using your 8% and 10% limits)
for i in range(1, 15):
    model += x[i+1] - x[i] <= 8, f"Grade_Max_Pos_{i}"
    model += x[i] - x[i+1] <= 8, f"Grade_Max_Neg_{i}"

for i in range(2, 15):
    model += (x[i+1] - x[i]) - (x[i] - x[i-1]) <= 10, f"Grade_Change_Pos_{i}"
    model += (x[i] - x[i-1]) - (x[i+1] - x[i]) <= 10, f"Grade_Change_Neg_{i}"

model += (x[2] - x[1]) - 4 <= 10, "Bound_In_Pos"
model += 4 - (x[2] - x[1]) <= 10, "Bound_In_Neg"
model += -3 - (x[15] - x[14]) <= 10, "Bound_Out_Pos"
model += (x[15] - x[14]) - (-3) <= 10, "Bound_Out_Neg"

# 5. Solve the Model quietly
model.solve(pulp.PULP_CBC_CMD(msg=False))

# ==========================================
# 6. Extract and Analyze the Boundary Shadow Prices
# ==========================================
print("--- BOUNDARY CONSTRAINT SENSITIVITY ANALYSIS ---")
print("This evaluates if extending the pipeline model would yield cost savings.\n")

# List of the exact names of the constraints at the edges of our system
boundary_constraints = [
    "Boundary_Elevation_Start", 
    "Boundary_Elevation_End", 
    "Bound_In_Pos", 
    "Bound_In_Neg", 
    "Bound_Out_Pos", 
    "Bound_Out_Neg"
]

for name in boundary_constraints:
    c = model.constraints[name]
    sp = c.pi
    
    if sp != 0:
        print(f"🔴 BOTTLENECK FOUND: {name}")
        print(f"   Shadow Price: ₹{abs(sp):,.2f}")
        print(f"   Meaning: Forcing the pipeline to meet this exact requirement is artificially driving up costs.")
        print(f"   Conclusion: Extending the model to allow this connection point to shift by 1 unit would save ₹{abs(sp):,.2f}.\n")
    else:
        print(f"🟢 NO BOTTLENECK: {name}")
        print(f"   Shadow Price: ₹0.00")
        print(f"   Meaning: This boundary naturally fits the optimal terrain profile.")
        print(f"   Conclusion: Extending the model at this specific interface provides NO immediate cost savings.\n")