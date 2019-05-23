# -*- coding: utf-8 -*-
from docx import Document
from processDoc import *
from preProc import *
from importlib import *
import copy
import re

def generateNEW():
    """
    old labels:
        identifier: e.g. '2.3.1'
        index: e.g. '2.3.1 ALM-0x12000001 进风口温度过高(Chassis,轻微告警)'
        explanation:  告警解释
        impact_on_sys: 对系统的影响
        causes: 可能原因
        solutions: 处理步骤
    NEW labels:
        identifier: e.g. '2.3.1'
        index: e.g. '2.3.1 ALM-0x12000001 进风口温度过高(Chassis,轻微告警)'
      * label: 故障标签 e.g. 'ALM-0x12000001'
      * phenomenon:  现象 e.g. '进风口温度过高'
      * faulty_body:  故障主体 e.g.  'Chassis'
      * degree:  故障等级 e.g.  '轻微告警'  **(sensor don't have such label)**
        explanation:  告警解释 e.g. '告警描述:', 'The air inlet temperature ( arg1 degrees C) exceeds the overtemperature threshold ( arg2 degrees C).'...
        impact_on_sys: 对系统的影响 e.g. '进风口温度过高会影响器件性能,导致设备运行不稳定。'
        causes: 可能原因 e.g.  'l 环境温度过高。', 'l 进风口被堵住。', ...
        solutions: 处理步骤 e.g. '步骤1 检查机房环境温度是否已超出设备运行环境要求的温度。' ...
    """
    faulty_part_records, sensor_records = getData()  # get data
    new_faulty = copy.deepcopy(faulty_part_records)
    new_sensor = copy.deepcopy(sensor_records)
    new_sensor = new_sensor[:-1]
    return generateNEWlabels(new_faulty), generateNEWlabels(new_sensor)

def generateNEWlabels(new_faulty):
    """
    generate new labels
    :para list 
    :return list with new labels
    """
    for i, faulty in enumerate(new_faulty):
        # generate label
        match = re.search(r"A[\S]+", str(faulty))
        new_faulty[i](label=match.group())
        # generate phenomenon
        s = " "
        match = re.search(r"[^(]+", s.join(str(faulty).split(' ')[2:]))
        new_faulty[i](phenomenon=match.group())
        # generate degree
        match = re.search(r".{2}告警", str(faulty))
        if match != None:
            new_faulty[i](degree=match.group())
        # generate faulty_body
        match = re.search(r"\([^ ,)]+", str(faulty))
        new_faulty[i](faulty_body=match.group()[1:])
        # refine explanation
        faulty.explanation = ''.join(faulty.explanation)
        # refine impact_on_sys
        for j, item in enumerate(faulty.impact_on_sys):
            if item[0] == 'l':
                if len(item) == 1:
                    faulty.impact_on_sys[j] = " "
                else:
                    faulty.impact_on_sys[j] = item[1:]
        faulty.impact_on_sys = ''.join(faulty.impact_on_sys)
        # refine causes
        for j, item in enumerate(faulty.causes):
            if item[0] == 'l':
                if len(item) == 1:
                    faulty.causes[j] = " "
                else:
                    faulty.causes[j] = item[1:]
        faulty.causes = ''.join(faulty.causes)
        # refine solutions
        for j, item in enumerate(faulty.solutions):
            if item[0] == 'l':
                if len(item) == 1:
                    faulty.solutions[j] = " "
                else:
                    faulty.solutions[j] = item[1:]
        faulty.solutions = '\n'.join(faulty.solutions)
        # generate alarm type
        match = re.search(r"\.\d{1,2}\.", faulty.identifier)
        if match.group() == '.3.':
            new_faulty[i](alarm_type='temperature')
        elif match.group() == '.4.':
            new_faulty[i](alarm_type='power')
        elif match.group() == '.5.':
            new_faulty[i](alarm_type='watchdog')
        elif match.group() == '.6.':
            new_faulty[i](alarm_type='subsystem')
        elif match.group() == '.7.':
            new_faulty[i](alarm_type='storage')
        elif match.group() == '.8.':
            new_faulty[i](alarm_type='fan')
        elif match.group() == '.9.':
            new_faulty[i](alarm_type='memory')
        elif match.group() == '.10.':
            new_faulty[i](alarm_type='others')
    return new_faulty