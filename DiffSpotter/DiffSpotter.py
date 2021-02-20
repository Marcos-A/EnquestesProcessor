#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

import csv
import errno
import os
import shutil

STABLE_VERSION_FOLDER = 'v2'
BETA_VERSION_FOLDER = 'v3'
COMPARISON_RESULT_LOG = 'comparison_result.csv'
TESTING_FOLDER = 'testing'
IGNORED_FILES_LIST = ['.DS_Store']

def scan_versions_folders(top_level_folder):
    dirs_and_files = os.scandir(top_level_folder)

    for entry in dirs_and_files:
        if entry.is_dir() is True:
            dir_name = os.path.basename(entry)

            if (dir_name == STABLE_VERSION_FOLDER):
                current_dir = os.getcwd()
                found_folder = os.path.join(current_dir, dir_name)
                stable_folder_dirs_and_files = os.scandir(found_folder)
                for entry in stable_folder_dirs_and_files:
                    scan_folder_content(top_level_folder,
                                     STABLE_VERSION_FOLDER,
                                     entry)

            elif (dir_name == BETA_VERSION_FOLDER):
                current_dir = os.getcwd()
                found_folder = os.path.join(current_dir, dir_name)
                beta_folder_dirs_and_files = os.scandir(found_folder)
                for entry in beta_folder_dirs_and_files:
                    scan_folder_content(top_level_folder,
                                     BETA_VERSION_FOLDER,
                                     entry)


def scan_folder_content(top_level_folder, prefix, entry):
    current_dir = os.getcwd()

    if (entry.is_dir() is True):
        dirs_and_files = os.scandir(entry)
        for entry in dirs_and_files:
            scan_folder_content(top_level_folder, prefix, entry)

    elif (entry.is_file()):
        entry_name = os.path.basename(entry)
        if entry_name in IGNORED_FILES_LIST:
            pass
        else:
            copy_folder_content(top_level_folder, current_dir, prefix, entry)


def copy_folder_content(top_level_folder, current_dir, prefix, file):
    file_and_extension = os.path.basename(file)
    file_name = file_and_extension.split('.')[0]
    file_extension = file_and_extension.split('.')[1]
    new_file_name =  file_name + '_' + str(prefix) + '.' + file_extension

    #print("RESULT: " + os.path.join(top_level_folder, TESTING_FOLDER, new_file_name))
    if not os.path.exists(os.path.join(top_level_folder, TESTING_FOLDER)):
            os.makedirs(os.path.join(top_level_folder, TESTING_FOLDER))
    shutil.copyfile(os.path.join(os.getcwd(), file),
                    os.path.join(top_level_folder, TESTING_FOLDER, new_file_name))


def analyze_output_files(top_level_folder):
    testing_folder = os.path.join(top_level_folder, TESTING_FOLDER)

    files_list = os.scandir(testing_folder)

    for file in files_list:
        file_name = os.path.basename(file)
        if ('_'+STABLE_VERSION_FOLDER in file_name):
            stable_file_version = file
            original_stable_file_name = file_name.replace('_'+STABLE_VERSION_FOLDER, '')

            rest_of_files_list = os.scandir(testing_folder)
            for other_file in rest_of_files_list:
                other_file_name = os.path.basename(other_file)
                original_beta_file_name = other_file_name.replace('_'+BETA_VERSION_FOLDER, '')
                if (original_stable_file_name == original_beta_file_name):
                    beta_file_version = other_file

                    compare_versions(stable_file_version, beta_file_version)


def compare_versions(stable_file_version, beta_file_version):
    stable_file_name = os.path.basename(stable_file_version)
    stable_file = os.path.join(top_level_folder, TESTING_FOLDER, stable_file_name)
    beta_file_name = os.path.basename(beta_file_version)
    beta_file = os.path.join(top_level_folder, TESTING_FOLDER, beta_file_name)

    with open(stable_file, 'r', encoding='utf-8') as stable:
        stable_reader = stable.readlines()

    with open(beta_file, 'r', encoding='utf-8') as beta:
        beta_reader = beta.readlines()

    stable_line = 0
    beta_line = 0

    with open(COMPARISON_RESULT_LOG, 'a', encoding='utf-8') as comparison_result_log:
        comparison_result_log_writer = csv.writer(comparison_result_log)

        while stable_line < len(stable_reader) and beta_line < len(beta_reader):
            if stable_reader[stable_line] != beta_reader[beta_line]:
                comparison_result_log_writer.writerow([stable_file_name] + 
                                                      ['STABLE VERSION'] + 
                                                      ['row ' + str(stable_line)] +  
                                                      [stable_reader[stable_line]])
                comparison_result_log_writer.writerow([beta_file_name] + 
                                                      ['BETA VERSION'] +
                                                      ['row ' + str(beta_line)] + 
                                                      [beta_reader[beta_line]])
                comparison_result_log_writer.writerow(['']) 

            stable_line += 1
            beta_line += 1


def file_and_dir_remover(file_or_dir):
    """def file_and_dir_remover(file_or_dir)
    Descripció: Elimina fitxers i directoris sempre que existeixin i estiguin
                buits.
    Entrada:    Nom del fitxer o directori.
    Sortida:    Eliminació de fixter o directori.
    """
    try:
        os.remove(file_or_dir)
    except OSError as e:
        """
        Descarta els errors per fitxer o directori no existent, o directori no
        buit.
        """
        if e.errno != errno.ENOENT and e.errno != errno.ENOTEMPTY:
            raise


if __name__ == '__main__':
    file_and_dir_remover(COMPARISON_RESULT_LOG)

    top_level_folder = os.getcwd()

    scan_versions_folders(top_level_folder)

    analyze_output_files(top_level_folder)
