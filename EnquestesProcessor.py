#!/usr/bin/python3.7
# -*- coding: UTF-8 -*-
from utilities.terminal import *
import csv
import os
from pip._internal import main
import subprocess
import sys

"""EnquestesProcessor:
Executa el programa de manera normal o en mode test a partir de les opcions especificades a través de la
línia de comandaments.
"""

REQUIREMENTS_FILE = 'requirements.txt'
DEFAULT_SETTINGS_FILE = 'settings.yaml'

def print_run_options():
    """print_run_options()
    Descripció: Imprimeix per pantalla les instruccions d'execució en cas que s'insereixin opcions incorrectes.
    Entrada:    Cap.
    Sortida:    Cap. Impremeix per missatge les instruccions d'execució.
    """
    terminal.breakline()        
    terminal.writeln("Executeu el programa d'acord amb una de les següents opcions:",
                     TerminalColors.YELLOW)
    terminal.tab()
    terminal.writeln("a) Execució d'estadística: python EnquestesProcessor.py [<seetings_file.yaml>]")
    terminal.writeln("b) Execució de tests complets: python EnquestesProcessor.py -t [verbosity: <0> | <1> | <2>]")
    terminal.writeln("c) Execució de tests unitaris: python EnquestesProcessor.py -t -u [verbosity: <0> | <1> | <2>]")
    terminal.writeln("d) Execució de test d'execució completa del codi: python EnquestesProcessor.py -t -c")
    terminal.breakline
    terminal.untab()


def run_manager(settings_yaml_file, reinstalled_modules):
    """run_manager(settings_yaml_file, reinstalled_modules)
    Descripció: Instal·la els mòduls requerits, reinstal·lant-los a la força en cas d'error i executa la
                classe Manager.
    Entrada:    Fitxer amb els ajustos de configuració. Indicació de si els mòduls ja han estat reinstal·lats
                alguna vegada durant el procés.
    Sortida:    Cap. Instal·la els mòduls i executa la classe Manager.
    """
    if (reinstalled_modules is True):
        manager = Manager(settings_yaml_file)
        manager.run_worker()
    else:
        try:
            manager = Manager(settings_yaml_file)
            manager.run_worker()
        except:
            reinstall_modules()
            reinstalled_modules = True
            run_manager(settings_yaml_file, reinstalled_modules)


def run_test_manager(reinstalled_modules, unit_tests_verbosity_level=2):
    """run_test_manager(reinstalled_modules, unit_tests_verbosity_level=2)
    Descripció: Instal·la els mòduls requerits, reinstal·lant-los a la força en cas d'error i executa la
                classe TestManager per l'execució dels tests unitaris i dels resultats complets.
    Entrada:    Indicació de si els mòduls ja han estat reinstal·lats alguna vegada durant el procés.
                Opcionalment el nivell de verbosity dels tests unitaris.
    Sortida:    Cap. Instal·la els mòduls i executa els tests unitaris i dels resultats complets de la
                classe TestManager.
    """
    if (reinstalled_modules is True):
        tester = TestManager()
        tester.run_tests()
    else:
        try:
            tester = TestManager()
            tester.run_tests()
        except:
            reinstall_modules()
            reinstalled_modules = True
            run_test_manager(reinstalled_modules, unit_tests_verbosity_level)


def run_unit_tests(reinstalled_modules, unit_tests_verbosity_level=2):
    """run_unit_tests(reinstalled_modules, unit_tests_verbosity_level=2)
    Descripció: Instal·la els mòduls requerits, reinstal·lant-los a la força en cas d'error i executa la
                classe TestManager per l'execució dels tests unitaris.
    Entrada:    Indicació de si els mòduls ja han estat reinstal·lats alguna vegada durant el procés.
                Opcionalment el nivell de verbosity dels tests unitaris.
    Sortida:    Cap. Instal·la els mòduls i executa els tests unitaris de la classe TestManager.
    """
    if (reinstalled_modules is True):
        tester = TestManager()
        tester.run_unit_tests(unit_tests_verbosity_level)
    else:
        try:
            tester = TestManager()
            tester.run_unit_tests(unit_tests_verbosity_level)
        except:
            reinstall_modules()
            reinstalled_modules = True
            run_unit_tests(reinstalled_modules, unit_tests_verbosity_level)


