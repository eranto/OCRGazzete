from pathy import shutil
from Consts import PAPERS_FOLDER, STATUS_FOLDER, NOT_FOUND_FOLDER, XML_FOLDER, ACCURACY_FILE_NAME, XML_HANDLER_1920_YEAR, XML_HANDLER_1920_MONTH
from ExcelHandler import ExcelHandler
from StatusHandler import StatusHandler
from ImageTrademarkXML import ImageTrademarkXML
import Utils
import os
from PIL import Image
from XMLHandler import XMLHandler
from XMLHandler1920 import XMLHandler1920
import logging
FIle_NAME_INDEX = 0
NOT_FOUND = 0


class Paper:
    def __init__(self, file, excel):
        try:
            self.original_file_name = file
            self.file_name = file.split('.')[FIle_NAME_INDEX]
            self.paper_path = PAPERS_FOLDER+'/'+file
            self.status_path = STATUS_FOLDER+'/'+self.file_name+'.txt'
            self.paper_date = Utils.convert_file_date(self.file_name)
            self.rows_for_date = excel.get_rows_from_date(self.paper_date)
            self.number_of_rows = len(self.rows_for_date.values.tolist())
            self.excel = excel
            self.status_handler = StatusHandler(self.file_name)
            logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                                level=logging.INFO, filename=self.file_name+'.log')
            file_name_splited = self.file_name.split('-')
            if((int(file_name_splited[0]) == XML_HANDLER_1920_YEAR and int(file_name_splited[1]) < XML_HANDLER_1920_MONTH) or
               (int(file_name_splited[0]) < XML_HANDLER_1920_YEAR)):
                self.xml = XMLHandler1920(self.file_name, self.rows_for_date)
            else:
                self.xml = XMLHandler(
                    self.file_name, self.rows_for_date)
            self.has_real_file = Utils.is_real_file_exist(self.file_name)
            Utils.create_folder_if_not_exist(STATUS_FOLDER)
            # if current file havent been analyzed yet ,extract already finished on empty_mode (no 1's in already done dictionary)
            is_status_file_path_exists = os.path.exists(
                STATUS_FOLDER+'/'+self.file_name+'.txt')
            if(is_status_file_path_exists is False):
                with open('./'+STATUS_FOLDER+'/'+self.file_name+'.txt', 'a') as fa:
                    fa.close()
            Utils.create_folder_if_not_exist(
                './'+PAPERS_FOLDER+'/'+self.file_name)
            Utils.create_folder_if_not_exist(
                './'+PAPERS_FOLDER+'/'+self.file_name+'/'+NOT_FOUND_FOLDER)
            self.already_done, self.romans_done = self.get_already_finished(
                excel, empty_mode=not is_status_file_path_exists)
            self.countries = []
            self.cities = []
            self.applicants = []
            self.bring_data_from_excel()
            self.trademarks = []
            self.images_app_nums_to_search = []
        except Exception as e:
            print(
                f'failed to create paper object and process file: {file} eror is: {e}')
            raise Exception(e)

    def extract(self, verification_level=1):
        app_nums_left = []
        images_rows = Utils.get_only_zero_value_from_dict(self.already_done)
        for app_num in images_rows:
            if(self.already_done[app_num] == 0):
                app_nums_left.append(app_num)
        if(len(app_nums_left) > 0):
            self.images_app_nums_to_search = app_nums_left
            self.extract_image_trademarks(
                verification_level=verification_level)

    def extract_image_trademarks(self, verification_level=1):
        try:
            self.xml.find_application_numbers_tags_of_images(
                self.images_app_nums_to_search, self.countries, self.cities, self.applicants, verification_level=verification_level)
            matches = self.xml.match_between_image_and_app_num()
            for key in matches.keys():
                app_num = key
                if(matches[key] != -1):
                    trademark_data = self.excel.get_trademark_data_by_application_number(
                        self.paper_date, app_num)
                    trademark = self.create_trademark(-1, trademark_data,
                                                      None, image_name=matches[app_num])
                    self.already_done[int(app_num)] = 1
        except Exception as e:
            # rmtree('./'+XML_FOLDER+'/'+self.file_name)
            raise(e)

    def extract_by_real(self):
        IMAGE_NAME_INDEX = 0
        APP_NUM_INDEX = 1
        real_app_num_to_image_name_dict = {}
        try:
            with open('./'+XML_FOLDER+'/'+self.file_name+'/word/media/'+ACCURACY_FILE_NAME, 'r') as fa:
                self.real_app_num_to_image_name_dict = {}
                line = fa.readline()
                while(line != ''):
                    image_name = line.split('-')[IMAGE_NAME_INDEX].lower()
                    app_num_with_backslash = line.split('-')[APP_NUM_INDEX]
                    app_num = app_num_with_backslash.split('\n')[0]
                    real_app_num_to_image_name_dict[app_num] = image_name
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

            # get excel file and paper object, return a dictionary with 1 for application numbers that have been already extracted and 0 for the rest
            # based on excel tuples
            # return also all roman numbers found

    def get_already_finished(self, excel, empty_mode=False):
        romans = []
        excel_rows = excel.excel
        rows = excel_rows[excel_rows["Publication dd//mm/yyyy"]
                          == 'OG '+self.paper_date]
        application_numbers = rows["Application No."].values.tolist()
        done = {int(key): 0 for key in application_numbers}
        if(empty_mode == False):
            with open(self.status_path, 'r') as f:
                line = f.readline()
                while(line != ''):
                    number = int(line.split('-')[0])
                    if(line.split('-')[1].isdigit() == True):
                        roman = int(line.split('-')[1])
                    else:
                        roman = 'x'
                    done[number] = 1
                    if(roman != 'x'):
                        romans.append(roman)
                    line = f.readline()
            return done, romans
        else:
            return done, []

    def bring_data_from_excel(self):
        self.countries = ExcelHandler.get_countries_from_data_frame(
            self.rows_for_date)
        self.cities = ExcelHandler.get_cities_from_data_frame(
            self.rows_for_date)
        self.applicants = ExcelHandler.get_applicants_from_data_frame(
            self.rows_for_date)

    def create_trademark(self, i, trademark_data, application_number_tag, image_name=None):
        if(image_name is not None):
            trademark = ImageTrademarkXML(
                i, None, image_name, application_number=trademark_data["application_number"], class_number=trademark_data[
                    "class_number"], initial_no=trademark_data["initial_no"], date_published=trademark_data["date_published"],
                applicant=trademark_data["applicant"], local_agent=trademark_data[
                    "local_agent"], date_applicated=trademark_data["date_applicated"],
            )
        else:
            raise Exception(
                "trademark type is not defined text/image")
        trademark.save_trademark(self.file_name)
        self.status_handler.write_to_file(
            trademark.application_number, trademark.index, image_name=trademark.name)
        self.trademarks.append(trademark)
        return trademark

    def copy_not_found_images(self):
        images_matched = list(
            map(lambda trademark: trademark.name, self.trademarks))
        for image in self.xml.images_names:
            if('real' in image):
                continue
            if(image not in images_matched):
                shutil.copy('./'+XML_FOLDER+'/'+self.file_name+'/word/media/' +
                            image, './'+PAPERS_FOLDER+'/'+self.file_name+'/'+NOT_FOUND_FOLDER+'/'+image.split('.')[0]+'.png')

    def create_verified_file(self):
        if(self.has_real_file):
            with open('./'+PAPERS_FOLDER+'/'+self.file_name+'/'+'verified.txt', 'a') as fa:
                fa.write('verified')
                fa.close()

    def copy_original_images(self):
        Utils.create_folder_if_not_exist(
            './'+PAPERS_FOLDER+'/'+self.file_name+'/'+'original')
        Utils.copytree('./'+XML_FOLDER+'/'+self.file_name+'/word/media/', './' +
                       PAPERS_FOLDER+'/'+self.file_name+'/original/')
        for image in os.listdir('./' + PAPERS_FOLDER+'/'+self.file_name+'/original/'):
            if('jpeg' in image):
                im = Image.open('./' + PAPERS_FOLDER+'/' +
                                self.file_name+'/original/'+image)
                im.save('./' + PAPERS_FOLDER+'/' +
                        self.file_name+'/original/'+image.split('.')[0]+'.png')
                os.remove('./' + PAPERS_FOLDER+'/' +
                          self.file_name+'/original/'+image)
