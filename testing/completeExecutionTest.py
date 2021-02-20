#!/usr/bin/python3.7
# -*- coding: UTF-8 -*-
import csv
import errno
import os
import PyPDF2
import shutil
from core.manager import *
from utilities.terminal import *

"""
Compara els fitxers resultants de l'execució completa del codi amb els generats
per una versió estable anterior i assenyala les diferències, imprimint pel terminal
el nom dels fitxers amb un resultat inesperat i generant el fitxer self.COMPARISON_RESULT_LOG.
"""

class CompleteExecutionTest():

    def __init__(self, testing_settings_dict, testing_settings_yaml_file):
        self.TESTING_SETTINGS_YAML_FILE = testing_settings_yaml_file
        self.TESTING_SETTINGS_DICT = testing_settings_dict

        self.TESTING_FOLDER = self.TESTING_SETTINGS_DICT['TESTING_FOLDER']
        self.STABLE_VERSION_FOLDER = self.TESTING_SETTINGS_DICT['STABLE_VERSION_FOLDER']
        self.BETA_VERSION_FOLDER = self.TESTING_SETTINGS_DICT['BETA_VERSION_FOLDER']
        self.COMPARISON_RESULT_LOG = os.path.join(self.TESTING_FOLDER,
                                                  self.TESTING_SETTINGS_DICT['COMPARISON_RESULT_LOG'])
        self.TMP_TESTING_COMPARISON_FOLDER = self.TESTING_SETTINGS_DICT['TMP_TESTING_COMPARISON_FOLDER']
        self.IGNORED_FILES_LIST = self.TESTING_SETTINGS_DICT['IGNORED_FILES_LIST']

        self.TOP_LEVEL_FOLDER = os.path.join(os.getcwd(), self.TESTING_FOLDER)
        
        self.manager = Manager(self.TESTING_SETTINGS_YAML_FILE)
        self.terminal = Terminal()

        global test_passed

    def scan_versions_folders(self):
        """scan_versions_folders(self)
        Descripció: Cerca el contingut dins de les carpetes self.STABLE_VERSION_FOLDE i 
                    self.BETA_VERSION_FOLDER i l'envia a la funció "scan_folder_content"
                    per continuar el procés.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        dirs_and_files = os.scandir(self.TOP_LEVEL_FOLDER)

        for entry in dirs_and_files:
            if entry.is_dir() is True:
                dir_name = os.path.basename(entry)

                if (dir_name == self.STABLE_VERSION_FOLDER):
                    found_folder = os.path.join(self.TOP_LEVEL_FOLDER, dir_name)
                    stable_folder_dirs_and_files = os.scandir(found_folder)
                    for entry in stable_folder_dirs_and_files:
                        self.scan_folder_content(self.STABLE_VERSION_FOLDER, entry)

                elif (dir_name == self.BETA_VERSION_FOLDER):
                    found_folder = os.path.join(self.TOP_LEVEL_FOLDER, dir_name)
                    beta_folder_dirs_and_files = os.scandir(found_folder)
                    for entry in beta_folder_dirs_and_files:
                        self.scan_folder_content(self.BETA_VERSION_FOLDER, entry)


    def scan_folder_content(self, prefix, entry):
        """scan_folder_content(self, prefix, entry)
        Descripció: Cerca de manera recursiva els fitxers i els envia a la funció "copy_folder_content"
                    per continuar el procés.
        Entrada:    Prefix format per la carpeta de procedència (segons si correspon a la
                    versió estable o beta).
                    Fitxer o carpeta.
        Sortida:    Cap.
        """
        current_dir = os.getcwd()

        if (entry.is_dir() is True):
            dirs_and_files = os.scandir(entry)
            for entry in dirs_and_files:
                self.scan_folder_content(prefix, entry)

        elif (entry.is_file()):
            entry_name = os.path.basename(entry)
            if entry_name in self.IGNORED_FILES_LIST:
                pass
            else:
                self.copy_folder_content(current_dir, prefix, entry)


    def copy_folder_content(self, current_dir, prefix, file_name):
        """copy_folder_content(self, current_dir, prefix, file_name)
        Descripció: Cerca de manera recursiva els fitxers i els envia a la funció "copy_folder_content"
                    per continuar el procés.
        Entrada:    Prefix format per la carpeta de procedència (segons si correspon a la
                    versió estable o beta).
                    Fitxer per ser copiat.
        Sortida:    Cap.
        """
        file_and_extension = os.path.basename(file_name)
        file_base_name, file_extension = self.split_file_base_name_and_extension(file_and_extension)
        new_file_name =  file_base_name + '_' + str(prefix) + '.' + file_extension

        if not os.path.exists(os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER)):
                os.makedirs(os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER))
        shutil.copyfile(os.path.join(os.getcwd(), file_name),
                        os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER, new_file_name))


    def analyze_output_files(self):
        """analyze_output_files(self)
        Descripció: A partir de les versions dels fitxers generades per la versió estable del codi,
                    cerca el seu equivalent generat per la versió beta del codi, detectant possibles
                    absències o arxius sobrants, o invocant les funcions "csv_compare_versions" o
                    "pdf_compare_versions" segons el cas per comparar els continguts dels fitxers.
        Entrada:    Cap
        Sortida:    Cap.
        """
        global test_passed

        testing_folder = os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER)
        files_list = os.scandir(testing_folder)
        self.find_unexpected_generated_files(files_list)

        files_list = os.scandir(testing_folder)
        for current_file in files_list:
            file_name = os.path.basename(current_file)
            if ('_'+self.STABLE_VERSION_FOLDER in file_name):
                stable_file_version = current_file
                original_stable_file_name = file_name.replace('_'+self.STABLE_VERSION_FOLDER, '')

                matched_file = False
                rest_of_files_list = os.scandir(testing_folder)
                for other_file in rest_of_files_list:
                    other_file_name = os.path.basename(other_file)
                    original_beta_file_name = other_file_name.replace('_'+self.BETA_VERSION_FOLDER, '')
                    if (original_stable_file_name == original_beta_file_name):
                        beta_file_version = other_file
                        matched_file = True
                        if (original_stable_file_name.endswith('.csv')):
                            self.csv_compare_versions(stable_file_version, beta_file_version)
                        if (original_stable_file_name.endswith('.pdf')):
                            self.pdf_compare_versions(stable_file_version, beta_file_version)
                        break
                if (matched_file is False):
                    self.announce_unmatched_file_detected(original_stable_file_name)
                    self.record_unmatched_file_error_log([original_stable_file_name] + ['STABLE VERSION'] +\
                                                         ['full file'] + ['BETA EQUIVALENT FILE WAS NOT GENERATED'])
                    test_passed = False


    def csv_compare_versions(self, stable_file_version, beta_file_version):
        """csv_compare_versions(self, stable_file_version, beta_file_version)
        Descripció: Compara el contingut de dos fitxers CSV.
        Entrada:    Versió estable i versió beta d'un mateix fitxer.
        Sortida:    Cap.
        """
        global test_passed

        stable_file_name = os.path.basename(stable_file_version)
        stable_file = os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER, stable_file_name)
        beta_file_name = os.path.basename(beta_file_version)
        beta_file = os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER, beta_file_name)
        
        unmatched_file_content_detected = False
        # Var id_column_position will appear in files with an id to anonymize responses
        # Var id_column_position is randomly generated in each execution, thus ignored in the comparison
        id_column_position = self.find_anonymized_id_column_in_compared_files(stable_file, beta_file)

        with open(stable_file, 'r', encoding='utf-8') as stable:
            stable_reader = stable.readlines()
        with open(beta_file, 'r', encoding='utf-8') as beta:
            beta_reader = beta.readlines()
        
        stable_line = 0
        beta_line = 0
        while stable_line < len(stable_reader) and beta_line < len(beta_reader):
            stable_file_row = stable_reader[stable_line].split(',')
            beta_file_row = beta_reader[beta_line].split(',')
            if id_column_position is None:
                comparison_result = self.are_compared_csv_lines_the_same(stable_file_row, beta_file_row)
            else:
                stable_file_row_without_id_column = stable_file_row[:id_column_position] +\
                                                    stable_file_row[id_column_position+1:]
                beta_file_row_without_id_column = beta_file_row[:id_column_position] +\
                                                  beta_file_row[id_column_position+1:]

                comparison_result = self.are_compared_csv_lines_the_same(stable_file_row_without_id_column,
                                                                     beta_file_row_without_id_column)

                if comparison_result is False and id_column_position is not None:
                    unmatched_stable_file_row_error_log = [stable_file_name] + ['STABLE VERSION'] +\
                                                          ['row ' + str(stable_line)] + [stable_file_row]
                    unmatched_beta_file_row_error_log = [beta_file_name] + ['BETA VERSION'] +\
                                                        ['row ' + str(beta_line)] + [beta_file_row]

                    self.record_unmatched_file_content_error_log(unmatched_stable_file_row_error_log, unmatched_beta_file_row_error_log)
                    if (unmatched_file_content_detected is False):
                        self.annouce_unmatched_file_content_detected(beta_file_name)
                        unmatched_file_content_detected = True
                        test_passed = False
            
            stable_line += 1
            beta_line += 1


    def are_compared_csv_lines_the_same(self, stable_file_row, beta_file_row):
        """are_compared_csv_lines_the_same(self, stable_file_row, beta_file_row)
        Descripció: Compara el contingut de dues línies d'un fitxer CSV per determinar si són iguals.
        Entrada:    Llistat amb una filera de la versió estable d'un fitxer CSV.
                    Llistat amb la mateixa filera de la versió beta del mateix fitxer CSV.
        Sortida:    True o False depenent del resultat de la comparació.
        """
        if stable_file_row == beta_file_row:
            return True
        else:

            return False
    
    def pdf_compare_versions(self, stable_file_version, beta_file_version):
        """pdf_compare_versions(self, stable_file_version, beta_file_version)
        Descripció: Compara el contingut de dos fitxers PDF.
        Entrada:    Versió estable i versió beta d'un mateix fitxer.
        Sortida:    Cap.
        """
        global test_passed

        stable_file_name = os.path.basename(stable_file_version)
        stable_file = os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER, stable_file_name)
        beta_file_name = os.path.basename(beta_file_version)
        beta_file = os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER, beta_file_name)

        stable = open(stable_file, 'rb')
        stable_file_reader = PyPDF2.PdfFileReader(stable)
        beta = open(beta_file, 'rb')
        beta_file_reader = PyPDF2.PdfFileReader(beta)

        stable_file_total_pages = stable_file_reader.getNumPages()
        beta_file_total_pages = beta_file_reader.getNumPages()
        if (stable_file_total_pages != beta_file_total_pages):
            unmatched_stable_string_error_log = [stable_file_name] + ['STABLE VERSION'] +\
                                                ['document structure'] + ['number of pages: ' + str(stable_file_total_pages)]
            unmatched_beta_string_error_log = [beta_file_name] + ['BETA VERSION'] +\
                                              ['document structure'] + ['number of pages: ' + str(beta_file_total_pages)]
            self.record_unmatched_file_content_error_log(unmatched_stable_string_error_log, unmatched_beta_string_error_log)
            self.annouce_unmatched_file_content_detected(beta_file_name)
            test_passed = False

        else:
            page_num = 0
            while page_num < stable_file_total_pages:
                stable_file_page_text = stable_file_reader.getPage(page_num)
                stable_file_page_text_string = stable_file_page_text.extractText()
                beta_file_page_text = beta_file_reader.getPage(page_num)
                beta_file_page_text_string = beta_file_page_text.extractText()

                if (stable_file_page_text_string != beta_file_page_text_string):
                    unmatched_stable_string_error_log = [stable_file_name] + ['STABLE VERSION'] +\
                                                        ['page ' + str(page_num)] + [stable_file_page_text_string]
                    unmatched_beta_string_error_log = [beta_file_name] + ['BETA VERSION'] +\
                                                      ['page ' + str(page_num)] + [beta_file_page_text_string]
                
                    self.record_unmatched_file_content_error_log(unmatched_stable_string_error_log, unmatched_beta_string_error_log)
                    self.annouce_unmatched_file_content_detected(beta_file_name)
                    test_passed = False
                    break
                page_num += 1
    

    def find_anonymized_id_column_in_compared_files(self, stable_file, beta_file):
        """find_anonymized_id_column_in_compared_files(self, stable_file, beta_file)
        Descripció: Troba la posició de la columna "ID" d'un fitxer, la qual conté un identificador aleatori
                    que es genera en cada execució i que mai coincidirà durant la comparació.
        Entrada:    Versió estable i versió beta d'un mateix fitxer.
        Sortida:    Posició de la columna amb els "ID" aleatoris o None en cas que no existeixi aquesta.
        """
        with open(stable_file, 'r', encoding='utf-8') as stable:
            stable_reader = csv.reader(stable)
            stable_header = next(stable_reader)

        with open(beta_file, 'r', encoding='utf-8') as beta:
            beta_reader = csv.reader(beta)
            beta_header = next(beta_reader)

        if ('ID' in stable_header and 'ID' in beta_header):
            return stable_header.index('ID')
        else:
            return None


    def find_unexpected_generated_files(self, files_list):
        """find_unexpected_generated_files(self, files_list)
        Descripció: Cerca fitxers sobrants generats per la versió beta del codi que no existeixin a la versió
                    estable del mateix.
        Entrada:    Llistat d'entrada amb els fitxers de la versió estable i de la versió beta.
        Sortida:    Cap.
        """
        global test_passed
        stable_version_files_list = []
        beta_version_files_list = []

        for file in files_list:
            file_name = os.path.basename(file)    
            if ('_'+self.STABLE_VERSION_FOLDER in file_name):
                original_stable_file_name = file_name.replace('_'+self.STABLE_VERSION_FOLDER, '')
                stable_version_files_list.append(original_stable_file_name)
            if ('_'+self.BETA_VERSION_FOLDER in file_name):
                original_beta_file_name = file_name.replace('_'+self.BETA_VERSION_FOLDER, '')
                beta_version_files_list.append(original_beta_file_name)

        unexpected_generated_files = list(set(beta_version_files_list) - set(stable_version_files_list))
        for unexpected_file in unexpected_generated_files:
            unexpected_file
            self.announce_unexpected_file_detected(unexpected_file)
            self.record_unexpected_file_error_log([unexpected_file] + ['BETA VERSION'] +\
                                                        ['full file'] + ['BETA FOUND FILE WAS NOT EXPECTED'])
            test_passed = False


    def generate_error_log_file(self):
        """generate_error_log_file(self)
        Descripció: Genera el fitxer CSV self.COMPARISON_RESULT_LOG on es registraran les errades
                    trobades durant el text d'execució completa del codi, i escriu la capçalera
                    de l'arxiu.
        Entrada:    Cap.
        Sortida:    Cap. Genera l'arxiu self.COMPARISON_RESULT_LOG.
        """
        with open(self.COMPARISON_RESULT_LOG, 'w', encoding='utf-8') as error_log_file:
            error_log_header_writer = csv.writer(error_log_file)
            error_log_header_writer.writerow(['FILE', 'VERSION', 'POSITION', 'RESULT'])


    def record_unmatched_file_error_log(self, stable_missing_file_record):
        """record_unmatched_file_error_log(self, stable_missing_file_record)
        Descripció: Registra al fitxer CSV self.COMPARISON_RESULT_LOG que s'ha detectat un fitxer
                    de menys com a resultat de l'execució del nou codi.
        Entrada:    Llista amb la informació relativa al fitxer faltant.
        Sortida:    Cap. Registra self.COMPARISON_RESULT_LOG la informació del fitxer faltant.
        """
        if not os.path.isfile(self.COMPARISON_RESULT_LOG):
            self.generate_error_log_file()
        
        with open(self.COMPARISON_RESULT_LOG, 'a', encoding='utf-8') as error_log:
            error_log_writer = csv.writer(error_log)
            error_log_writer.writerow(stable_missing_file_record)
            error_log_writer.writerow([''])


    def record_unexpected_file_error_log(self, beta_surplus_file_record):
        """record_unexpected_file_error_log(self, beta_surplus_file_record)
        Descripció: Registra al fitxer CSV self.COMPARISON_RESULT_LOG que s'ha detectat un fitxer
                    de més com a resultat de l'execució del nou codi.
        Entrada:    Llista amb la informació relativa al fitxer faltant.
        Sortida:    Cap. Registra self.COMPARISON_RESULT_LOG la informació del fitxer sobrant.
        """
        if not os.path.isfile(self.COMPARISON_RESULT_LOG):
            self.generate_error_log_file()
        
        with open(self.COMPARISON_RESULT_LOG, 'a', encoding='utf-8') as error_log:
            error_log_writer = csv.writer(error_log)
            error_log_writer.writerow(beta_surpluss_file_record)
            error_log_writer.writerow([''])


    def record_unmatched_file_content_error_log(self, stable_record, beta_record):
        """record_unmatched_file_content_error_log(self, stable_record, beta_record)
        Descripció: Registra al fitxer CSV self.COMPARISON_RESULT_LOG la diferència trobada
                    en un arxiu com a resultat de l'execució del codi complet.
        Entrada:    Llista amb la informació esperada al fitxer de la versió estable.
                    Llista amb la informació esperada al fitxer de la versió beta.
        Sortida:    Cap. Registra self.COMPARISON_RESULT_LOG la informació esperada d'acord amb
                    la versió estable del codi, i la informació rebuda com a resultat de l'execució
                    de la versió beta del codi.
        """
        if not os.path.isfile(self.COMPARISON_RESULT_LOG):
            self.generate_error_log_file()
        
        with open(self.COMPARISON_RESULT_LOG, 'a', encoding='utf-8') as error_log:
            error_log_writer = csv.writer(error_log)
            error_log_writer.writerow(stable_record)
            error_log_writer.writerow(beta_record)
            error_log_writer.writerow([''])


    def announce_unexpected_file_detected(self, file_name):
        """announce_unexpected_file_detected(self, file_name)
        Descripció: Imprimeix pel terminal l'avís de què s'ha detectat un fitxer de més com a resultat
                    de l'execució del nou codi.
        Entrada:    Nom de l'arxiu.
        Sortida:    Cap. Imprimeix pel terminal el nom de l'arxiu inesperat.
        """
        global test_passed
        if (test_passed is True):
            self.terminal.breakline()

        self.terminal.tab()
        self.terminal.writeln("El nou codi ha generat el fitxer inesperat " + file_name, TerminalColors.DARKRED)
        self.terminal.untab()


    def announce_unmatched_file_detected(self, file_name):
        """announce_unmatched_file_detected(self, file_name)
        Descripció: Imprimeix pel terminal l'avís de què s'ha detectat un fitxer de menys com a resultat
                    de l'execució del nou codi.
        Entrada:    Nom de l'arxiu.
        Sortida:    Cap. Imprimeix pel terminal el nom de l'arxiu faltant.
        """
        global test_passed
        if (test_passed is True):
            self.terminal.breakline()

        self.terminal.tab()
        self.terminal.writeln("El nou codi no ha generat el fitxer " + file_name, TerminalColors.DARKRED)
        self.terminal.untab()


    def annouce_unmatched_file_content_detected(self, file_name):
        """annouce_unmatched_file_content_detected(self, file_name)
        Descripció: Imprimeix pel terminal l'avís de què s'ha detectat un fitxer del contingut del qual
                    no coincideix amb l'esperat.
        Entrada:    Nom de l'arxiu.
        Sortida:    Cap. Imprimeix pel terminal el nom de l'arxiu on es troba el conflicte.
        """
        global test_passed
        if (test_passed is True):
            self.terminal.breakline()

        self.terminal.tab()
        self.terminal.writeln("Error detectat al fitxer " + file_name, TerminalColors.DARKRED)
        self.terminal.untab()


    def split_file_base_name_and_extension(self, file_name):
        """split_file_base_name_and_extension(self, file_name)
        Descripció: Donat el nom d'un arxiu separa el seu nom base de la seva extensió.
        Entrada:    Nom de l'arxiu.
        Sortida:    Nom base de l'arxiu (sense l'extensió ni el punt intermedi).
                    Extensió (sense el punt previ).
        """
        extension_position = file_name.count('.')
        file_base_name = file_name[:-len(file_name.split('.')[extension_position])-1]
        file_extension = file_name.split('.')[extension_position]
        
        return file_base_name, file_extension


    def succeed(self):
        """succeed(self)
        Descripció: Imprimeix un missatge d'"OK" pel terminal.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        self.terminal.writeln("OK", TerminalColors.DARKGREEN)


    def catch_exception(self, ex):    
        self.error(str(ex))    
        sys.exit()


    def file_and_dir_remover(self, file_or_dir):
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


    def remove_execution_result_and_tmp_files(self):
        """remove_execution_result_and_tmp_files(self)
        Descripció: Elimina els directoris self.TMP_TESTING_COMPARISON_FOLDER i self.BETA_VERSION_FOLDER
                    amb els seus continguts.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        shutil.rmtree(os.path.join(self.TOP_LEVEL_FOLDER, self.TMP_TESTING_COMPARISON_FOLDER))
        shutil.rmtree(os.path.join(self.TOP_LEVEL_FOLDER, self.BETA_VERSION_FOLDER))


    def run_complete_execution_test(self):
        """remove_execution_result_and_tmp_files(self)
        Descripció: Executa la seqüència de test dels resultats complets d'execució del codi.
        Entrada:    Cap.
        Sortida:    Cap. Impremeix pel terminal els resultats de l'execució.
        """
        global test_passed
        test_passed = True

        try:
            self.terminal.breakline()
            self.terminal.writeln("----------------------------------------------------------------------")
            self.terminal.writeln("----------------------------------------------------------------------")
            self.terminal.writeln("Iniciant el test d'execució del codi complet...",
                                  TerminalColors.BLACKONYELLOWBACKGROUND)

            self.file_and_dir_remover(self.COMPARISON_RESULT_LOG)

            self.terminal.breakline()
            self.terminal.writeln("Executant el nou codi:",
                        TerminalColors.YELLOW)
            self.manager.run_worker()
        except Exception as ex:
            self.catch_exception(ex)
        
        try:
            self.terminal.write("Analitzant el resultat de l'execució... ",
                                TerminalColors.YELLOW)
            self.scan_versions_folders()
            self.analyze_output_files()
            if (test_passed is True):
                self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        try:
            if (test_passed is False):
                self.terminal.breakline()
            self.terminal.write("Eliminant fitxers temporals... ",
                        TerminalColors.YELLOW)
            self.remove_execution_result_and_tmp_files()
            self.succeed()
            self.terminal.breakline()
        except Exception as ex:
            self.catch_exception(ex)

        if (test_passed is False):
            self.terminal.writeln("ELS RESULTATS DEL NOU CODI NO HAN SUPERAT EL TEST",
                        TerminalColors.REDBACKGROUND)
        else:
            self.terminal.writeln("TEST D'EXECUCIÓ COMPLETA DEL CODI SUPERAT AMB ÈXIT",
                TerminalColors.BLACKONGREENBACKGROUND)
        self.terminal.breakline()
