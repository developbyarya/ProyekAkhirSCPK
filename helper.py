import numpy as np

def split_empasis(arr: np.array):
    emphasis_set = set()
    for item in arr:
        parts = [e.strip() for e in item.split(';')]
        emphasis_set.update(parts)

    # If you want it as a list
    emphasis_list = sorted(emphasis_set)
    return emphasis_list

def count_matches(emphasis_string, selected):
    emphases = [e.strip() for e in emphasis_string.split(';')]
    return sum(1 for e in emphases if e in selected)

def budget_score(expense, min_budget, max_budget):
    if expense < min_budget or expense > max_budget:
        return 0
    return 1 - ((expense - min_budget) / (max_budget - min_budget + 1e-6))  # avoid division by zero