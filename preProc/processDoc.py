# -*- coding: utf-8 -*-
"""
Notes:
    Split docx into paragraphs using date as tag.
"""
import re
from docx import Document

class record(list):
    """
    record is a subclass of list that can accept additional attributes.
    It is able to be used just like a regular list.

    Usage:
    initialization:
    r = record(1,2,3,4, date='2018')
    r = record(1,2,3,4)(date='2018')
    r = record([1,2,3,4], date='2018')
    r = record({1,2,3,4}, date='2018')
    r = record(2**b for b in range(4), date='2018')
    r = record(2**b for b in range(4))(date='2018')
    r = record([2**b for b in range(4)], date='2018')
    r = record({2**b for b in range(4)}, date='2018')
    call procedure:
    r = record(1,2,3,4)
    r(date='2018')
    """
    def __new__(self, *args, **kwargs):
        return super(record, self).__new__(self, args, kwargs)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            list.__init__(self, args[0])
        else:
            list.__init__(self, args)
        self.__dict__.update(kwargs)

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

def procDoc(argv):
    """
    processDoc function.
    generate allRecord which is a list that contains customized data type record
    Usage:
    allRecord contains a list of record.
    allRecord[0]   # get the 0th record
    allRecord[0].date  # get the 0th record's date
    :param: argv
    :return: allRecord
    """
    document = Document(argv) # open document
    l = [ paragraph.text for paragraph in document.paragraphs ]
    allRecord = []
    for i in l:
        match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", i)
        if match is None:
            continue
        idate = match.group()  # get date
        r = record([i[len(idate)+1:]], date=idate)  # form one record
        allRecord.append(r)  # append to allRecord
    return allRecord

def parseDoc(partl):
    """
    parse document
    :para: partl: lines in document
    :return: records
	 labels:
	 explanation  告警解释
	 impact_on_sys 对系统的影响
	 causes 可能原因
	 solutions 处理步骤
    """
    records = []
    size = len(partl)
    i = 0
    match = None
    while i < size:
        index = ''
        while i < size:
            match = re.search(r"(\d{1}.\d{1,2}.\d{1,2})", partl[i])
            if match != None:
                break
            i += 1
        while i < size and partl[i] != '告警解释':
            index += partl[i]
            i += 1
        r = record([index])
        if match != None:
            r(identifier=match.group())
        else:
            r(identifier='')
        i += 1

        expl = []
        while i < size and partl[i] != '告警属性':
            expl.append(partl[i])
            i += 1
        r(explanation=expl)

        impact = []
        while i < size and partl[i] != '对系统的影响':
            i += 1
        i += 1
        while i < size and partl[i] != '可能原因':
            impact.append(partl[i])
            i += 1
        r(impact_on_sys=impact)
        i += 1

        coz = []
        while i < size and partl[i] != '处理步骤':
            coz.append(partl[i])
            i += 1
        r(causes=coz)
        i += 1

        steps = []
        while i < size and partl[i] != '----结束':
            steps.append(partl[i])
            i += 1
        r(solutions=steps)
        
        records.append(r)
    return records

