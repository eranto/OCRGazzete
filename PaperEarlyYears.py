
from ExcelHandler import ExcelHandler
from Paper import Paper
from Consts import XML_FOLDER, ACCURACY_FILE_NAME
import logging


class PaperEarlyYears(Paper):
    def __init__(self, file, excel):
        super().__init__(file, excel)

    def extract_by_real(self):
        IMAGE_NAME_INDEX = 0
        APP_NUM_AND_CLASS_INDEX = 1
        INITIAL_INDEX = 1
        CLASS_INDEX = 0
        real_app_num_to_image_name_dict = {}
        real_initial_and_class_to_image_name_dict = {}
        try:
            with open('./'+XML_FOLDER+'/'+self.file_name+'/word/media/'+ACCURACY_FILE_NAME, 'r') as fa:
                self.real_app_num_to_image_name_dict = {}

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
                        logging.info(initial_and_class)
                        line = fa.readline()
                        continue
                    extracted_app_num = ExcelHandler.get_application_numbers_by_class_and_initial(
                        self.rows_for_date, initial, class_number)
                    if(extracted_app_num != '-1'):
                        real_app_num_to_image_name_dict[extracted_app_num] = image_name
                        real_initial_and_class_to_image_name_dict[(
                            class_number, initial)] = image_name
                    # else:
                    #     try:
                    #         trademark_data = ExcelHandler.get_trademark_data_by_application_number(
                    #             self.paper_date, initial)
                    #         app_num = initial
                    #         if(int(trademark_data[class_number]) == class_number):
                    #             real_app_num_to_image_name_dict[app_num] = image_name
                    #     except Exception as e:
                    #         logging.exception(e)
                    #         continue
                    line = fa.readline()
                fa.close()
        except:
            print(f"reading from real file failed {self.file_name}")
            raise("Exception: reading from real file failed")
        for app_num, image_name in real_app_num_to_image_name_dict.items():
            try:
                trademark_data = self.excel.get_trademark_data_by_application_number(
                    self.paper_date, app_num)
                trademark = self.create_trademark(-1, trademark_data,
                                                  None, image_name=image_name+'.jpeg')
                self.already_done[int(app_num)] = 1
            except Exception as e:
                logging.exception(e)
                continue
