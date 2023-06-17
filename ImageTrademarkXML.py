from pandas.io import excel
from Consts import PAPERS_FOLDER, PROJECT_PATH, XML_FOLDER
from Trademark import Trademark
import shutil
import logging


class ImageTrademarkXML(Trademark):
    def __init__(self, index, tag, image_name, application_number=-1, class_number=-1, initial_no=-1, applicant=None, local_agent=None, date_published=None, date_applicated=None):
        super().__init__(index, tag, application_number=application_number, class_number=class_number, initial_no=initial_no,
                         applicant=applicant, local_agent=local_agent, date_published=date_published, date_applicated=date_applicated)
        self.type = "Image"
        self.tag = tag
        self.name = image_name

    def save_trademark(self, folder_name):
        save_to = './'+PAPERS_FOLDER + \
            '/'+folder_name+'/'+str(self.application_number)+'.png'
        try:
            shutil.copyfile(r'./'+XML_FOLDER + '/' +
                            folder_name+'/word/media/'+self.name, save_to)
            print(
                f"tradmark {self.name} saved as image number {self.application_number}")

        except Exception as e:
            raise Exception("failed when trying to copy image", e)
