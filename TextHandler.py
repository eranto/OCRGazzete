from rdflib import logging
from Consts import STATUS_FOLDER
import Utils
from spellchecker import SpellChecker
from functools import reduce
from fuzzywuzzy import fuzz


class TextHandler:
    def __init__(self):
        self.spell = SpellChecker()
        self.no_alternatives = ['no', 'n<x']
        self.class_alternatives = ['class', 'clans']
        self.in_respect_of_alternatives = ['in respect of']
        self.seperators = [' ', ',', '.', '']

    def get_all_misspellings_for_word(self, word, edit_distance=1):
        if(edit_distance == 1):
            return self.spell.edit_distance_1(word)
        else:
            return self.spell.edit_distance_1(word)

    def check_if_tag_contain_appnum_tag(self, str, verification_level=1):
        new_str = str
        no_check_list = list(
            map(lambda t: t in new_str, self.no_alternatives))
        no_check = reduce(lambda t1, t2: t1 or t2, no_check_list)
        class_check_list = list(
            map(lambda t: t in new_str, self.class_alternatives))
        class_check = reduce(
            lambda t1, t2: t1 or t2, class_check_list)
        in_respect_of_check_list = list(
            map(lambda t: t in new_str, self.in_respect_of_alternatives))
        in_respect_of_check = reduce(
            lambda t1, t2: t1 or t2, in_respect_of_check_list)
        if(no_check+class_check+in_respect_of_check >= 2):
            logging.info(str+" 1")
            return True
        elif no_check == True:
            if(verification_level == 2):
                logging.info(str+" 1")
                return True
            else:
                class_alternatives = self.get_all_misspellings_for_word(
                    'class', edit_distance=2)
                in_respect_of_alternatives = self.get_all_misspellings_for_word(
                    'in respect of')
                for word in class_alternatives:
                    if(word in new_str):
                        logging.info(str+" 1")
                        return True
                for word in in_respect_of_alternatives:
                    if(word in new_str):
                        logging.info(str+" 1")
                        return True
                logging.info(str+" 0")
                return False
        logging.info(str+" 0")
        return False

    def parse_numbers_from_string(self, s):
        application_number = -1
        class_number = -1
        if(s == None):
            return -1, -1
        tokens = s.split(' ')
        for i, t in enumerate(tokens):
            tokens[i] = Utils.remove_spaces_at_start_and_end(tokens[i])
            if(tokens[i] == '' or tokens[i] == ' '):
                tokens.remove(tokens[i])
        # save index of every token contain at least one digit
        for i, t in enumerate(tokens):
            if(TextHandler.check_if_word_includes_digit(t) and (application_number == -1 or class_number == -1)):
                if(i > 0 and (tokens[i-1].lower() in self.no_alternatives or tokens[i-1].lower() in self.get_all_misspellings_for_word('no', edit_distance=1))):
                    application_number = tokens[i]
                elif(i > 0 and (tokens[i-1].lower() in self.class_alternatives or tokens[i-1].lower() in self.get_all_misspellings_for_word('class', edit_distance=2))):
                    class_number = tokens[i]
        return application_number, class_number

    @staticmethod
    def check_if_country_or_cities_exist_in_string(text, list_of_lists):
        found = []
        try:
            for list_elem in list_of_lists:
                list_i = list_elem
                for c in list_i:
                    if(text != None and c in text and c not in found):
                        found.append(c)
        except Exception as e:
            logging.exception(e)
            return []
        return found

    @staticmethod
    def check_if_applicant_exist_in_string(text, all_applicants):
        found = []
        list_i = all_applicants
        for c in list_i:
            ratio = fuzz.partial_ratio(
                c, text)
            if(ratio > 75 and c not in found):
                found.append(c)
        return found

    @staticmethod
    def check_if_word_includes_digit(word):
        for ch in word:
            if(ch.isdigit()):
                return True
        return False

    @staticmethod
    def check_is_date_filed_paragraph(text):
        to_search = 'The date of the application'
        ratio = fuzz.partial_ratio(
            to_search, text)
        if(ratio > 70):
            return True
        else:
            return False
