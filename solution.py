from functools import reduce
from itertools import groupby
from operator import itemgetter

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
diag_1 = [a + b for a,b in zip(rows, cols)]
diag_2 = [a + b for a,b in zip(rows, cols[::-1])]
diag_units = [diag_1, diag_2]

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

# definition of useful constant data
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# constant data definitions specific for the non diagonal sudoku (not used)
#unitlist_nodiag = row_units + column_units + square_units
#units_nodiag = dict((s, [u for u in unitlist_nodiag if s in u]) for s in boxes)
#peers_nodiag = dict((s, set(sum(units_nodiag[s],[]))-set([s])) for s in boxes)

# constant data definitions specific for the diagonal sudoku
unitlist_diag = row_units + column_units + square_units + diag_units
units_diag = dict((s, [u for u in unitlist_diag if s in u]) for s in boxes)
peers_diag = dict((s, set(sum(units_diag[s],[]))-set([s])) for s in boxes)

# this configuration makes the functions solve the diagonal sudoku
unitlist = unitlist_diag
units = units_diag
peers = peers_diag

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def k_naked_elimination(box_list, values, k=2):
    """Eliminate values using the naked tuple strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked tuples eliminated from peers.
    """
    box_set = set(box_list)
    val_key_list = sorted([(values[b], b) for b in box_set])
    grouped = groupby(val_key_list, itemgetter(0))
    value_occurrence = [(g[0], set([e[1] for e in g[1]])) for g in grouped]
    for idx in range(2,k+1):        
        interesting_sets = list(filter(lambda x: len(x[0]) == len(x[1]) == idx, value_occurrence))
        if not interesting_sets:
            continue
        for s in interesting_sets:
            elements = set(s[0])
            candidates_b = box_set - s[1] 
            for el in candidates_b:
                values[el] = "".join(sorted(set(values[el]) - elements))
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for rc in row_units + column_units:
        k_naked_elimination(box_list=rc, values=values, k=2)
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    size = 10
    values = "".join([str(x) for x in range(1,size)])
    return dict(zip(cross(rows, cols), [values if v == "." else v for v in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate_box(box, values):
    """Eliminate the values for a box after getting it's peers
        auxiliar function for eliminate.
    """
    unit_name = box[0] # e.g. A1
    unit_peers = box[1] # e.g. {'A7', 'I1', 'H1', 'A8', 'E1', 'A3', 'B1', 'C2', 'A9', 'B2', 'A2', 'A6', 'C1', 'F1', 'A4', 'A5', 'G1', 'D1', 'C3', 'B3'}
    
    unit_values = values[unit_name]
    if len(unit_values) == 1:
        return unit_values

    # clean set = set of box values - set of the peers values
    clean_set = set(unit_values) - \
        reduce((lambda x,y: x | y),
                filter(lambda x: len(x) == 1,
                    map(lambda x: set(values[x]), unit_peers)))
    return "".join(sorted(clean_set))

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    clean_values = dict(map((lambda x: (x[0], eliminate_box(x, values))),
        peers.items()))
    return clean_values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for box in unit:
            box_val = values[box]
            if len(box_val) == 1:
                continue
            remaining_boxes = set(unit) - set([box])
            remaining_boxes_values = set("".join([values[k] for k in remaining_boxes]))
            diff = set(box_val) - remaining_boxes_values
            if len(diff) == 1:
                values[box] = diff.pop()
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        values = only_choice(values)
        
        # Use the aked twins elimination strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def get_possibilities(values):
    return sorted(list(filter(lambda x: len(x[1]) > 1, values.items())), key=(lambda x: len(x[1])))

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False

    # Choose one of the unfilled squares with the fewest possibilities
    sorted_poss_square = get_possibilities(values)

    # if the max num. of possibilities is 0 the puzzle is solved (for effect of the filter function)
    if not sorted_poss_square: 
        return values

    cell,v = sorted_poss_square[0]
    
    for hypotesys in v:
        new_values = values.copy()
        new_values[cell] = hypotesys
        rec_values = search(new_values)
        if rec_values:
            return rec_values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
