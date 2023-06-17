from pandas.io import excel
from Consts import PAPERS_FOLDER
import pandas as pd
from bs4 import BeautifulSoup
import Utils
import os
import ExcelHandler


class Trademark:
    def __init__(self, index, tag, application_number=-1, class_number=-1, initial_no=-1, applicant=None, local_agent=None, date_published=None, date_applicated=None):
        self.index = index
        self.tag = None
        self.roman_index = Utils.int_to_Roman(index)
        self.application_number = application_number
        self.class_number = class_number
        self.initial_no = initial_no
        self.applicant = applicant
        self.local_agent = local_agent
        self.date_published = date_published
        self.date_applicated = date_applicated
        self.image_path = None

    def save_trademark(self, folder_name):
        raise NotImplementedError
