import os
import numpy as np
# import tensorflow as tf
import json
import re
from multiprocessing import Pool
from collections import namedtuple
from PIL import Image
import json


MAX_SIZE = 500
root_dir = os.path.dirname(__file__)
SerializeInfo = namedtuple('SerializeInfo', ['input_file', 'input_json', 'output_prefix'])

def serialize_image(info):
    try:
        img = Image.open(info.input_file)
        img = img.resize((300, 300), Image.ANTIALIAS)
        img.save(f'{info.output_prefix}.jpg', "JPEG")
        os.rename(info.input_json, f'{info.output_prefix}.json')
        os.remove(info.input_file)
    except IOError as e:
        print(e)
        print("Could not resize image")
        print(info.input_json)
        print(f'{info.output_prefix}.json')
    return None

def serialize_images(input_dir, output_dir):
    """ meta filename = 'meta.json' """

    odirs = os.listdir(output_dir)
    odirs = list(filter(lambda d: d[:3] == 'tff', odirs))
    odirs.sort()

    if len(odirs) == 0:
        odir = os.path.join(output_dir, 'tff0001')
        os.makedirs(odir)
    else:
        odir = os.path.join(output_dir, odirs[-1])

    if not os.path.exists(os.path.join(odir, 'meta.json')):
        with open(os.path.join(odir, 'meta.json'), 'w') as f:
            json.dump({'size': 0}, f)

    fnames = list(os.listdir(input_dir))
    infos = []
    for fname in fnames:
        if fname[-4:] == '.mp4':
            os.remove(os.path.join(input_dir, fname))
        elif fname[-4:] == '.jpg':
            test_search = re.search('\d+.jpg', fname)
            if test_search:
                os.remove(os.path.join(input_dir, fname))
                continue
            else:
                fname_prefix = fname[:-4]

            # print(fname)
            with open(os.path.join(odir, 'meta.json'), 'r') as f:
                csize = json.load(f)['size']
            if csize >= MAX_SIZE:
                current_id = int(odir[-4:].lstrip('0'))
                fid = "%04d" % (current_id + 1)
                odir = os.path.join(output_dir, f'tff{fid}')
                if not os.path.exists(odir):
                    os.makedirs(odir)
                if not os.path.exists(os.path.join(odir, 'meta.json')):
                    with open(os.path.join(odir, 'meta.json'), 'w') as f:
                        json.dump({'size': 0}, f)
                with open(os.path.join(odir, 'meta.json')) as f:
                    csize = json.load(f)['size']

            csize += 1
            jpg_prefix = "%04d" % csize
            infos.append(SerializeInfo(
                os.path.join(input_dir, fname),
                os.path.join(input_dir, f'{fname_prefix}.json'),
                os.path.join(odir, f'{jpg_prefix}')))

            with open(os.path.join(odir, 'meta.json'), 'w') as f:
                json.dump({'size': csize}, f)

    pool = Pool(4)
    pool.map(serialize_image, infos)

serialize_images(os.path.join(root_dir, 'selfies'), os.path.join(root_dir, 'data'))
