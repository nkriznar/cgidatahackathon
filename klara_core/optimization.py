"""
KLARA OS — Optimization Models (Step 8 & 9)

Implements the optimization logic using PuLP to solve:
Solution 1: Navigation Optimization Model (Strain reduction across care pathways)
"""

import pulp
import time

def optimize_pathways(patients: list, capacities: dict):
    """
    Step 8.1 - Formulation
    Linear Programming assignment problem using PuLP.
    Assigns patients to pathways to minimize total system strain.

    Args:
        patients: List of dicts, e.g., [{'id': 'p1', 'risk': 'high', 'pref': 'ED'}, ...]
        capacities: Dict of pathway capacities, e.g., {'ED': 100, 'VirtualCareNS': 50, ...}

    Objective: Minimize Z = Σi Σj [(strain_j × x_ij) + (mismatch_ij × x_ij) + (wait_j × x_ij) - (preference_ij × x_ij)]

    Returns:
        dict: Patient ID to assigned pathway.
    """
    start_time = time.time()

    # Define Pathways
    pathways = ["VirtualCareNS", "Pharmacy", "Primary Care", "UTC", "ED", "Self-Care", "811"]

    # Problem: Minimize System Strain
    prob = pulp.LpProblem("Navigation_Optimization_Model", pulp.LpMinimize)

    # Decision variables: x_ij in {0, 1}
    x = pulp.LpVariable.dicts("assignment",
                              [(p["id"], j) for p in patients for j in pathways],
                              cat='Binary')

    # Heuristic metrics for demonstration (would be pulled from Layer 3 in production)
    strain = {"VirtualCareNS": 2, "Pharmacy": 1, "Primary Care": 5, "UTC": 7, "ED": 10, "Self-Care": 0, "811": 1}
    wait = {"VirtualCareNS": 1, "Pharmacy": 0, "Primary Care": 14, "UTC": 4, "ED": 8, "Self-Care": 0, "811": 0}

    def calc_mismatch(patient_risk, pathway):
        # High risk requires ED or UTC. Going elsewhere is a huge mismatch.
        if patient_risk == "high" and pathway not in ["ED", "UTC"]:
            return 1000
        # Mental health should ideally go to Primary Care or VirtualCareNS
        if patient_risk == "mental_health" and pathway not in ["VirtualCareNS", "Primary Care"]:
            return 50
        # Low risk to ED is a high mismatch (causes strain)
        if patient_risk == "low" and pathway in ["ED", "UTC"]:
            return 100
        return 0

    # Objective Function
    objective = []
    for p in patients:
        for j in pathways:
            mismatch = calc_mismatch(p.get("risk", "low"), j)
            # Simple preference matching logic (preference = 10 if matched, else 0)
            preference = 10 if p.get("pref") == j else 0
            
            cost = strain[j] + mismatch + wait[j] - preference
            objective.append(cost * x[(p["id"], j)])

    prob += pulp.lpSum(objective), "Total_System_Strain"

    # Constraints
    
    # 1. One-assignment: Each patient assigned to exactly one pathway
    for p in patients:
        prob += pulp.lpSum([x[(p["id"], j)] for j in pathways]) == 1, f"One_Assignment_{p['id']}"

    # 2. Capacity: Σi x_ij <= C_j
    for j in pathways:
        if j in capacities:
            prob += pulp.lpSum([x[(p["id"], j)] for p in patients]) <= capacities[j], f"Capacity_{j}"

    # 3. Clinical Safety (RED -> ED/UTC only) is handled by the high mismatch penalty
    # (or could be a hard constraint)
    for p in patients:
        if p.get("risk") == "high":
            for j in pathways:
                if j not in ["ED", "UTC"]:
                    prob += x[(p["id"], j)] == 0, f"Clinical_Safety_{p['id']}_{j}"

    # Solve the problem
    # Using default CBC solver included with PuLP
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    solve_time_ms = (time.time() - start_time) * 1000

    assignments = {}
    if pulp.LpStatus[prob.status] == "Optimal":
        for p in patients:
            for j in pathways:
                if pulp.value(x[(p["id"], j)]) == 1:
                    assignments[p["id"]] = j
    
    return {
        "status": pulp.LpStatus[prob.status],
        "assignments": assignments,
        "solve_time_ms": solve_time_ms
    }
