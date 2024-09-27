### Import Packages
import sys
import pandas as pd

### Extract diff signs from pre and post review code
def extract_diffs(example):
    old_diffs = set()
    for row in example.old.split("\n"):
        if len(row) > 0:
            if row[0] != " ":
                old_diffs.add(row[0])

    new_diffs = set()
    for row in example.new.split("\n"):
        if len(row) > 0:
            if row[0] != " ":
                new_diffs.add(row[0])
    return old_diffs, new_diffs

### Extract ground truth change type
def extract_change_type(example):
    old_diffs, new_diffs = extract_diffs(example)
    
    if old_diffs == set("-") and new_diffs == set():
        change_type = "remove_only"
    elif old_diffs == set() and new_diffs == set("+"):
        change_type = "add_only"
    elif old_diffs == set("-") and new_diffs == set("+"):
        change_type = "modify"
    return change_type

### Extract wrong change types
def get_wrong_answers(example):
    correct_answer = example.correct_answer
    wrong_answers = set(["remove_only", "add_only", "modify"])
    wrong_answers.remove(correct_answer)
    return wrong_answers

### Construct change type MCQA dataset
def construct_mcqa_change_type(data):
    examples = data[['old','new','review']]
    examples['correct_answer'] = examples.apply(lambda row: extract_change_type(row), axis=1)
    examples['wrong_answer'] = examples.apply(lambda row: get_wrong_answers(row), axis=1)
    return examples

### Main Function
def main():
    data_dir = "../data/" + sys.argv[1] 
    output_dir = "../mcqa_sets/" + sys.argv[2] 
    data = pd.read_json(data_dir, lines=True)
    change_type_mcqa = construct_mcqa_change_type(data)
    change_type_mcqa.to_json(output_dir,orient='records', lines=True)
    print("### Change Type MCQA Constructed for ", sys.argv[1], "###")
    return

if __name__ == "__main__":
    main()