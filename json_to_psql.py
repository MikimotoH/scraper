#!/usr/bin/env python3
# coding: utf-8

import sys
import os
from datetime import datetime
import re
import psycopg2
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('json_file')
argparser.add_argument('--brand', dest='brand')
args = argparser.parse_args()
json_file = args.json_file
brand = args.brand
if brand is None:
    brand = os.path.splitext(os.path.basename(json_file))[0].title()
print('use brand="%(brand)s"'%locals())

try:
    db = psycopg2.connect(database='firmware',host='127.0.0.1',
            user='firmadyne', password='firmadyne')
    cur = db.cursor()
    with open(json_file, 'r') as fin:
        for line in fin:
            try:
                fw_md5 = re.search(r'"checksum": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                continue
            try:
                file_url = re.search(r'"url": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                continue
            try:
                fname = re.search(r'"path": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                continue
            try:
                model = re.search(r'"product": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                model=None
            try:
                desc = re.search(r'"description": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                desc=None
            try:
                fw_ver = re.search(r'"version": "(.*?)"', line, re.I).group(1)
            except AttributeError:
                fw_ver=None
            try:
                rel_date = re.search(r'"date": "(.*?)"', line, re.I).group(1)
                rel_date = datetime.strptime(rel_date, '%Y-%m-%d %H:%M:%S')
            except AttributeError:
                rel_date=None
            cur.execute("INSERT INTO image "
                    "(hash, filename, file_url, brand"+
                    (", model" if model else "") + (", version" if fw_ver else "") + 
                    (", rel_date" if rel_date else "") + (", description" if desc else "") + ") VALUES "+
                    "(%(fw_md5)s, %(fname)s, %(file_url)s, %(brand)s" + 
                    (", %(model)s" if model else "") + (", %(fw_ver)s" if fw_ver else "") +
                    (", %(rel_date)s" if rel_date else "") + (", %(desc)s" if desc else "") +
                    ") ON CONFLICT (hash) DO UPDATE SET filename=%(fname)s, file_url=%(file_url)s" +
                    ", brand=%(brand)s " +
                    (", model=%(model)s" if model else "") +
                    (", version=%(fw_ver)s" if fw_ver else "") +
                    (", rel_date=%(rel_date)s" if rel_date else "") +
                    (", description=%(desc)s" if desc else "") + 
                    " RETURNING id ", 
                    locals())
            db.commit()
            iid = cur.fetchone()
            iid = iid[0]
            print('UPSERT "%(fname)s", file_url="%(file_url)s", id=%(iid)d'%locals())
except Exception as ex:
    print(ex)
    import traceback
    traceback.print_exc()
finally:
    db.close()

