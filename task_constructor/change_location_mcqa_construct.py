### Import Packages
import sys
import pandas as pd
import itertools
import warnings
import math
warnings.filterwarnings("ignore")

### Extract ground truth changed lines for {delete_only/modify}, and remaining options set
def extract_changed_lines_del_mod(example):
    example = example.old.split("\n")
    gt = set()

    for row_no in range(len(example)):
        line = example[row_no]

        if len(example[row_no]) != 0:
            if line[0] == "-":
                gt.add(row_no + 1)

    options = set(range(1,len(example)+1))
    return gt, options

### Extract ground truth changed lines for {add_only}, and remaining options set
def extract_changed_lines_add(example):
    example = example.new.split("\n")
    location_old = 0
    options = set()
    options.add(0)
    gt = set()
    for row_no in range(len(example)):
        if len(example[row_no]) != 0:
            if example[row_no][0] == "+":
                gt.add(location_old)
                continue

        location_old += 1
        options.add(location_old)
    return gt, options

# Extract ground truth changed lines general function 
def extract_changed_lines(example):
    if example.type_correct == "add_only":
        return extract_changed_lines_add(example)
    else:
        return extract_changed_lines_del_mod(example)

### Calculate minimum possible jaccard similarity 
def min_jaccard_similarity_multiple_sets(pool_size, set_size, num_sets):
    total_required_elements = num_sets * set_size
    
    # When the sets can be fully disjoint
    if total_required_elements <= pool_size:
        return 0  # Minimum similarity is 0 when sets are disjoint

    # Calculate overlap if the pool is too small to form disjoint sets
    overlap = total_required_elements - pool_size
    max_intersection_per_pair = max(1, math.ceil(overlap/num_sets))  # Distribute overlap across pairs
    union_per_pair = 2 * set_size - max_intersection_per_pair

    # Jaccard similarity for each pair of sets
    return max_intersection_per_pair / union_per_pair

### Calculate jaccard similarity
def jaccard_similarity(set1, set2):
    # Calculate intersection and union
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    # Calculate Jaccard similarity
    return intersection / union if union != 0 else 0

### Calculate all possible combinations given the set size and lines available
def compute_combinations(pool, n):
    return list(itertools.combinations(pool, n))

### Retrieve negative answers (easy: lowest jaccard similarity possible)
def retrieve_answers_easy(gt, options):

    # Get lowest jaccard similarity
    lowest_jsim = min_jaccard_similarity_multiple_sets(len(options), len(gt), 4)

    # Get all candidate answers
    possible_answers = compute_combinations(options,len(gt))
    answer_set = [] # Storing viable answers

    # Consider through all candidate answers
    for answer in possible_answers:
        # Stop at three selected answers
        if len(answer_set) >= 3:
            break

        answer = set(answer)
        # Candidate answer must not already have been selected
        if (answer != gt) and (answer not in answer_set):
            lowest_jsim_flag = True

            # Jaccard similarity should be the lowest possible against each of the existing answers
            if jaccard_similarity(answer, gt) > lowest_jsim:
                lowest_jsim_flag = False
                
            for existing_answer in answer_set:
                if jaccard_similarity(answer, existing_answer) > lowest_jsim:
                    lowest_jsim_flag = False

            # Found a viable answer
            if lowest_jsim_flag == True:
                answer_set.append(answer)
    return answer_set

### Retrieve negative answers (hard: highest jaccard similarity possible)
def retrieve_answers_hard(gt, options):

    # Get highest jaccard similarity
    highest_jsim = (len(gt) - 1)/(len(gt) + 1)

    # Get all candidate answers
    possible_answers = compute_combinations(options,len(gt))
    answer_set = [] # Storing viable answers

    # Consider through all candidate answers
    for answer in possible_answers:
        # Stop at three selected answers
        if len(answer_set) >= 3:
            break
        
        answer = set(answer)
        # Candidate answer must not already have been selected
        if (answer != gt) and (answer not in answer_set):
            # Jaccard similarity should be the highest possible with the correct answer
            if jaccard_similarity(answer, gt) == highest_jsim:
                answer_set.append(answer)
    return answer_set

### Main Function
def main():
    data_dir = "../mcqa_sets/" + sys.argv[1] 
    output_dir = "../mcqa_sets/" + sys.argv[2] 
    data = pd.read_json(data_dir, lines=True)

    gt_all = []
    answers_easy_all = []
    answers_hard_all = []
    for row_no in range(len(data)):
        example = data.iloc[row_no]
        gt, options = extract_changed_lines(example)
        answers_easy = retrieve_answers_easy(gt, options)
        answers_hard = retrieve_answers_hard(gt, options)
        gt_all.append(gt)
        answers_easy_all.append(answers_easy)
        answers_hard_all.append(answers_hard)
    
    data['loc_correct'] = gt_all
    data['loc_wrong_easy'] = answers_easy_all
    data['loc_wrong_hard'] = answers_hard_all
    data.to_json(output_dir,orient='records', lines=True)
    print("### Change Localisation MCQA Constructed for {0} ###".format(sys.argv[1]))
    return

if __name__ == "__main__":
    main()
    