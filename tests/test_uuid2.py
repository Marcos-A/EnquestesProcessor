#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
import csv
import uuid

SOURCE_FILE_STUDENTS_WITH_MP = 'alumnes-mp.csv'
SOURCE_FILE_STUDENT_ANSWERS = 'respostes.csv'
TMP_ANONYMIZED_STUDENTS_WITH_MP = 'anonymous_alumnes-mp.csv'
TMP_ANONYMIZED_STUDENT_ANSWERS = 'anonymous_respostes.csv'

def replace_student_email_with_random_id(student_email, student_name, email_to_id_dict, id_to_email_and_name_dict):
    """def replace_student_email_with_random_id(student_email, student_name,
                                                email_to_id_dict, id_to_email_and_name_dict)
    Descripció: Reemplaça l'email de l'estudiant amb un ID aleatori únic, i actualitza el diccionari amb
                l'email dels estudiants com a clau i la seva respectiva id com a valor, i el diccionari
                amb les id dels estudiants com a clau i una tupla l'email i nom respectius com com a valor.
    Entrada:    Email, nom, diccionari amb l'email dels estudiants com a clau i la seva respectiva id
                com a valor, diccionari amb les id dels estudiants com a clau i una tupla l'email i nom
                respectius com com a valor.
    Sortida:    Diccionari amb l'email dels estudiants com a clau i la seva respectiva id
                com a valor, i diccionari amb les id dels estudiants com a clau i una tupla l'email i nom
                respectius com com a valor, tots dos actualitzats amb les dades de l'estudiant passat com
                a paràmetre.
    """
    student_id = uuid.uuid4()

    email_to_id_dict[student_email] = student_id
    id_to_email_and_name_dict[student_id] = [student_email, student_name]

    return email_to_id_dict, id_to_email_and_name_dict


def anonymize_answers():
    """anonymize_answers()
    Descripció: Reemplaça l'email de l'estudiant amb un ID aleatori únic
    Entrada:    Cap.
    Sortida:    Diccionari amb l'email dels estudiants com a clau i la seva respectiva id
                com a valor, i diccionari amb les id dels estudiants com a clau i una tupla l'email i nom
                respectius com com a valor, tots dos actualitzats amb les dades de l'estudiant passat com
                a paràmetre.
    """
    email_to_id_dict = {}
    id_to_email_and_name_dict = {}

    with open(SOURCE_FILE_STUDENTS_WITH_MP, 'r', encoding='utf-8') as alumnes:
        alumnes_reader = csv.reader(alumnes)
        next(alumnes, None)

        for alumnes_row in alumnes_reader:
            student_name = alumnes_row[0]
            student_email = alumnes_row[1]
            email_to_id_dict, id_to_email_and_name_dict = replace_student_email_with_random_id(
                                                    student_email, student_name,
                                                    email_to_id_dict, id_to_email_and_name_dict)

    with open(TMP_ANONYMIZED_STUDENT_ANSWERS, 'w', encoding='utf-8') as anonymized_respostes:
        anonymized_respostes_writer = csv.writer(anonymized_respostes)

        with open(SOURCE_FILE_STUDENT_ANSWERS, 'r', encoding='utf-8') as respostes:
            respostes_reader = csv.reader(respostes)
            anonymized_respostes_writer.writerow(next(respostes_reader))
            
            for respostes_row in respostes_reader:
                r_email = respostes_row[1]
                if (r_email not in email_to_id_dict):
                    email_to_id_dict, id_to_email_and_name_dict = replace_student_email_with_random_id(
                                                            r_email, 'desconegut',
                                                            email_to_id_dict, id_to_email_and_name_dict)
                r_student_random_id = str(email_to_id_dict.get(r_email))

                anonymized_respostes_writer.writerow([respostes_row[0]] +
                                                     [r_student_random_id] +
                                                     respostes_row[2:])
        
    return email_to_id_dict, email_to_id_dict


if __name__ == '__main__':
    email_to_id_dict, id_to_email_and_name_dict = anonymize_answers()
