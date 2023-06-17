import logging
from ExcelHandler import ExcelHandler
from Consts import ACCURACY_FILE_NAME, STATUS_FOLDER, XML_FOLDER
import Utils
import os


class AccuracyCalculator:
    def __init__(self, paper_name, result, number_of_rows, rows_for_date):
        self.paper_name = paper_name
        self.real_app_num_to_image_name_dict = None
        self.result = result
        self.number_of_rows = number_of_rows
        print(
            f"number of rows for date {self.paper_name}: {self.number_of_rows}")
        self.accuracy = None
        if(int(paper_name.split('-')[0]) <= 25):
            self.read_accuracy_file_early_years(rows_for_date)
        else:
            self.read_accuracy_file()
        self.calculate_accuracy(self.result)

    def read_accuracy_file(self):
        IMAGE_NAME_INDEX = 0
        APP_NUM_INDEX = 1
        if(Utils.is_paper_folder_exist(self.paper_name) and Utils.is_real_file_exist(self.paper_name)):
            try:
                with open('./'+XML_FOLDER+'/'+self.paper_name+'/word/media/'+ACCURACY_FILE_NAME, 'r') as fa:
                    self.real_app_num_to_image_name_dict = {}
                    line = fa.readline()
                    while(line != ''):
                        image_name = line.split('-')[IMAGE_NAME_INDEX].lower()
                        app_num_with_backslash = line.split('-')[APP_NUM_INDEX]
                        app_num = app_num_with_backslash.split('\n')[0]
                        self.real_app_num_to_image_name_dict[app_num] = image_name
                        line = fa.readline()
                    fa.close()
            except:
                print(f"reading from real file failed {self.paper_name}")
                raise("Exception: reading from real file failed")

    def read_accuracy_file_early_years(self, rows_for_date):
        IMAGE_NAME_INDEX = 0
        APP_NUM_AND_CLASS_INDEX = 1
        INITIAL_INDEX = 1
        CLASS_INDEX = 0
        if(Utils.is_paper_folder_exist(self.paper_name) and Utils.is_real_file_exist(self.paper_name)):
            try:
                with open('./'+XML_FOLDER+'/'+self.paper_name+'/word/media/'+ACCURACY_FILE_NAME, 'r') as fa:
                    self.real_app_num_to_image_name_dict = {}
                    self.real_initial_and_class_to_image_name_dict = {}
                    line = fa.readline()
                    while(line != ''):
                        image_name = line.split('-')[IMAGE_NAME_INDEX].lower()
                        app_num_and_class_with_backslash = line.split(
                            '-')[APP_NUM_AND_CLASS_INDEX]
                        app_num_and_class = app_num_and_class_with_backslash.split('\n')[
                            0]
                        initial_and_class = app_num_and_class.split('_')
                        try:
                            class_number = initial_and_class[CLASS_INDEX]
                            initial = initial_and_class[INITIAL_INDEX]
                        except Exception as e:
                            logging.exception(e)
                            line = fa.readline()
                            continue
                        extracted_app_num = ExcelHandler.get_application_numbers_by_class_and_initial(
                            rows_for_date, initial, class_number)
                        self.real_initial_and_class_to_image_name_dict[(
                            class_number, initial)] = image_name
                        self.real_app_num_to_image_name_dict[extracted_app_num] = image_name
                        line = fa.readline()
                    fa.close()
            except:
                print(f"reading from real file failed {self.paper_name}")
                raise("Exception: reading from real file failed")

    def calculate_accuracy(self, result):
        hits = 0
        misses = 0
        misses_text = ""
        try:
            if(self.real_app_num_to_image_name_dict is not None):
                for app_num, image_name in self.real_app_num_to_image_name_dict.items():
                    if(app_num not in result.keys()):
                        continue
                    result_image_num = result[app_num].split('.')[0]
                    if(image_name == result_image_num):
                        hits += 1
                    else:
                        misses += 1
                        misses_text += app_num+": guess:"+result_image_num+" real:"+image_name+','
        except Exception as e:
            print(e, app_num)
            raise e
        try:
            if(hits+misses == 0):
                accuracy = 0
            else:
                accuracy = hits/(hits+misses)
            if(Utils.is_real_file_exist(self.paper_name)):
                print(
                    f"accuracy for {self.paper_name} is: {round(accuracy,2)}, num of hits: {hits}/{hits+misses}, misses: {misses} ,identified: {(hits+misses)}/{len(self.real_app_num_to_image_name_dict.keys())} = {round((hits+misses)/len(self.real_app_num_to_image_name_dict.keys()),2)},  misses_text:{misses_text}")
                AccuracyCalculator.write_to_accuracy_file(
                    f"accuracy for {self.paper_name} is: {round(accuracy,2)}, num of hits: {hits}/{hits+misses}, misses: {misses} ,identified: {(hits+misses)}/{len(self.real_app_num_to_image_name_dict.keys())} = {round((hits+misses)/len(self.real_app_num_to_image_name_dict.keys()),2)},  misses_text:{misses_text}")
                return accuracy
            else:
                print(
                    f"no real file for {self.paper_name}  ,identified: {len(self.result.keys())}/{self.number_of_rows} = {round(len(self.result.keys())/self.number_of_rows,2)}")
                AccuracyCalculator.write_to_accuracy_file(
                    f"no real file for {self.paper_name}  ,identified: {len(self.result.keys())}/{self.number_of_rows} = {round(len(self.result.keys())/self.number_of_rows,2)}")
                return -1

        except ZeroDivisionError:
            print('divide by zero is not allowed')

    @ staticmethod
    def write_to_accuracy_file(line_to_write):
        with open('./accuracy/log.txt', 'a') as f:
            f.write(line_to_write)
            f.write('\n')
            f.close
