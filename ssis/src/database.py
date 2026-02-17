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
    data = []
    try:
        with open(file_path, mode='r', newline=' ', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    return data

def save_data(filename,fieldnames,data_list):
    file_path = get_file_path(filename)
    with open(file_path, mode='w', newline=' ', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader
        writer.writerows(data_list)

def append_row(filename,fieldnames,row_dict):
    file_path = get_file_path(filename)
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='w', newline=' ', encoding='utf-8') as file:\
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
        writer.writerow(row_dict)
        

def is_unique(filename,column_name,new_value):
    current_data = read_data(filename)
    for row in current_data:
        if row[column_name] == str(new_value):
            return False
    return True

def is_valid_student_id(student_id):
    pattern = r"^\d{4}$"
    return bool(re.match(pattern, student_id))

def is_valid_gender(gender):
    return gender in GENDER_OPTIONS

def does_code_exist(filename, code_column, code_to_check):
    data = read_data(filename)
    return any(row[code_column] == code_to_check for row in data)

def parent_exists(parent_filename, parent_column, value):
    data = read_data(parent_filename)
    return any(row[parent_column].strip() == str(value).strip for row in data)

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
    if not is_unique('students.csv', 'student_id', student_id):
        return False, "Error: Student ID already exists."
    if not is_valid_student_id(student_id):
        return False, "Error: ID must be in XXXX-XXXX format."
    if not is_valid_gender(gender):
        return False, "Error: Invalid gender submitted."
    if not does_code_exist('programs.csv', 'program_code', program_code):
        return False, f"Error: Program '{program_code}' does not exist."
    
    return True, "Success"