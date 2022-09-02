import time

start_time = time.time()

import tabula
import yaml
import os

from decimal import Decimal

with open("SI_scrape_config.yaml", 'r', encoding='utf-8') as conf_f:
    config = yaml.safe_load(conf_f)

raw_report_date = config['report_month']
dir_path = config['report_pdf_fp'] + str(raw_report_date)


def tabula_kw_find(data, keywords):
    lines = []
    for i, line in enumerate(data):
        for kw in keywords:
            for c, cell in enumerate(line):
                if type(cell) == str:
                    str_index = cell.find(kw)
                    if str_index != -1:
                        lines.append(line[c:])
                        break
    return lines


def trim(lines):
    lines_temp = [l for l in lines if len(l) > 1]

    if len(lines_temp) == 1:
        return lines_temp[0]
    elif len(lines_temp) == 2 and lines[0] == lines[1]:
        return lines_temp[0]
    elif len(lines_temp) == 3 and lines[0] == lines[1] == lines[2]:
        return lines_temp[0]

    else:
        lines_temp_comb = []
        for l in lines_temp:
            lines_temp_comb += l
        lines_temp_comb_nodupe = list(dict.fromkeys(lines_temp_comb))
        return lines_temp_comb_nodupe


for file in os.listdir(dir_path + '//unread//'):
    if file == 'SKL_Q005.pdf' or True:
        tab_list = []

        fp = dir_path + '//unread//' + file
        try:
            dfs = tabula.read_pdf(fp, pages='all')
        except:
            pass
        print('------------------------------------------', file, '------------------------------------------')

        mng_lines = []
        aum_lines = []
        bank_lines = []

        report_output_aum = 'AUM NF'
        report_output_aum_multi = []
        # share_lines = []

        for table in dfs:

            data_arr = table.to_numpy().tolist()

            for i, line in enumerate(data_arr):
                for kw in config['aum_keywords']:
                    for c, cell in enumerate(line):
                        if type(cell) == str:
                            str_index_aum = cell.find(kw)
                            if str_index_aum != -1:
                                aum_lines.append(line[c:])
                                break
            if aum_lines == []:
                pass
                '''
                for i, line in enumerate(data_arr):
                    for kw in config['aum_keywords_1']:
                        for c, cell in enumerate(line):
                            if type(cell) == str:
                                str_index_aum = cell.find(kw)
                                if str_index_aum != -1:
                                    aum_lines.append(line[c:])
                                    break'''

        for i, l in enumerate(aum_lines):
            aum_lines[i] = [x for x in l if type(x) == str]
            temp_aum_line = []
            for j, x in enumerate(aum_lines[i]):
                temp_aum_line += x.split(' ')
            aum_lines[i] = temp_aum_line

        aum_lines = trim(aum_lines)
        aum_avoid = list('%')
        # aum_lines = [s for s in mng_lines if not any([dig in s for dig in digits])]
        aum_lines = [s for s in aum_lines if len(s) > 1]

        words_to_keep_postcurr_list = list('0123456789%.百佰千仟萬億兆MBK') + ['mil', 'bil']
        chars_to_keep_postcurr_list = list('0123456789%.百佰千仟萬億兆MBK') + list('mil'+'bil')
        
        chars_avoid = list('%年月日-')
        for i in range(7):
            chars_avoid += [str(int(str(raw_report_date)[:4]) - i) + '/']
            chars_avoid += ['/' + str(int(str(raw_report_date)[:4]) - i)]

        aum_lines_filt = []
        for i, s in enumerate(aum_lines):
            if any([char in s for char in words_to_keep_postcurr_list]):
                if not any([char in s for char in chars_avoid]):
                    aum_lines_filt.append(s)

        aum_lines_filt_char = []

        for i, s in enumerate(aum_lines_filt):
            aum_lines_filt[i] = s.replace('(', '').replace(')', '').replace('）', '').replace('（', '')

        for i, s in enumerate(aum_lines_filt):
            aum_lines_filt_char.append('')
            for j, char in enumerate(s):
                if char in chars_to_keep_postcurr_list:
                    aum_lines_filt_char[i] += char
        for i, s in enumerate(aum_lines_filt_char):
            if len(''.join(char for char in s if char == '.')) > 1:
                aum_lines_filt_char.remove(s)


        if len(aum_lines_filt_char) == 1:
            multiplier = 1
            if len(aum_lines_filt_char[0]) > 2:
                if all([char in list('.0123456789') for char in aum_lines_filt_char[0]]) and Decimal(
                        aum_lines_filt_char[0]) > 5000:
                    report_output_aum = Decimal(aum_lines_filt_char[0])

        elif len(aum_lines_filt_char) == 2:
            multiplier = 1
            for i, s in enumerate(aum_lines_filt_char):
                if s == "億":
                    multiplier = 100000000
                elif s == "千萬":
                    multiplier = 10000000
                elif s == "百萬" or s == "佰萬":
                    multiplier = 1000000
                elif s == "十萬" or s == "拾萬":
                    multiplier = 100000
                elif s == "萬":
                    multiplier = 10000
                elif s == "千" or s == "仟":
                    multiplier = 1000
                elif s == "百" or s == "佰":
                    multiplier = 100
                elif s == "十" or s == "拾":
                    multiplier = 10
                elif s == "M":
                    multiplier = 1000000
                elif s == "Mil" or s == 'mil' or s == 'MIL':
                    multiplier = 1000000
                elif s == "B":
                    multiplier = 1000000000
                elif s == "Bil" or s == 'bil' or s == 'BIL':
                    multiplier = 1000000000
                elif s == "k" or s == "K":
                    multiplier = 1000
                if len(''.join(char for char in aum_lines_filt_char[i - 1] if char == '.')) <= 1 and len(
                        aum_lines_filt_char[i - 1]) > 0:
                    if all([char in list('.0123456789') for char in aum_lines_filt_char[i - 1]]):
                        if Decimal(aum_lines_filt_char[i - 1]) * multiplier > 5000:
                            report_output_aum = Decimal(aum_lines_filt_char[i - 1]) * multiplier
                            break

        if report_output_aum == 'AUM NF':
            for i, s in enumerate(aum_lines_filt_char):
                if len(s) > 3:
                    if not aum_lines_filt_char[i][-1].isdigit() and not aum_lines_filt_char[i][-2].isdigit() and not \
                            aum_lines_filt_char[i][-3].isdigit() and all(
                        [char in list('.0123456789') for char in aum_lines_filt_char[i][:-3]]):
                        if aum_lines_filt_char[i][-3:] == "Mil" or aum_lines_filt_char[i][-3:] == 'mil' or \
                                aum_lines_filt_char[i][
                                -3:] == 'MIL':
                            multiplier = 1000000
                        elif aum_lines_filt_char[i][-3:] == "Bil" or aum_lines_filt_char[i][-3:] == 'bil' or \
                                aum_lines_filt_char[i][
                                -3:] == 'BIL':
                            multiplier = 1000000000
                        if multiplier != 1:
                            report_output_aum_multi.append(Decimal(aum_lines_filt_char[i][:-3]) * multiplier)

                    elif not aum_lines_filt_char[i][-1].isdigit() and not aum_lines_filt_char[i][-2].isdigit() and all(
                            [char in list('.0123456789') for char in aum_lines_filt_char[i][:-2]]):
                        if aum_lines_filt_char[i][-2:] == "千萬":
                            multiplier = 10000000
                        elif aum_lines_filt_char[i][-2:] == "百萬" or aum_lines_filt_char[i][-2:] == "佰萬":
                            multiplier = 1000000
                        elif aum_lines_filt_char[i][-2:] == "十萬" or aum_lines_filt_char[i][-2:] == "拾萬":
                            multiplier = 100000
                        if multiplier != 1:
                            report_output_aum_multi.append(Decimal(aum_lines_filt_char[i][:-2]) * multiplier)

                    elif not aum_lines_filt_char[i][-1].isdigit() and all(
                            [char in list('.0123456789') for char in aum_lines_filt_char[i][:-1]]):
                        if aum_lines_filt_char[i][-1] == "億":
                            multiplier = 100000000
                        elif aum_lines_filt_char[i][-1] == "萬":
                            multiplier = 10000
                        elif aum_lines_filt_char[i][-1] == "千" or aum_lines_filt_char[i][-1] == "仟":
                            multiplier = 1000
                        elif aum_lines_filt_char[i][-1] == "百" or aum_lines_filt_char[i][-1] == "佰":
                            multiplier = 100
                        elif aum_lines_filt_char[i][-1] == "十" or aum_lines_filt_char[i][-1] == "拾":
                            multiplier = 10
                        elif aum_lines_filt_char[i][-1] == "M":
                            multiplier = 1000000
                        elif aum_lines_filt_char[i][-1] == "B":
                            multiplier = 1000000000
                        elif aum_lines_filt_char[i][-1] == "k" or aum_lines_filt_char[i][-1] == "K":
                            multiplier = 1000
                        if multiplier != 1:
                            report_output_aum_multi.append(Decimal(aum_lines_filt_char[i][:-1]) * multiplier)

            for aum in report_output_aum_multi:
                if aum > 5000:
                    report_output_aum = aum

        '''
        for table in dfs:
            data_arr = table.to_numpy().tolist()
            for i, line in enumerate(data_arr):
    
                for kw in config['manager_keywords']:
                    for c, cell in enumerate(line):
                        if type(cell) == str:
                            str_index_mng = cell.find(kw)
                            if str_index_mng != -1:
                                mng_lines.append(line[c:])
                                break
    
        for i, l in enumerate(mng_lines):
            mng_lines[i] = [x for x in l if type(x) == str]
            temp_mng_line = []
            for j, x in enumerate(mng_lines[i]):
                temp_mng_line += x.split(' ')
            mng_lines[i] = temp_mng_line
    
        mng_lines = trim(mng_lines)
    
        digits = list('0123456789%')
        mng_lines = [s for s in mng_lines if not any([dig in s for dig in digits])]
        mng_lines = [s for s in mng_lines if len(s)>1]
    
        tw_lastnames_10 = list('陳林黃張李王吳劉蔡楊')
        tw_lastnames_50 = list('許鄭謝洪郭邱曾廖賴徐周葉蘇莊呂江何蕭羅高潘簡朱鍾游彭詹胡施沈余盧梁趙顏柯翁魏孫戴')
        tw_lastnames_200 = ['張簡', '歐陽'] + list('范方宋鄧杜傅侯曹薛丁卓阮馬tai董温唐藍石蔣古紀姚連馮歐程湯黄田康姜白汪鄒尤巫鐘'
                                                   '黎涂龔嚴韓袁金童陸夏柳凃邵錢伍倪溫于譚駱熊任甘秦顧毛章史官萬俞雷粘饒闕'
                                                   '凌崔尹孔辛武辜陶段龍韋葛池孟褚殷麥賀賈莫文管關向包丘梅')
        tw_lastnames_all = tw_lastnames_10 + tw_lastnames_50 + tw_lastnames_200
        output_mng = ''
        for name in mng_lines:
            if len(name) == 3 and name[0] in tw_lastnames_all:
                output_mng = name
                break
    
    
    
    
    
    
        for table in dfs:
            data_arr = table.to_numpy().tolist()
            for i, line in enumerate(data_arr):
                for kw in config['bank_keywords']:
                    for c, cell in enumerate(line):
                        if type(cell) == str:
                            str_index_bank = cell.find(kw)
                            if str_index_bank != -1:
                                bank_lines.append(line[c:])
                                break
    
        for i, l in enumerate(bank_lines):
            bank_lines[i] = [x for x in l if type(x) == str]
            temp_bank_line = []
            for j, x in enumerate(bank_lines[i]):
                temp_bank_line += x.split(' ')
            bank_lines[i] = temp_bank_line
    
        bank_lines = trim(bank_lines)
        bank_lines = [s for s in bank_lines if not any([dig in s for dig in digits])]
        bank_lines = [s for s in bank_lines if len(s) > 1]
    
        output_bank = ''
        for l in bank_lines:
            if ('銀行' in l or '商銀' in l or '企銀' in l or '機構' in l) and ('保管銀行' not in l and '保管機構' not in l):
                output_bank = l
                break
        '''

        '''
        for kw in config['shares_keywords']:
            if kw in str(line):
                print(line)
        '''

        print(aum_lines)
        # print(aum_lines_filt)
        print(aum_lines_filt_char)
        print(report_output_aum)

        # print(output_mng)
        # print(output_bank)

print("\n\n time elapsed: {:.2f}s".format(time.time() - start_time))
