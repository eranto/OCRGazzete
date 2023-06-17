from Consts import PAGE_DIVIDER_X_POSITION
from XMLHandler import XMLHandler


class XMLHandler1920 (XMLHandler):
    def __init__(self, paper_date, rows_for_date):
        super().__init__(paper_date, rows_for_date)

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
            # picture and tag is on the same bar on the same page, picature before tag
            if(value['page'] == tag_page and tag_y >= value['y'] and ((tag_x < PAGE_DIVIDER_X_POSITION and value['x'] < PAGE_DIVIDER_X_POSITION) or (tag_x > PAGE_DIVIDER_X_POSITION and value['x'] > PAGE_DIVIDER_X_POSITION))):
                candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = -100000000
            for k, v in candidates.items():
                if(v['y'] > min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            # image in the bottom left bar , tag is on the right bar at the top on the sampe page
            for key, value in images_not_used.items():
                if(value['page'] == tag_page and tag_y <= value['y'] and ((tag_x > PAGE_DIVIDER_X_POSITION and value['x'] < PAGE_DIVIDER_X_POSITION))):
                    candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = -100000000
            for k, v in candidates.items():
                if(v['y'] > min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            # picture is page before on the left bar and the tag is on the next page in the top right bar
            for key, value in images_not_used.items():
                if(value['page'] == tag_page-1 and tag_y < value['y'] and ((tag_x <= PAGE_DIVIDER_X_POSITION and value['x'] > PAGE_DIVIDER_X_POSITION))):
                    candidates[key] = self.image_data[key]
        if(len(candidates) > 0):
            min_y = -100000000
            for k, v in candidates.items():
                if(v['y'] > min_y):
                    min_y = v['y']
                    best = k
            self.image_data[best]['used'] = 1
            return best
        else:
            return best
