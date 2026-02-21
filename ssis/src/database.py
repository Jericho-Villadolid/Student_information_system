import csv
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
GENDER_OPTIONS = ["M", "F", "O"]

def get_file_path(filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)

def read_data(filename):
    file_path = get_file_path(filename)
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file, skipinitialspace=True)
        return list(reader)

def save_data(filename, headers, data):
    full_path = get_file_path(filename)
    clean_data = []
    for row in data:
        clean_row = {h: row.get(h, '') for h in headers}
        clean_data.append(clean_row)

    with open(full_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(clean_data)

def append_row(filename, headers, new_row_dict):
    data = read_data(filename)
    clean_new = {h: new_row_dict.get(h, '') for h in headers}
    data.append(clean_new)
    save_data(filename, headers, data)

def update_row(filename, pk_value, updated_dict):
    data = read_data(filename)
    if not data:
        return
    id_field = list(updated_dict.keys())[0]
    for i, row in enumerate(data):
        if str(row[id_field]) == str(pk_value):
            row.update(updated_dict)
            data[i] = row
            break
    save_data(filename, list(data[0].keys()), data)

def is_unique(filename, column_name, new_value):
    current_data = read_data(filename)
    normalized_new = str(new_value).strip().lower()
    return not any(
        str(row.get(column_name, "")).strip().lower() == normalized_new
        for row in current_data
    )

def is_valid_student_id(student_id):
    return bool(re.match(r"^\d{4}-\d{4}$", student_id))

def validate_college(college_code):
    if not college_code or college_code.strip() == '':
        return False, "College code cannot be empty."
    if not is_unique('colleges.csv', 'college_code', college_code):
        return False, "This college code already exists."
    return True, "Valid"

def validate_program(program_code, college_code):
    if not is_unique('programs.csv', 'program_code', program_code):
        return False, "This program code already exists."
    if not parent_exists('colleges.csv', 'college_code', college_code):
        return False, f"Error: College '{college_code}' does not exist"
    return True, "Valid"

def validate_student(student_id, gender, program_code):
    if not is_valid_student_id(student_id):
        return False, "Use YYYY-NNNN format."
    if not is_unique('students.csv', 'student_id', student_id):
        return False, "This ID already exists."
    if gender not in GENDER_OPTIONS:
        return False, "Use M, F, or O."
    programs = read_data('programs.csv')
    normalized_program = str(program_code).strip().lower()
    if not any(
        str(p.get('program_code', '')).strip().lower() == normalized_program
        for p in programs
    ):
        return False, f"Program '{program_code}' not found."
    return True, "Valid"

def parent_exists(parent_filename, parent_column, value):
    data = read_data(parent_filename)
    normalized_value = str(value).strip().lower()
    return any(
        str(row.get(parent_column, "")).strip().lower() == normalized_value
        for row in data
    )

def delete_record(filename, pk_column, pk_value):
    data = read_data(filename)
    if not data:
        return
    headers = list(data[0].keys())
    new_data = [row for row in data if str(row[pk_column]) != str(pk_value)]
    save_data(filename, headers, new_data)

def update_college_cascade(old_code, new_code):
    colleges = read_data('colleges.csv')
    for college in colleges:
        if college['college_code'] == old_code:
            college['college_code'] = new_code
            break
    save_data('colleges.csv', ['college_code', 'college_name'], colleges)

    programs = read_data('programs.csv')
    updated = False
    for prog in programs:
        if prog['college_code'] == old_code:
            prog['college_code'] = new_code
            updated = True
    if updated:
        save_data('programs.csv', ['program_code', 'program_name', 'college_code'], programs)

def delete_college_cascade(college_code):
    colleges = read_data('colleges.csv')
    colleges = [c for c in colleges if c['college_code'] != college_code]
    save_data('colleges.csv', ['college_code', 'college_name'], colleges)

    programs = read_data('programs.csv')
    updated = False
    for prog in programs:
        if prog['college_code'] == college_code:
            prog['college_code'] = "N/A"
            updated = True
    if updated:
        save_data('programs.csv', ['program_code', 'program_name', 'college_code'], programs)

def delete_program_cascade(program_code):
    programs = read_data('programs.csv')
    programs = [p for p in programs if p['program_code'] != program_code]
    save_data('programs.csv', ['program_code', 'program_name', 'college_code'], programs)

    students = read_data('students.csv')
    updated = False
    for s in students:
        if s['program_code'] == program_code:
            s['program_code'] = "N/A"
            updated = True
    if updated:
        headers = ['student_id', 'first_name', 'last_name', 'year_level', 'gender', 'program_code']
        save_data('students.csv', headers, students)