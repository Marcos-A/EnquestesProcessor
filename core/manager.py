#!/usr/bin/python3.7
# -*- coding: UTF-8 -*-
from utilities.terminal import *
from core.worker import *
import sys
import os
import yaml


"""EnquestesProcessor_3.0: 
Fitxers d'entrada:
    - alumnes-mp.csv: llista dels alumnes matriculats a cada CF,
                    amb el seu nom complet, l'adreça Xeill, el cicle i curs,
                    i una «x» per cada MP al qual estigui matriculat
    - respostes.csv: descarregat des del formulari d'avaluació de Google Drive,
                    conté les valoracions dels alumnes
Fitxers de sortida:
    - finals:
        * estadistica_respostes.csv: conté la mitjana de les respostes per ítem
                                    objecte avaluat i grup
        * resultats_respostes.csv: conté les respostes per ser traspassades al
                                full de càlcul final
        * resultats_errades.csv: conté les respostes filtrades
        * resultats_alumnes-respostes.csv: conté quins objectes han estat
                                        avaluats per cada alumne
    - registres (opcionalment eliminables):
        * errades_rec.csv: conté les errades filtrades amb l'avaluació completa
                        feta per l'estudiant
        * resultats_rec.csv: conté les respostes filtrades amb l'avaluació
                            completa feta per l'estudiant
    - temporals (opcionalment eliminables):
        * resultats_tmp.csv: conté les respostes vàlides amb la identificació
                            de l'estudiant

Novetats respecte a la versió 2.4:
    - refactorització completa del codi
    - incorporació d'un sistema de tests unitaris
"""


