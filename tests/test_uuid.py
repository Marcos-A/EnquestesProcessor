#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
import csv
import uuid

SOURCE_FILE_STUDENTS_WITH_MP = 'alumnes-mp.csv'
SOURCE_FILE_STUDENT_ANSWERS = 'respostes.csv'
TMP_ANONYMIZED_STUDENTS_WITH_MP = 'anonymous_alumnes-mp.csv'
TMP_ANONYMIZED_STUDENT_ANSWERS = 'anonymous_respostes.csv'

def replace_student_email_with_random_id():
    email_random_id_dict = {}
    random_id_student_dict = {}

    with open(TMP_ANONYMIZED_STUDENTS_WITH_MP, 'w', encoding='utf-8') as anonymized_alumnes:
        anonymized_alumnes_writer = csv.writer(anonymized_alumnes)
        anonymized_alumnes_writer.writerow(['ID', 'GRUP', 'MP01', 'MP02', 'MP03', 'MP04', 'MP05',
                                     'MP06', 'MP07', 'MP08', 'MP09', 'MP10', 'MP11', 'MP12',
                                     'MP13', 'MP14', 'MP15'])

        with open(SOURCE_FILE_STUDENTS_WITH_MP, 'r', encoding='utf-8') as alumnes:
            alumnes_reader = csv.reader(alumnes)
            next(alumnes, None)

            for alumnes_row in alumnes_reader:
                student_name = alumnes_row[0]
                student_email = alumnes_row[1]
                student_random_id = str(uuid.uuid4())
                #print("-----"+student_random_id)
                email_random_id_dict[student_email] = student_random_id
                random_id_student_dict[student_random_id] = student_name
                anonymized_alumnes_writer.writerow([student_random_id]+alumnes_row[2:])

    with open(TMP_ANONYMIZED_STUDENT_ANSWERS, 'w', encoding='utf-8') as anonymized_respostes:
        anonymized_respostes_writer = csv.writer(anonymized_respostes)

        with open(SOURCE_FILE_STUDENT_ANSWERS, 'r', encoding='utf-8') as respostes:
            respostes_reader = csv.reader(respostes)
            anonymized_respostes_writer.writerow(next(respostes_reader))
            
            for respostes_row in respostes_reader:
                r_email = respostes_row[1]
                r_student_random_id = str(email_random_id_dict.get(r_email))
                #print("====="+r_student_random_id)

                anonymized_respostes_writer.writerow([respostes_row[0]] +
                                                     [r_student_random_id] +
                                                     respostes_row[2:])
        
    return email_random_id_dict, random_id_student_dict

if __name__ == '__main__':
    replace_student_email_with_random_id()

