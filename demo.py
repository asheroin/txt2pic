# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont
# import Image
# import ImageFont
# import ImageDraw
import math
import re
import json
import sys
import argparse

"""
settings
"""


pic_width = 750
# pic_width = 690
text_pix = 32
title_pix  = 50
date_pix = 25
text_width = 16
text_start_heigth = 10

"""
main
"""

class textParser(object):
    def __init__(self,fname):
        self.n_word = int(math.floor((pic_width - text_width * 2) / text_pix))
        self.line_list,self.f_r = self.__parser(open(fname, "r"))
        # self.cur_p = text_start_heigth * 4 + title_pix + date_pix + text_pix
        f_r = self.f_r

    def __parser(self,file_object):
        """
        text praser
        """
        # line_list = [line.strip() for line in file_object.readlines() if line.strip() != ""]
        line_list = [line.strip() for line in file_object.readlines()]
        re_pattern = re.compile(r'^\[.*\]')
        text_dict = {}
        text_dict['text'] = []
        for idx, line in enumerate(line_list):
            # print line.decode("utf-8")
            re_result = re_pattern.findall(line)
            if len(re_result) == 0:
                continue
            if re_result[0].startswith('[title]'):
                text_dict['title'] = {'line':idx, 'content':re.sub(r'^\[.*\]', '', line)}
            elif re_result[0].startswith('[date]'):
                text_dict['date'] = {'line':idx, 'content':re.sub(r'^\[.*\]', '', line)}
            elif re_result[0].startswith('[profile_img]'):
                pass
            elif re_result[0].startswith('[chn]'):
                text_dict['text'].append({'start':idx, 'content':line, 'type':'chn'})
            elif re_result[0].startswith('[jpn]'):
                text_dict['text'].append({'start':idx, 'content':line, 'type':'jpn'})
            elif re_result[0].startswith('[img]'):
                text_dict['text'].append({'start':idx, 'content':line, 'type':'img'})
        for idx, value in enumerate(text_dict['text']):
            if idx == 0:
                continue
            text_dict['text'][idx-1]['end'] = value['start']
        text_dict['text'][-1]['end'] = len(line_list)
        json.dump(text_dict, open('praser_result.txt', 'w'), indent=1)
        return line_list,text_dict


    def __getDrawDict(self):
        assert self.f_r
        
        self.draw_dict = []
        for idx, ctx in enumerate(self.f_r['text']):
            draw_block = {}
            draw_block['type'] = ctx['type']
            draw_block['ctx'] = []
            if ctx['type']=='img':
                # im_ctx = Image.open(ctx['content'])
                draw_block['ctx'] = re.sub(r'^\[.*\]', '', ctx['content'])
                self.draw_dict.append(draw_block)
            else:
                for line in self.line_list[ctx['start']:ctx['end']]:
                    text = re.sub(r'^\[.*\]', '', line)
                    line = text.decode("utf-8")
                    text_lines = [line[idx*self.n_word:(idx+1)*self.n_word] for idx in range(int(math.ceil(1.0*len(line) / self.n_word)))]
                    for idx,line in enumerate(text_lines):
                        draw_block['ctx'].append({'ctx':line})
                self.draw_dict.append(draw_block)


    def __buildDrawBlock(self):
        
        self.cur_p = text_start_heigth 
        title_line = self.f_r['title']['content'].decode("utf-8")
        title_n_word = int(math.floor((pic_width - text_width * 2) / title_pix))
        title_lines = [title_line[idx*title_n_word:(idx+1)*title_n_word] for idx in range(int(math.ceil(1.0*len(title_line) / title_n_word)))]
        # title block
        title_blocks = []
        for idx,val in enumerate(title_lines):
            title_block = {}
            title_block['ctx'] = val
            title_block['draw_start'] = self.cur_p
            title_blocks.append(title_block)
            self.cur_p += title_pix + text_start_heigth
        # date block
        self.cur_p += text_start_heigth
        date_block = {}
        date_block['ctx'] = self.f_r['date']['content'].decode("utf-8")
        date_block['draw_start']  =  self.cur_p
        self.cur_p += date_pix + text_start_heigth
        # blank line
        self.cur_p += text_pix + text_start_heigth

        for block in self.draw_dict:
            if block['type']=='img':
                self.cur_p+=5
                im = Image.open(block['ctx'])
                (x, y) = im.size
                scale = x / (pic_width - 2.0*text_width)
                new_y = int(math.floor(y / scale))
                block['draw_start']=self.cur_p
                block['new_y'] = new_y
                self.cur_p+=new_y+5
                pass 
            else: 
                for line in block['ctx']:
                    line['draw_start'] = self.cur_p
                    self.cur_p+=text_pix+5
            self.cur_p+=text_pix

        self.draw_block = {}
        self.draw_block['title'] = title_blocks
        self.draw_block['date'] = date_block
        self.draw_block['text'] = self.draw_dict
        self.draw_block['heigth'] = self.cur_p
        return self.draw_block
    def bulid(self):
        self.__getDrawDict()
        return self.__buildDrawBlock()


class imgDrawer(object):
    def __init__(self,draw_block):
        font_type = "AdobeKaitiStd-Regular.otf"
        self.draw_block = draw_block
        cur_p = self.draw_block['heigth']
        self.font = ImageFont.truetype(os.path.join("font",font_type), text_pix)
        self.font_title = ImageFont.truetype(os.path.join("font",font_type), title_pix)
        self.font_date = ImageFont.truetype(os.path.join("font",font_type), date_pix)

        self.im = Image.new("RGBA", (pic_width, cur_p), (255, 255, 255,0))
        self.background = Image.new("RGB", (pic_width, cur_p), (255, 255, 255))
        self.background = Image.new("RGB", (pic_width, cur_p), (255, 255, 224))
    def draw(self):
        draw_block = self.draw_block
        dr = ImageDraw.Draw(self.im)

         

        for line in draw_block['title']:
            dr.text((text_width, line['draw_start']), line['ctx'], font=self.font_title, fill="#000000")
        
        dr.text((text_width, draw_block['date']['draw_start']), draw_block['date']['ctx'], font=self.font_date, fill="#000000")
        # draw text
        for block in draw_block['text']:
            if block['type']=='img':
                imt = Image.open(block['ctx'])
                im_resize = imt.resize((int(pic_width - 2.0*text_width),block['new_y']), Image.ANTIALIAS)
                self.im.paste(im_resize,(text_width,block['draw_start']))
            elif block['type'] == 'chn':
                for line in block['ctx']:
                    dr.text((text_width, line['draw_start']), line['ctx'], font=self.font, fill=(0,0,0,255))
            elif block['type'] == 'jpn':
                for line in block['ctx']:
                    dr.text((text_width, line['draw_start']), line['ctx'], font=self.font, fill=(0,0,0,100))
        self.background.paste(self.im,self.im)
        return self.background

def main():
    """
    main func
    """
    fname = "example.txt"
    draw_block = textParser(fname).bulid()
    res = imgDrawer(draw_block).draw()
    res.save(fname.split('.')[0]+'.jpg')


if __name__ == "__main__":
    main()
