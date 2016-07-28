#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg2
import os, sys
from os import path
from glob import glob
from glob import iglob 
from datetime import datetime
import re

lang2cc = { 
        'german': 'de',
        'deutsch': 'de',
        'english': 'en',
        'englisch': 'en',
        'french': 'fr',
        'französisch': 'fr',
        'italian': 'it',
        'italienisch': 'it',
        'polish':'pl',
        'spanish':'es',
        'spanisch': 'es',
        }

def read_info_txt(fname):
    with open(fname, mode='r', encoding='latin2', errors='ignore') as fin:
        lines = fin.read().splitlines()
    product=''
    version=''
    rel_date=None
    annex=''
    lang=''
    for l in lines:
        l = l.strip()
        if not l: 
            continue
        if l.startswith('__'):
            break
        if not l[0].isalpha():
            continue
        # if not re.match(r'\s*[\w]+[\w\-]*[\w]+\s*:\s+\w+', l):
        #    continue
        if ':' not in l:
            continue

        try:
            aname, avalue  = l.split(':')
        except ValueError:
            try:
                aname,_,avalue = l.split(':')
            except ValueError:
                continue
        aname=aname.lower().strip()
        avalue = avalue.strip(" \t\n.-").replace('-', ' ')
        if not avalue:
            continue
        if aname in ['product', 'produkt']:
            product = avalue
        elif aname in ['version']:
            version = avalue.lstrip('0')
        elif aname in ['release date', 'release datum']:
            avalue = re.sub(r'\.|-', '/', avalue)
            rel_date = datetime.strptime(avalue, '%d/%m/%Y')
        elif aname in ['language', 'sprache']:
            lang = ','.join(lang2cc[_.strip().lower()] for _ in avalue.split(',') if _.strip())
        elif aname in ['annex']:
            annex = avalue
        else:
            # print('unknown attribute name:"%s"'%aname)
            continue
        if product and version and rel_date:
            break
    assert product and version
    
    if lang:
        version = version + ' Language:'+lang
    elif annex:
        version = version + ' Annex:'+annex
    elif lang and annex:
        version = version + ' Language:'+lang + ' Annex:'+annex
    return {'product':product, 'version':version, 'rel_date':rel_date}

    
try:
    read_info_txt('avm/FRITZ.Box_Fon_WLAN_7113.de-en-es-it-fr.90.04.86.image.info.txt')
    conn = psycopg2.connect(database="firmware", user="firmadyne", password="firmadyne", host="127.0.0.1")
    cur = conn.cursor()
    brand_id=1
    for image_file in glob('avm/*.image'):
        if not path.exists(image_file + '.info.txt'):
            print("Not exist %s.info.txt"%image_file)
            continue
        print('image_file: ', image_file)
        pvd = read_info_txt(image_file+'.info.txt')
        print(pvd)
        cur.execute("INSERT INTO image (filename, brand, model, version, rel_date, brand_id) VALUES (%s,%s,%s,%s,%s,%s) ", 
               (image_file, 'Avm', pvd['product'], pvd['version'], pvd['rel_date'], brand_id))
    conn.commit()

finally:
    conn.close()

