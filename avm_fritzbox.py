from urllib import request
from os import path
import sys
import re
import ftputil
import pdb

def getext(fname):
    return path.splitext(fname)[-1]

localstor='avm'
import os
os.makedirs(localstor, exist_ok=True)
try:
    with ftputil.FTPHost('ftp.avm.de', 'anonymous', '') as host:
        host.keep_alive()
        for root, dirs, files in host.walk('fritz.box'):
            if not any(_ for _ in files if getext(_)=='.image'):
                continue
            files.sort(key=lambda x:getext(x))
            fw_image=None
            for f in files:
                ext = getext(f)
                if ext =='.image':
                    fw_image = f
                    print('download %s/%s'%(root,f) )
                    if path.exists(path.join(localstor, f)):
                        print('bypass file: %s'%f)
                        continue
                    host.download(path.join(root, f), path.join(localstor, f))
                elif f == 'info.txt':
                    assert fw_image is not None
                    host.download(path.join(root, f), path.join(localstor, fw_image+'.'+ f))
except Exception as ex:
    import traceback
    pdb.set_trace()
    traceback.print_exc()
