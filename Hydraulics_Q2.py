import pulp

# We wrap your exact code into a function so we can run it twice
# First time: Strict 8% limit
# Second time: 8.5% limit on the single bottleneck segment
def solve_pipeline(relaxed_segment=None, relaxation_amount=0.0):
    # 1. Setup the Problem
    model = pulp.LpProblem("Pipeline_Leveling", pulp.LpMinimize)

    # Existing elevations provided in the case study
    E = {1: 51, 2: 67, 3: 61, 4: 55, 5: 40, 6: 45, 7: 20, 8: 22, 
         9: 20, 10: 42, 11: 60, 12: 42, 13: 25, 14: 28, 15: 22}
    stations = list(range(1, 16))

    # EXACTLY FROM YOUR CODE: Area multiplier is 2000
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

    # 4. Constraints (EXACTLY FROM YOUR CODE)
    model += v_cut == area_multiplier * pulp.lpSum([cut[i] for i in range(2, 15)])
    model += v_fill == area_multiplier * pulp.lpSum([fill[i] for i in range(2, 15)])
    model += v_cut + borrow == v_fill + dump

    for i in stations:
        model += x[i] - E[i] == fill[i] - cut[i]

    model += x[1] == 51
    model += x[15] == 22

    # Maximum Allowable Grade Constraints (Base 8%)
    # This block allows us to relax the specific bottleneck we find later
    for i in range(1, 15):
        pos_limit = 8.0
        neg_limit = 8.0
        
        if relaxed_segment == f"Grade_Max_Pos_{i}": pos_limit += relaxation_amount
        if relaxed_segment == f"Grade_Max_Neg_{i}": neg_limit += relaxation_amount
            
        model += x[i+1] - x[i] <= pos_limit, f"Grade_Max_Pos_{i}"
        model += x[i] - x[i+1] <= neg_limit, f"Grade_Max_Neg_{i}"

    # Maximum Allowable Change in Grade to 10%
    for i in range(2, 15):
        model += (x[i+1] - x[i]) - (x[i] - x[i-1]) <= 10, f"Grade_Change_Pos_{i}"
        model += (x[i] - x[i-1]) - (x[i+1] - x[i]) <= 10, f"Grade_Change_Neg_{i}"

    # Boundary Grade Changes
    model += (x[2] - x[1]) - 4 <= 10, "Bound_In_Pos"
    model += 4 - (x[2] - x[1]) <= 10, "Bound_In_Neg"
    model += -3 - (x[15] - x[14]) <= 10, "Bound_Out_Pos"
    model += (x[15] - x[14]) - (-3) <= 10, "Bound_Out_Neg"

    # Solve quietly to keep terminal clean
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return model

# ==========================================
# PART 1: Run the Baseline Model
# ==========================================
print("--- RUNNING YOUR BASELINE MODEL (STRICT 8% GRADE) ---")
base_model = solve_pipeline()
base_cost = pulp.value(base_model.objective)
print(f"Base Total Cost: ₹{base_cost:,.2f}\n")

# ==========================================
# PART 2: Dig into Sensitivity Data to find Bottleneck
# ==========================================
print("--- SENSITIVITY ANALYSIS ---")
best_segment = None
highest_shadow_price = 0

# Scan all constraints for the highest shadow price among Grade Limits
for name, c in base_model.constraints.items():
    if "Grade_Max" in name and c.pi != 0:
        sp = abs(c.pi)
        if sp > highest_shadow_price:
            highest_shadow_price = sp
            best_segment = name

# A 0.5% relaxation means multiplying the shadow price by 0.5
predicted_savings = highest_shadow_price * 0.5

print(f"The bottleneck constraint is: {best_segment}")
print(f"Its Shadow Price is: ₹{highest_shadow_price:,.2f} per 1% grade change.")
print(f"Predicted savings for 0.5% relaxation: ₹{predicted_savings:,.2f}\n")

# ==========================================
# PART 3: Prove the Savings with a Relaxed Model
# ==========================================
print(f"--- RUNNING RELAXED MODEL (Allowing 8.5% on {best_segment}) ---")
relaxed_model = solve_pipeline(relaxed_segment=best_segment, relaxation_amount=0.5)
relaxed_cost = pulp.value(relaxed_model.objective)
actual_savings = base_cost - relaxed_cost

print(f"New Total Cost:  ₹{relaxed_cost:,.2f}")
print(f"Actual Savings:  ₹{actual_savings:,.2f}")

if round(predicted_savings, 2) == round(actual_savings, 2):
    print("\nCONCLUSION: The sensitivity analysis perfectly predicted the savings!")