class Manager(): 

    def __init__(self, settings_yaml_file='settings.yaml'):
        self.settings_yaml_file = settings_yaml_file
        
        self.SETTINGS_DICT = yaml.safe_load(open(self.settings_yaml_file))
        self.LOG_LEVEL= self.SETTINGS_DICT['LOG_LEVEL']

        self.terminal = Terminal()  
        self.worker = Worker(self.SETTINGS_DICT)

    def setup_options():
        """
        Descripció: Demana a l'usuari que definieixi les opcions no establertes.
        Entrada:    Cap.
        Sortida:    Defineix les variables globals OPTION_TMP_FILES,
                    OPTION_TMP_RECORDS, OPTION_DUPLICATED_ANSWERS en el seu cas.
        """
        
        while worker.OPTION_TMP_FILES != 0 and worker.OPTION_TMP_FILES != 1:        
            self.terminal.writeln("Voleu conservar els arxius temporals? (s/n) ")
            worker.OPTION_TMP_FILES = answer_from_string_to_binary(input().lower())

        while worker.OPTION_TMP_RECORDS != 0 and worker.OPTION_TMP_RECORDS != 1:
            self.terminal.writeln("Voleu conservar els registres? (s/n) ")
            worker.OPTION_TMP_RECORDS = answer_from_string_to_binary(input().lower())

        while worker.OPTION_DUPLICATED_ANSWERS != 0 and worker.OPTION_DUPLICATED_ANSWERS != 1:
            self.terminal.writeln("En cas de respostes duplicades, quina voleu conservar? (1: la primera, 2: l'última) ")
            worker.OPTION_DUPLICATED_ANSWERS = answer_from_string_to_binary(input().lower())

        while worker.OPTION_REPORTS != 0 and worker.OPTION_REPORTS != 1:
            self.terminal.writeln("Desitja generar els informes? (s/n) ")
            worker.OPTION_REPORTS = answer_from_string_to_binary(input().lower())


    def answer_from_string_to_binary(text):
        """
        Descripció: Converteix una string amb una 's'/'y' o amb una 'n' en un int 0 o 1 respectivament.
        Entrada:    string
        Sortida:    int
        Exemple:    'n' retorna 1
        """
        return 1 if text == 'y' or text == 's' or text == '2' else 0    


    def offer_navigation_menu_for_troublesome_source_files(source_file):
        """
        Descripció: Ofereix a l'usuari l'opció de solucionar un problema amb els
                    fitxers d'entrada i continuar amb l'execució del programa, o bé
                    interrompre'l.
        Entrada:    String amb el nom del fitxer d'entrada.
        Sortida:    Executa una determinada funció segons l'opció triada.
        """    
        self.terminal.tab()
        self.terminal.breakline()
        self.terminal.writeln("Què voleu fer? Trieu una opció:", TerminalColors.UNDERLINE)

        self.terminal.tab()
        self.terminal.write("1. ", TerminalColors.CYAN)
        self.terminal.writeln("Solucionar el problema i seguir.")
        self.terminal.write("2. ", TerminalColors.CYAN)
        self.terminal.writeln("Voleu sortir del programa")
        self.terminal.untab()

        option = input()
        if option == "1":
            self.terminal.writeln("Si us plau, assegureu-vos de què heu solucionat el problema i premeu «Enter».")
            self.terminal.untab()

            input()
            if self.LOG_LEVEL> 0: terminal.write("Reintentant... ")
            check_source_file(source_file)

        elif option == "2":
            self.terminal.untab()
            exit()

        else:
            self.terminal.writeln("Si us plau, assegureu-vos de què heu solucionat una opció vàlida.")
            self.terminal.untab()
            offer_navigation_menu_for_troublesome_source_files(source_file)


    def check_source_file(self, source_file):
        """
        Descripció: Comprova que el fitxer d'entrada existeix i no està buit.
        Entrada:    String amb el nom del fitxer d'entrada.
        Sortida:    Cap o crida a la funció
        """
        if not os.path.exists(source_file):
            error("No s'ha trobat a la carpeta el fitxer «%s»." % source_file)        
            offer_navigation_menu_for_troublesome_source_files(source_file)

        if os.path.getsize(source_file) == 0:
            print("\nEl fitxer «%s» està buit." % source_file)
            offer_navigation_menu_for_troublesome_source_files(source_file)


    def catch_exception(self, ex):    
        self.error(str(ex))    
        sys.exit()


    def succeed(self):
        """
        Descripció: Imprimeix un missatge d'"OK" pel terminal.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        if self.LOG_LEVEL> 0: 
            self.terminal.writeln("OK", TerminalColors.DARKGREEN)


    def error(self, details):
        """
        Descripció: Imprimeix un missatge d'error pel terminal amb diferent grau de detall segons
                    la configuració triada.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        msg = ""
        if self.LOG_LEVEL> 0: msg += "ERROR"
        if self.LOG_LEVEL> 1: msg += ": " + details
        
        self.terminal.writeln(msg, TerminalColors.DARKRED)
   

    def run_worker(self):
        """
        Descripció: Executa el procés complet del programa, imprimint pel terminal diferent
                    informació d'acord amb la configuració triada.
        Entrada:    Cap. Requereix dels fitxers d'entrada del programa.
        Sortida:    Cap. Genera els fitxers de sortida del programa.
        """
        self.terminal.breakline()        
        self.terminal.writeln("Iniciant el procés:", TerminalColors.YELLOW)
        self.terminal.tab()    
        
        if self.LOG_LEVEL> 0: self.terminal.write("Carregant configuració...")
        try:
            #TODO: si no es diu el contrari, el programa pregunta, en cas contrari, es pot passar un fitxer yaml i llegeix d'aqui en comptes de preguntar
            #setup_options()
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Netejant fitxers antics... ")
        try:
            self.worker.clean_files()
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Comprovant fitxers d'origen... ")
        try:
            self.check_source_file(self.worker.SOURCE_FILE_STUDENTS_WITH_MP)
            self.check_source_file(self.worker.SOURCE_FILE_STUDENT_ANSWERS)    
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Filtrant respostes invàlides... ")
        try:        
            id_to_email_and_name_dict = self.worker.anonymize_answers()
            self.worker.filter_invalid_responses(id_to_email_and_name_dict)
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Filtrant respostes duplicades... ")
        try:
            self.worker.filter_duplicated_answers()
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Generant llistat de respostes... ")
        try:
            self.worker.generate_list_of_answers(id_to_email_and_name_dict)
            self.worker.final_result_files_arranger(id_to_email_and_name_dict)
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Eliminant les dades sensibles... ")
        try:
            self.worker.final_result_files_arranger(id_to_email_and_name_dict)
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Generant estadístiques... ")
        try:
            merged_grup_mp_dict = self.worker.generate_statistics()
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        if self.worker.OPTION_REPORTS == 1:
            if self.LOG_LEVEL> 0: self.terminal.write("Generant informes... ")
            try:
                self.worker.generate_reports(**merged_grup_mp_dict)
                self.succeed()
            except Exception as ex:
                self.catch_exception(ex)

        if self.worker.OPTION_EXPORT_REPORT_CENTRE_TO_PDF == 1:
            if self.LOG_LEVEL> 0: self.terminal.write("Exportant informe de Centre a PDF... ")
            try:
                self.worker.export_centre_report_to_pdf()
                self.succeed()
            except Exception as ex:
                self.catch_exception(ex)

        if self.LOG_LEVEL> 0: self.terminal.write("Eliminant fitxers temporals... ")
        try:
            self.worker.clean_temp_files()
            self.succeed()
        except Exception as ex:
            self.catch_exception(ex)

        self.terminal.untab()
        self.terminal.breakline()