def run_complete_execution_test(reinstalled_modules):
    """run_complete_execution_test(reinstalled_modules)
    Descripció: Instal·la els mòduls requerits, reinstal·lant-los a la força en cas d'error i executa la
                classe TestManager per l'execució dels tests dels resultats complets.
    Entrada:    Indicació de si els mòduls ja han estat reinstal·lats alguna vegada durant el procés.
    Sortida:    Cap. Instal·la els mòduls i executa els tests dels tests dels resultats complets a través
                de la classe TestManager.
    """
    if (reinstalled_modules is True):
        tester = TestManager()
        tester.run_complete_execution_test()
    else:
        try:
            tester = TestManager()
            tester.run_complete_execution_test()
        except:
            reinstall_modules()
            reinstalled_modules = True
            run_complete_execution_test(reinstalled_modules)


def check_yaml_file_type(arg):
    """check_yaml_file_type(arg)
    Descripció: Comprova que el fitxer amb els ajustos proporcionat a través de la línia de comandaments
                correspon al tipus YAML.
    Entrada:    Argument amb el nom del fitxer.
    Sortida:    True o False d'acord amb el resultat.
    """
    if not ('.' in arg):
        return False
    else:
        extension_position = arg.count('.')
        arg_extension = arg.split('.')[extension_position].lower()
        if (arg_extension == 'yaml'):
            return True
        else:
            return False


def requirements_installation():
    """requirements_installation()
    Descripció: Instal·la els mòduls del fitxer de requeriments REQUIREMENTS_FILE.
    Entrada:    Cap. Requereix de l'existència del fitxer de requeriments REQUIREMENTS_FILE.
    Sortida:    Cap. Instal·la els mòduls necessaris no presents al sistema.
    """
    terminal.breakline()    
    terminal.writeln("Instal·lant mòduls:", TerminalColors.DARKGREY)
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])


def reinstall_modules():
    """reinstall_modules()
    Descripció: Reinstal·la els mòduls del fitxer de requeriments REQUIREMENTS_FILE, encara que hi
                siguin presents al sistema.
    Entrada:    Cap. Requereix de l'existència del fitxer de requeriments REQUIREMENTS_FILE.
    Sortida:    Cap. Reinstal·la tots els mòduls necessaris encara que siguin presents al sistema.
    """
    terminal.breakline()    
    terminal.writeln("Degut a un error d'execució s'està provant a reinstal·lar els mòduls ja presents al sistema; " +
                     "en cas que l'error persisteixi s'avortarà l'execució del programa:", TerminalColors.DARKGREY)
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt", "--force-reinstall"])


if __name__ == '__main__':
    global terminal
    terminal = Terminal()
    requirements_installation()
    terminal.breakline()    
    terminal.write("Processador automàtic d'enquestes: ", TerminalColors.YELLOW)
    terminal.writeln("v3.0")
    terminal.write("Copyright © 2019: ", TerminalColors.YELLOW)
    terminal.writeln("INS Puig Castellar")
    terminal.write("Under the GPL v3.0 license: ", TerminalColors.YELLOW)
    terminal.writeln("https://github.com/ElPuig/Aplicacions-Gestio-Dades")    
    
    from core.manager import *
    from testing.testManager import *
    
    reinstalled_modules = False

    if (len(sys.argv) > 4):
        print_run_options()
    elif (len(sys.argv) == 1):
        run_manager(DEFAULT_SETTINGS_FILE, reinstalled_modules)
    elif (len(sys.argv) == 2):
        if (check_yaml_file_type(sys.argv[1]) is True):
            run_manager(sys.argv[1])
        elif (sys.argv[1] == '-t'):
            run_test_manager(reinstalled_modules)
        else:
            print_run_options()
    elif (len(sys.argv) >= 2):
        if (sys.argv[1] != '-t'):
            print_run_options()
        elif (sys.argv[2] == '0' or sys.argv[2] == '1' or sys.argv[2] == '2'):
            run_test_manager(reinstalled_modules, int(sys.argv[2]))
        elif (sys.argv[2] == '-u'):
            if (len(sys.argv) == 3):
                run_unit_tests(reinstalled_modules)
            elif (sys.argv[3] == '0' or sys.argv[3] == '1' or sys.argv[3] == '2'):
                run_unit_tests(reinstalled_modules, int(sys.argv[3]))
            else:
                print_run_options()
        elif (sys.argv[2] == '-c' and len(sys.argv) == 3):
            run_complete_execution_test(reinstalled_modules)
        else:
            print_run_options()
    else:
        print_run_options()
