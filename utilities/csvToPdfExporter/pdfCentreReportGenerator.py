#!/usr/bin/python3.7
# -*- coding: UTF-8 -*-
import datetime
from jinja2 import Environment, FileSystemLoader
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
from weasyprint import HTML, CSS
import sys
import yaml

"""
Converteix l'informe de Centre en format CSV en un document en PDF, a través de la conversió
intermèdia en HTML.
"""

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))  

class PDF_Centre_Report_Generator():

    def __init__(self, settings_dict=yaml.safe_load(open('settings.yaml'))):
        self.SETTINGS_DICT = settings_dict

        self.TEMP_HTML_FILES_FOLDER = os.path.join(self.SETTINGS_DICT['TEMP_HTML_FILES_FOLDER'])
        self.TEMP_PDF_FILES_FOLDER = os.path.join(self.SETTINGS_DICT['TEMP_PDF_FILES_FOLDER'])
        self.TEMPLATES_FOLDER = os.path.join(self.SETTINGS_DICT['TEMPLATES_FOLDER'])
        self.TEMPLATE_COVER_PAGE = self.SETTINGS_DICT['TEMPLATE_COVER_PAGE']
        self.TEMPLATE_GROUP_PAGE = self.SETTINGS_DICT['TEMPLATE_GROUP_PAGE']
        self.RESULT_COVER_PAGE = self.SETTINGS_DICT['RESULT_COVER_PAGE']
        self.RESULT_GROUP_PAGE_ROOT_FILENAME = self.SETTINGS_DICT['RESULT_GROUP_PAGE_ROOT_FILENAME']
        self.REPORT_OUTPUT_FOLDER = self.SETTINGS_DICT['OUTPUT_FOLDER']
        self.REPORT_PDF_FILE_CENTRE = self.SETTINGS_DICT['REPORT_PDF_FILE_CENTRE']

    def create_cover_page(self):
        """create_cover_page(self)
        Descripció: Genera la portada de l'informe en HTML basat en la plantilla self.TEMPLATE_COVER_PAGE.
        Entrada:    Cap. Requereix de l'existència de la plantilla self.TEMPLATE_COVER_PAGE.
        Sortida:    Portada de l'informe en HMTL.
        """
        current_datetime = datetime.datetime.now()
        current_year = int(current_datetime.year)
        past_year = current_year - 1
        academic_year = "curs " + str(past_year) + "-" + str(current_year)[-2:]

        templates_dir = self.TEMPLATES_FOLDER
        env = Environment(loader = FileSystemLoader(templates_dir))
        template = env.get_template(self.TEMPLATE_COVER_PAGE)

        if not os.path.exists(self.TEMP_HTML_FILES_FOLDER):
            os.makedirs(self.TEMP_HTML_FILES_FOLDER)
        cover_page = os.path.join(self.TEMP_HTML_FILES_FOLDER,
                                "0-" + self.RESULT_COVER_PAGE)
        with open(cover_page, 'w') as cp:
            cp.write(template.render(academic_year = academic_year))

        return self.RESULT_COVER_PAGE


    def create_group_page(self, grup, num, curs_dict, group_info_dict):
        """create_group_page(self, grup, num, curs_dict, group_info_dict)
        Descripció: Genera una pàgina en HTML pels resultats de cada grup, basada en la plantilla
                    self.TEMPLATE_GROUP_PAGE.
        Entrada:    Cap. Requereix de l'existència de la plantilla self.TEMPLATE_GROUP_PAGE.
        Sortida:    Resultats de cada grup en HMTL.
        """
        table_dict = dict(curs_dict)
        group_info_dict = dict(group_info_dict)

        current_datetime = datetime.datetime.now()
        current_year = int(current_datetime.year)
        past_year = current_year - 1
        academic_year = "curs " + str(past_year) + "-" + str(current_year)[-2:]

        departament = group_info_dict['departament']
        cicle = group_info_dict['nom']
        grau_level = group_info_dict['grau']
        curs = group_info_dict['curs']
        
        templates_dir = os.path.join(self.TEMPLATES_FOLDER)
        env = Environment(loader = FileSystemLoader(templates_dir))
        template = env.get_template(self.TEMPLATE_GROUP_PAGE)
        
        if not os.path.exists(self.TEMP_HTML_FILES_FOLDER):
            os.makedirs(self.TEMP_HTML_FILES_FOLDER)
        generated_group_page = os.path.join(self.TEMP_HTML_FILES_FOLDER,
                                            str(num) + "-" + self.RESULT_GROUP_PAGE_ROOT_FILENAME + grup + ".html")
        with open(generated_group_page, 'w') as ggp:
            ggp.write(template.render(items = table_dict,
                                      group = grup,
                                      cicle = cicle,
                                      course = curs,
                                      grau = grau_level,
                                      department = departament,
                                      school_year = academic_year))
        

    def print_html_to_pdf(self, html_page, pdf_result):
        """print_html_to_pdf(self, html_page, pdf_result)
        Descripció: Converteix cada pàgina HTML en un fitxer PDF.
        Entrada:    Ruta de l'arxiu HTML d'entrada. Ruta de l'arxiu PDF de sortida.
        Sortida:    Cap. Genera el fitxer de sortida en PDF.
        """
        if not os.path.exists(self.TEMP_PDF_FILES_FOLDER):
            os.makedirs(self.TEMP_PDF_FILES_FOLDER)
        html = HTML(html_page)
        html.write_pdf(pdf_result)


    def print_template_with_css_file_to_pdf(self, html_page, css_file, pdf_result):
        """print_template_with_css_file_to_pdf(self, html_page, css_file, pdf_result)
        Descripció: Converteix cada pàgina HTML amb els estils en CSS donats en un fitxer PDF.
        Entrada:    Ruta de l'arxiu HTML d'entrada. Ruta del fitxer CSS d'estils. Ruta de
                    l'arxiu PDF de sortida.
        Sortida:    Cap. Genera el fitxer de sortida en PDF.
        """
        html = HTML(html_page)
        html.write_pdf(pdf_result,
                    stylesheets=[CSS(css_file)])


    def merge_pdf_files(self, *group_pdf_files_list):
        """merge_pdf_files(self, *group_pdf_files_list)
        Descripció: Uneix un llistat de fitxers en PDF en un únic arxiu PDF.
        Entrada:    Llistat amb els fitxers PDF per unir.
        Sortida:    Cap. Genera el fitxer únic de sortida en PDF.
        """
        list_of_pdf_files = list(group_pdf_files_list)
        
        merger = PdfFileMerger()
        for pdf_file in list_of_pdf_files:
            pdf_read_file = PdfFileReader(open(os.path.join(self.TEMP_PDF_FILES_FOLDER, pdf_file), 'rb'))
            merger.append(pdf_read_file)
        
        if not os.path.exists(self.REPORT_OUTPUT_FOLDER):
            os.makedirs(self.REPORT_OUTPUT_FOLDER)
        merger.write(os.path.join(self.REPORT_OUTPUT_FOLDER,
                                  self.REPORT_PDF_FILE_CENTRE))
