from Consts import STATUS_FOLDER
import Utils


class StatusHandler:
    def __init__(self, paper_name):
        self.paper_name = paper_name

    def write_to_file(self, application_number, i, image_name=''):
        try:
            new_i = i
            if(i == -1 or i == -2):
                new_i = 'x'
            with open('./'+STATUS_FOLDER+'/'+self.paper_name+'.txt', 'a') as fa:
                fa.write(str(application_number)+'-' +
                         str(new_i)+'-'+image_name+'-'+'\n')
                fa.close()
        except:
            raise("Exception: writing to status file")

    def read_status_file(self):
        APP_NUM_INDEX = 0
        ROMAN_INDEX = 1
        IMAGE_NAME_INDEX = 2
        try:
            with open('./'+STATUS_FOLDER+'/'+self.paper_name+'.txt', 'r') as fa:
                self.result = {}
                line = fa.readline()
                while(line != ''):
                    app_num = line.split('-')[APP_NUM_INDEX]
                    image_name = line.split('-')[IMAGE_NAME_INDEX]
                    self.result[app_num] = image_name
                    line = fa.readline()
                fa.close()
            return self.result
        except Exception as e:
            raise(e)
