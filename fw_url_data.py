#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg2
import re
from os import path
import json
import sys
import traceback
import pdb

# iid_min, iid_max = sys.argv[1], sys.argv[2]
json_filename = sys.argv[1]

try:
    conn = psycopg2.connect(host='127.0.0.1', user='firmadyne', password='firmadyne', database='firmware')
    cur = conn.cursor()
    def get_filename(_id):
        cur.execute("SELECT filename FROM image WHERE id=%s", (_id,))
        return cur.fetchone()[0]

    with open(json_filename) as fin:
        lines = fin.read().splitlines()

    def get_att(l,att):
        try:
            return re.search(r'"%s": "(.*?)"'%att,l).group(1)
        except AttributeError:
            return None
    for i,l in enumerate(lines[1:-1], 1):
        filepath = get_att(l, 'path')
        if not filepath:
            print('no filepath in line %d'%i)
            continue
        product = get_att(l, 'product')
        version = get_att(l, 'version')
        url = get_att(l, 'url')
        filename = path.split(filepath)[-1]
        try:
            try:
                cur.execute("SELECT id FROM image WHERE filename = %s", (filename,))
                iid = cur.fetchone()[0]
            except TypeError:
                print('"%s" is not found in database'%filename)
                continue
            print("line=%d, iid=%s file='%s', model='%s', version='%s' "%(i,iid,filename,product,version))
            cur.execute('UPDATE image SET (model,version,file_url)=(%s,%s,%s) WHERE id=%s',
                    (product, version, url,iid) )
            conn.commit()
        except Exception as ex:
            print(ex)
            pdb.set_trace()
            traceback.print_exc()
finally:
    conn.close()

