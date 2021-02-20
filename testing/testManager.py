#!/usr/bin/python3.7
# -*- coding: UTF-8 -*-
import unittest
import os
import sys
import shutil

from testing.unittester import *
from testing.completeExecutionTest import *

class TestManager():

    def __init__ (self):
        self.unittester = EnquestesProcessorTest()
        
        self.TESTING_SETTINGS_YAML_FILE = 'testing/testing_settings.yaml'
        self.TESTING_SETTINGS_DICT = yaml.safe_load(open(self.TESTING_SETTINGS_YAML_FILE))


    def run_unit_tests(self, unit_tests_verbosity_level=2):
        """
        Descripció: Executa els tests unitaris.
        Entrada:    Opcionalment admet el nivell de verbosity.
        Sortida:    Cap.
        """
        unit_testing = unittest.TestLoader().loadTestsFromModule(self.unittester)
        unittest.TextTestRunner(verbosity=unit_tests_verbosity_level).run(unit_testing)


    def run_complete_execution_test(self):
        """
        Descripció: Executa els tests de comparació dels fitxers de sortida.
        Entrada:    Cap.
        Sortida:    Cap.
        """
        complete_execution_test = CompleteExecutionTest(self.TESTING_SETTINGS_DICT,
                                                             self.TESTING_SETTINGS_YAML_FILE)
        complete_execution_test.run_complete_execution_test()


    def run_tests(self, unit_tests_verbosity_level=2):
        """
        Descripció: Executa els tests unitaris i els tests de comparació dels fitxers de sortida.
        Entrada:    Opcionalment admet el nivell de verbosity dels tests unitaris.
        Sortida:    Cap.
        """
        self.run_unit_tests(unit_tests_verbosity_level)
        self.run_complete_execution_test()

