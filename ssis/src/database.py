import csv
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
GENDER_OPTIONS = ["M", "F", "O"]

def get_file_path(filename):
    return os.path.join(DATA_DIR,filename)

def read_data(filename):
    file_path = get_file_path(filename)
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file, skipinitialspace=True)
        return list(reader)

def save_data(filename,fieldnames,data_list):
    file_path = get_file_path(filename)
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader
        writer.writerows(data_list)

def append_row(filename,fieldnames,row_dict):
    file_path = get_file_path(filename)
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)
        

def is_unique(filename,column_name,new_value):
    current_data = read_data(filename)
    return not any(row.get(column_name) == str(new_value) for row in current_data)

def is_valid_student_id(student_id):
    return bool(re.match(r"^\d{4}-\d{4}$", student_id))

def validate_college(college_code):
    if not college_code or college_code.strip()==' ':
        return False, "College code cannot be empty."
    if not is_unique('colleges.csv','college_code', college_code):
        return False, "This college code already exists."
    return True, "Valid"

def validate_program(program_code, college_code):
    if not is_unique('programs.csv', 'program_code', program_code):
        return False, "This program already exists."
    if not parent_exists('colleges.csv', 'college_code', college_code):
        return False, f"Error: College '{college_code}' does not exist"
    return True, "Valid"

def validate_student(student_id,gender,program_code):
    if not is_valid_student_id(student_id): return False, "Use YYYY-NNNN format."
    if not is_unique('students.csv', 'student_id', student_id): return False, "This ID already exists."
    if gender not in GENDER_OPTIONS: return False, "Use M, F, or O."
    if not any(row['program_code']== program_code for row in read_data('programs.csv')):
        return False, f"Program {program_code} not found."
    return True, "Valid"