import logging
from tabnanny import check
from typing import ByteString, Text
import zipfile
import os
from lxml import etree
from Consts import XML_FOLDER, PAPERS_FOLDER, PAGE_DIVIDER_X_POSITION
from ExcelHandler import ExcelHandler
import Utils
import docx
from TextHandler import TextHandler
import sys
from Filters import Filters


class XMLHandler:
    def __init__(self, paper_date, rows_for_date):
        self.paper_date = paper_date
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=logging.INFO, filename=paper_date+'.log')
        self.text_handler = TextHandler()
        # if folder with images already exist dont extract files
        with zipfile.ZipFile('./'+PAPERS_FOLDER+'/'+paper_date+'.docx', "r") as zip_ref:
            path = './'+XML_FOLDER+'/'+paper_date
            if(Utils.is_paper_folder_exist(paper_date) == False):
                Utils.create_folder_if_not_exist(path)
                zip_ref.extractall(path)
                xml_content = zip_ref.read('word/document.xml')
            else:
                parsed = etree.parse(
                    './'+XML_FOLDER+'/'+paper_date+'/word/document.xml')
                xml_content = etree.tostring(
                    parsed, encoding='utf8', method='xml')
        tree = etree.fromstring(xml_content)
        self.tree = etree.ElementTree(tree)
        self.ns = {}  # namespace dict
        etree.indent(self.tree, space="\t", level=0)
        self.tree.write(path+'/indent.xml')
        self.images_path = path+'/word/media'
        self.images_names = os.listdir(self.images_path)
        self.rows_for_date = rows_for_date
        self.ordered_paragraphs = []
        self.map_rId_to_image_name()
        self.build_namespaces_dict()
        self.find_all_images_in_xml()
        self.sort_paragraphs_order()

    # map rId of all images from document.xml.rels file
    def map_rId_to_image_name(self):
        doc = docx.Document(docx='./'+PAPERS_FOLDER +
                            '/'+self.paper_date+'.docx')
        part = doc.part
        rels = part.rels
        self.rId_dict = {}
        for rel in rels.values():
            try:
                rId = rel.rId
                try:
                    target = rel.target_part
                except ValueError:
                    # rel.target_ref is from type media/imageX.jpeg
                    image_name = rel.target_ref.split('/')[1]
                    self.rId_dict[rId] = image_name
                    continue
                if('image' in target.content_type):
                    # target.partname is from type /word/media/imageX.jpeg
                    image_name = target.partname.split('/')[3]
                    self.rId_dict[rId] = image_name
                else:
                    continue
            except Exception as e:
                print(f"failed to extract rel from rels due to:{e}")
                continue

    def find_all_images_in_xml(self):
        self.images_elements = []
        self.image_data = {}
        self.page_numbers = [0]
        for elem in self.tree.iter():
            if(elem.tag == self.ns["w"]+'drawing'):
                rId = -1
                cords = {'page': -1, 'x': -1, 'y': -1}  # cordinates
                drawing = elem
                for e in drawing.iter():
                    if(e.tag == self.ns["a"]+'blip'):
                        ns = Utils.add_curly_braces_to_string(e.nsmap["r"])
                        rId = (e.attrib[ns+'embed'])
                        p_element = self.get_ancestor_by_type(
                            e, self.ns["w"]+'p')
                        try:
                            ppr_element = p_element.find(self.ns['w']+'pPr')
                            wframe_element = ppr_element.find(
                                self.ns['w']+'framePr')
                            end_of_page_flag = self.check_if_p_tag_has_page_bottom_tag(
                                p_element)
                            if(end_of_page_flag):
                                cords['page'] = self.page_numbers[-1]-1
                                cords['x'] = previous['x']
                                cords['y'] = 800000
                                self.image_data[rId] = cords
                                break
                            if(wframe_element is None):
                                break
                            cords['page'] = self.page_numbers[-1]
                            cords['x'] = int(
                                wframe_element.attrib[self.ns['w']+'x'])
                            if(self.paper_date == '45-06-07' and cords['y'] == -1 and '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}y' not in wframe_element.attrib):
                                cords['y'] = 10000
                            else:
                                cords['y'] = int(
                                    wframe_element.attrib[self.ns['w']+'y'])
                            cords['name'] = self.rId_dict[rId]
                            self.image_data[rId] = cords
                            previous = cords
                        except Exception as e:
                            print(e, sys.exc_info()
                                  [-1].tb_lineno, type(e).__name__)
                            raise(e)
                self.images_elements.append(elem)
            elif(elem.tag == self.ns["w"]+'footnotePr'):
                self.page_numbers.append(self.page_numbers[-1]+1)
        print(self.image_data)

    def find_application_numbers_tags_of_images(self, application_numbers_to_search, all_countries, all_cities, all_applicants, verification_level=1):
        application_numers_left = application_numbers_to_search.copy()
        self.application_numbers_cords = {}
        pages = [0]
        number_of_tags_identified = 0
        for elem in self.tree.iter():
            try:
                row_data = None
                application_number = -1
                class_number = -1
                real_class_number = -1
                if(len(application_numers_left) == 0):
                    break
                # if tag is paragraph tag
                if(elem.tag == self.ns['w']+'p'):
                    text = self.get_text_from_paragraph(elem)
                    text = Utils.clean_text(text)
                    if(text is None):
                        continue
                    if(self.text_handler.check_if_tag_contain_appnum_tag(text, verification_level=verification_level)):
                        text = self.get_next_two_paragraphs(
                            elem)
                        number_of_tags_identified += 1
                        # get application number and class number from tag
                        application_number, class_number = self.text_handler.parse_numbers_from_string(
                            text)
                        application_date = self.get_application_date(elem)
                        countries_in_text = TextHandler.check_if_country_or_cities_exist_in_string(
                            text, all_countries)
                        cities_in_text = TextHandler.check_if_country_or_cities_exist_in_string(
                            text, all_cities)
                        applicants_in_text = TextHandler.check_if_applicant_exist_in_string(
                            text, all_applicants)
                        filter_flag = 'MULTIPLE'  # flag can have 3 values - MULTIPLE, ONE, ZERO
                        Filters.init_filter(application_numers_left)
                        # filter by application_number_and_class
                        if(Utils.check_if_application_and_class_is_ok(application_number, class_number, application_numers_left)):
                            filter_flag = Filters.filter_list_of_applications_number_by_app_num_and_class(
                                self.rows_for_date, application_number, class_number)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and application_date != None):
                            filter_flag = Filters.filter_list_of_application_numbers_by_application_date(
                                self.rows_for_date, application_date)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and str(class_number).isdigit() and int(class_number) != -1):
                            filter_flag = Filters.filter_list_of_application_numbers_by_class_number(
                                self.rows_for_date, class_number)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and len(applicants_in_text) > 0):
                            filter_flag = Filters.filter_list_of_application_numbers_by_applicant(
                                self.rows_for_date, applicants_in_text)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and len(countries_in_text) > 0):
                            filter_flag = Filters.filter_list_of_application_numbers_by_country(
                                self.rows_for_date, countries_in_text)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and len(cities_in_text) > 0):
                            filter_flag = Filters.filter_list_of_application_numbers_by_city(
                                self.rows_for_date, cities_in_text)
                        if(filter_flag in ["MULTIPLE", "ZERO"] and str(application_number).isdigit() is False and application_number != -1 and len(Filters.intersection_of_lists(Filters.list_to_filter)) != 1 and verification_level == 2):
                            filter_flag = Filters.filter_list_of_application_numbers_by_pattern(
                                self.rows_for_date, application_number)
                        filtered_list_of_appplications_numbers = Filters.filter()
                        if(len(filtered_list_of_appplications_numbers) == 1):
                            application_number = filtered_list_of_appplications_numbers[0]
                        else:
                            application_number = -1
                        # if appication number was found
                        if(application_number != -1):
                            row_data = ExcelHandler.get_rowdata_by_application_number(
                                self.rows_for_date, str(application_number))
                            if(row_data != None):
                                real_class_number = int(
                                    row_data['class_number'])
                        # if(int(application_number) in application_numers_left and (class_number == real_class_number or class_number == -1 or verification_level == 2)):
                        if(application_number != -1):
                            app_num = int(application_number)
                            x, y = self.get_cords_from_paragraph(elem)
                            self.application_numbers_cords[str(app_num)] = {
                                'x': x, 'y': y, 'page': pages[-1], }
                            if(app_num in application_numers_left):
                                application_numers_left.remove(app_num)
                        else:
                            logging.info(
                                f" failed at tag last condition: {number_of_tags_identified}: {application_number}, {class_number}, {real_class_number}, {application_date}")
                        logging.info(
                            f"{number_of_tags_identified}: {application_number}, {class_number}, {countries_in_text},{cities_in_text}, {application_date}")
                # find page end tag
                elif(elem.tag == self.ns["w"]+'footnotePr'):
                    pages.append(pages[-1]+1)
                    logging.info(f"new page {pages[-1]}")
            # print(self.application_numbers_cords)
            except Exception as e:
                logging.exception(e)
                continue
        logging.info(f"tags identified: {number_of_tags_identified}")

    def match_between_image_and_app_num(self):
        logging.info("matches:")
        matches = {}
        for key in self.application_numbers_cords.keys():
            tag_page = int(self.application_numbers_cords[key]['page'])
            tag_x = int(self.application_numbers_cords[key]['x'])
            tag_y = int(self.application_numbers_cords[key]['y'])
            best = self.get_image_candidate_by_tag(tag_page, tag_x, tag_y)
            best_from_all = self.get_image_candidate_by_tag(
                tag_page, tag_x, tag_y, only_not_used=False)
            if(best == best_from_all):
                matches[key] = best
            else:
                matches[key] = None
        for app_num, rId in matches.items():
            if(rId is not None):
                image_name = self.rId_dict[rId]
                matches[app_num] = image_name
                logging.info(f"{app_num}  :  {image_name}")
            else:
                matches[app_num] = -1
        num_of_matches = len(dict(
            filter(lambda elem: elem[1] != -1, matches.items())).keys())
        logging.info(
            f"num of tags:{len(self.application_numbers_cords.keys())} , num of images data keys: {len(self.image_data.keys())}, num of matches: {num_of_matches}")
        print(matches)
        return matches

    def get_image_candidate_by_tag(self, tag_page, tag_x, tag_y, only_not_used=True):
        candidates = {}
        best = None
        # calculate which images havent been used yet
        images_not_used = {}
        if(only_not_used == True):
            for key, value in self.image_data.items():
                if('used' not in value.keys()):
                    images_not_used[key] = value
        else:
            images_not_used = self.image_data.copy()
        # find best image according to it's position and tag position
        for key, value in images_not_used.items():
            # picture is on the left bar on the same page
            if(value['page'] == tag_page and tag_y <= value['y'] and ((tag_x < PAGE_DIVIDER_X_POSITION and value['x'] < PAGE_DIVIDER_X_POSITION) or (tag_x > PAGE_DIVIDER_X_POSITION and value['x'] > PAGE_DIVIDER_X_POSITION))):
                candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = 100000000
            for k, v in candidates.items():
                if(v['y'] < min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            for key, value in images_not_used.items():
                if(value['page'] == tag_page and tag_y >= value['y'] and ((tag_x < PAGE_DIVIDER_X_POSITION and value['x'] > PAGE_DIVIDER_X_POSITION))):
                    candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = 100000000
            for k, v in candidates.items():
                if(v['y'] < min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            # picture is on the right bar on the next page
            for key, value in images_not_used.items():
                if(value['page'] == tag_page+1 and tag_y >= value['y'] and ((tag_x > PAGE_DIVIDER_X_POSITION and value['x'] < PAGE_DIVIDER_X_POSITION))):
                    candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = 100000000
            for k, v in candidates.items():
                if(v['y'] < min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            return best

    def build_namespaces_dict(self):
        self.ns["w"] = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        self.ns["a"] = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

    # for example tag = <a:blip> and type_tage=<Drawing> wil return the ancestor of <a:blip> that is from type <Drawing>
    def get_ancestor_by_type(self, tag, type_tag):
        parent = tag.getparent()
        while(parent.tag != type_tag or parent.tag == self.ns["w"]+'document'):
            parent = parent.getparent()
        return parent

    def check_if_p_tag_has_page_bottom_tag(self, p_tag):
        for elem in p_tag.iter():
            if(elem.tag == self.ns["w"]+'footnotePr'):
                return True
        return False

    # get w:p tag and extract it's cordinates using w:framePr x w:x and w:y

    def get_cords_from_paragraph(self, p_tag, continue_on_error=False):
        try:
            w_ppr = p_tag.find(self.ns['w']+'pPr')
            w_frame_pPr = w_ppr.find(self.ns['w']+'framePr')
            x = w_frame_pPr.attrib[self.ns['w']+'x']
            y = w_frame_pPr.attrib[self.ns['w']+'y']
        except Exception as e:
            if(continue_on_error):
                return -1, -1
            logging.exception(e)
            raise e
        return x, y

    def get_text_from_paragraph(self, p_tag):
        text = ""
        w_rs = p_tag.findall(self.ns['w']+'r')
        for w_r in w_rs:
            w_ts = w_r.findall(self.ns['w']+'t')
            for w_t in w_ts:
                text += w_t.text + \
                    ' ' if w_t is not None else ""
        return text
    # order paragraph by page, then by column(x<4000 or x>4000 ), they by y cordinate

    def sort_paragraphs_order(self):
        paragraphs = []
        pages = [0]
        # create list of all paragraphs
        for elem in self.tree.iter():
            if(elem.tag == self.ns["w"]+'p'):
                x, y = self.get_cords_from_paragraph(
                    elem, continue_on_error=True)
                paragraphs.append(
                    (elem, pages[-1], int(x), int(y)))
            elif(elem.tag == self.ns["w"]+'footnotePr'):
                pages.append(pages[-1]+1)
        s = sorted(paragraphs, key=lambda x: (
            x[1], 0 if x[2] <= PAGE_DIVIDER_X_POSITION else 1, x[3]))  # (Paragraph,page,x,y)
        self.ordered_paragraphs = s

    # def get_next_two_paragraphs(self, elem):
    #     flag = False
    #     text = ""
    #     i = 0
    #     for elem2 in self.tree.iter():
    #         if(elem2 == elem):
    #             flag = True
    #             text = self.get_text_from_paragraph(elem2)

    #         if(flag != True):
    #             continue
    #         else:
    #             if(elem != elem2 and elem2.tag == self.ns["w"]+'p'):
    #                 i += 1
    #                 text2 = self.get_text_from_paragraph(elem2)
    #                 text2 = Utils.clean_text(text2)
    #                 if(self.text_handler.check_if_tag_contain_appnum_tag(text2) is False):
    #                     text += " " + Utils.clean_text(text2)
    #                 else:
    #                     text = Utils.clean_text(text)
    #                     return text

    #         if(i > 2):
    #             text = Utils.clean_text(text)
    #             return text

    def get_next_two_paragraphs(self, elem):
        for index, p in enumerate(self.ordered_paragraphs):
            if(p[0] == elem):
                text = Utils.clean_text(self.get_text_from_paragraph(elem))
                i = 1
                num_of_paragraphs_added = 0
                break
        while(num_of_paragraphs_added < 2):
            if(index+i < len(self.ordered_paragraphs)):
                if(self.ordered_paragraphs[index+i][1] != -1):
                    text2 = Utils.clean_text(self.get_text_from_paragraph(
                        self.ordered_paragraphs[index+i][0])
                    )

                else:
                    i += 1
                text += text2
                num_of_paragraphs_added += 1
            else:
                break
        return text

    def get_application_date(self, elem):
        flag = False
        i = 0
        for elem2 in self.tree.iter():
            if(elem2 == elem):
                flag = True
                text = self.get_text_from_paragraph(elem2)
                if('filed' in text):
                    date = Utils.get_date_from_text(text)
                    return date
            if(flag != True):
                continue
            else:
                if(elem != elem2 and elem2.tag == self.ns["w"]+'p'):
                    i += 1
                    text = self.get_text_from_paragraph(elem2)
                    text = Utils.clean_text(text)
                    if('filed' in text):
                        date = Utils.get_date_from_text(text)
                        return date
            if(i > 3):
                return None

    # if __name__ == '__main__':
    #     try:
    #         from XMLHandler import XMLHandler
    #         xml = XMLHandler('48-02-12')
    #         xml.find_all_images_in_xml()
    #         xml.find_application_numbers_tags_of_images(
    #             [7589, 7823, 8684, 8704, 8772, 8877, 8973, 8974, 9010, 9042, 9043, 9099])
    #         matches = xml.match_between_image_and_app_num()
    #         rmtree('./'+XML_FOLDER+'/'+'48-02-12')
    #     except Exception as e:
    #         rmtree('./'+XML_FOLDER+'/'+'48-02-12')
    #         raise(e)
