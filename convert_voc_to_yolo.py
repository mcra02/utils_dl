import glob
import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir, getcwd
from os.path import join
import shutil

dirs = ['train', 'test']
classes = ['erizo-negro', 'erizo-rojo']

def findImagesInDir(base_dir):
    list_images = []

    for file_name in glob.glob(base_dir + '/*.jpg'):
        list_images.append(file_name)

    return list_images

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_dataset_annotation(base_dir, output_dir, image_path, output_images_dir, trash_output_dir):
    basename = os.path.basename(image_path)
    basename_no_ext = os.path.splitext(basename)[0]

    in_file = open(base_dir + '/' + basename_no_ext + '.xml')
    out_file = open(output_dir + '/' + basename_no_ext + '.txt', 'w')

    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    erne = 0
    erro = 0

    count = 0

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        if cls == 'erizo-negro':
          erne += 1
        if cls == 'erizo-rojo':
          erro += 1
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

        count += 1

    if count == 0:
      print('***** ' + basename_no_ext)
      shutil.copy(base_dir + '/' + basename_no_ext + '.jpg', trash_output_dir + basename_no_ext + '.jpg')
      shutil.copy(base_dir + '/' + basename_no_ext + '.xml', trash_output_dir + basename_no_ext + '.xml')

    shutil.copy(base_dir + '/' + basename_no_ext + '.jpg', output_images_dir + '/' + basename_no_ext + '.jpg')

    return erne, erro

cwd = getcwd()

for base_dir in dirs:
    full_base_dir = cwd + '/' + base_dir

    full_output_dir_labels = cwd + '/seaurchin/labels/' + base_dir
    full_output_dir_images = cwd + '/seaurchin/images/' + base_dir

    trash_output_dir = cwd + '/seaurchin/trash/'

    if not os.path.exists(full_output_dir_labels):
        os.makedirs(full_output_dir_labels)
    if not os.path.exists(full_output_dir_images):
        os.makedirs(full_output_dir_images)
    if not os.path.exists(trash_output_dir):
        os.makedirs(trash_output_dir)

    image_paths = findImagesInDir(full_base_dir)
    list_file = open(full_base_dir + '.txt', 'w')

    erne = 0
    erro = 0

    for image_path in image_paths:
        list_file.write(image_path + '\n')
        ne, ro = convert_dataset_annotation(full_base_dir, full_output_dir_labels, image_path, full_output_dir_images, trash_output_dir)
        erne += ne
        erro += ro

    list_file.close()

    print("Mapping finished: " + base_dir)
    print("Seaurchin red: " + str(erro))
    print("Seaurchin black: " + str(erne))