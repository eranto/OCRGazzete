from operator import index
from ExcelHandler import ExcelHandler
from shutil import copy
import Utils


class Filters():
    list_to_filter = []
    filterd_list = []

    @staticmethod
    def init_filter(application_numbers_left):
        application_numbers_left_str = list(map(
            lambda x: str(x), application_numbers_left))
        Filters.list_to_filter = [application_numbers_left_str]
        Filters.filtered_list = []

    @staticmethod
    def filter():
        copy_of_list_to_filter = Filters.list_to_filter.copy()
        Filters.filterd_list = Filters.intersection_of_lists(
            copy_of_list_to_filter)

        # if(len(Filters.filterd_list) == 0):
        #     flag = False
        #     copy_of_list_to_filter = []
        #     for li in Filters.list_to_filter:
        #         if(len(li)) > 1 or flag:
        #             copy_of_list_to_filter.append(li)
        #         else:
        #             flag = True
        #     Filters.filterd_list = Filters.intersection_of_lists(
        #         copy_of_list_to_filter)
        return Filters.filterd_list

    @staticmethod
    def intersection_of_lists(lists):
        if(len(lists) == 0):
            return []
        if(len(lists) == 1):
            return lists[0]
        else:
            new_lists = lists
            new_lists[1] = list(set(lists[0]) & set(lists[1]))
            return Filters.intersection_of_lists(new_lists[1:])

    @staticmethod
    def filter_list_of_applications_number_by_app_num_and_class(rows_for_date, application_number, class_number):
        application_number = int(application_number)
        class_number = int(class_number)
        if(application_number != -1):
            row_data = ExcelHandler.get_rowdata_by_application_number(
                rows_for_date, str(application_number))
            Filters.list_to_filter.append([str(application_number)])
            if(len(Filters.intersection_of_lists(Filters.list_to_filter)) == 1):
                return 'ONE'
            else:
                return 'ZERO'
        else:
            return 'ZERO'

    @staticmethod
    def filter_list_of_application_numbers_by_application_date(rows_for_date, application_date):
        filter_flag = 'MULTIPLE'
        candidates_by_date = ExcelHandler.get_application_numbers_by_application_date(
            rows_for_date, application_date)
        if(len(candidates_by_date) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_date)
        elif(len(candidates_by_date) == 0):
            filter_flag = "ZERO"
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_date)
        return filter_flag

    @staticmethod
    def filter_list_of_application_numbers_by_class_number(rows_for_date, class_number):
        candidates_by_class = ExcelHandler.get_application_numbers_by_class(
            rows_for_date, class_number)
        if(len(candidates_by_class) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_class)
        elif(len(candidates_by_class) == 0):
            filter_flag = "ZERO"
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_class)
        return filter_flag

    @staticmethod
    def filter_list_of_application_numbers_by_country(rows_for_date, countries_in_text):
        candidates_by_country = ExcelHandler.get_application_number_by_country(
            rows_for_date, countries_in_text)
        if(len(candidates_by_country) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_country)
        elif(len(candidates_by_country) == 0):
            filter_flag = "ZERO"
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_country)
        return filter_flag

    @staticmethod
    def filter_list_of_application_numbers_by_city(rows_for_date, cities_in_text):
        candidates_by_city = ExcelHandler.get_application_number_by_city(
            rows_for_date, cities_in_text)
        if(len(candidates_by_city) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_city)
        elif(len(candidates_by_city) == 0):
            filter_flag = "ZERO"
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_city)
        return filter_flag

    @staticmethod
    def filter_list_of_application_numbers_by_applicant(rows_for_date, applicants_in_text):
        candidates_by_applicant = ExcelHandler.get_application_number_by_applicant(
            rows_for_date, applicants_in_text)
        if(len(candidates_by_applicant) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_applicant)
        elif(len(candidates_by_applicant) == 0):
            filter_flag = "ZERO"
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_applicant)
        return filter_flag

    @staticmethod
    def filter_list_of_application_numbers_by_pattern(rows_for_date, application_number):
        filter_flag = 'MULTIPLE'
        pattern = Utils.build_pattern(application_number)
        numbers = ExcelHandler.get_applications_numbers_from_data_frame(
            rows_for_date)
        candidates_by_pattern = []
        for n in numbers:
            flag = True
            if(len(pattern) != len(n)):
                continue
            # check if match for pattern
            for index, ch in enumerate(n):
                if((ch == pattern[index] or pattern[index] == 'X') is False):
                    flag = False
                    break
            if(flag):
                candidates_by_pattern.append(n)
        if(len(candidates_by_pattern) == 1 and len(Filters.list_to_filter) >= 2):
            filter_flag = "ONE"
            Filters.list_to_filter.append(candidates_by_pattern)
            return filter_flag

        elif(len(candidates_by_pattern) == 0):
            filter_flag = "ZERO"
            return filter_flag
        else:
            filter_flag = "MULTIPLE"
            Filters.list_to_filter.append(candidates_by_pattern)
            return filter_flag
