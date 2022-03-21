#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Создает синтетическую базу обучения
# для набора объектов из obj мешей
# неокрашенные металлические объекты ( оцинковка )

# the tool for synthetic coco-style database generation
# zincum _style metal details
# NSTU Novosibirsk Russia
# @Authors: Alex Kolker (a.kolker@corp.nstu.ru) and Sonya Oshepkova
# Novosibirsk 2020
#The tool was created with support of RFBR 18-58-76003 project ( ERA.Net RUS Plus st2017-294 EU project)
#The licence limitations: CC BY-NC 4.0 license
#@AUTHORS Alex Kolker; Zhanna Pershina; Sonya Oshepkova @NSTU Novosibirsk 2020 @If you were used it please cite us.


import configparser
import copy
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

import cv2
import numpy as np
from jinja2 import Template

# позиции источника света
# the light source
# light_pos = [[0, 0, 0], [0, -20, 0], [0, 20, 0], [-20, -20, 0], [20, 20, 0]]
light_pos = []
# стопка будет определятся порядком- последний - самый верхний
# the batch of details. The first is lower
# detail_nameset = [['./input/bolt.obj', 'BOLT', 0], ['./input/bow1.obj', 'bow',1], ['./input/lanya.obj', 'SKREW', 2]]
detail_nameset = []

num = 0
learn_dataset = None
GlobalScale = 1


def make_transform(alpha, beta, gamma, Dx=0., Dy=0., Dz=0.):
    flip_transform_x = [[1, 0, 0, 0],
                        [0, np.cos(alpha), -np.sin(alpha), 0],
                        [0, np.sin(alpha), np.cos(alpha), 0],
                        [0, 0, 0, 1]]

    flip_transform_y = [[np.cos(beta), 0, np.sin(beta), 0],
                        [0, 1, 0, 0],
                        [-np.sin(beta), 0, np.cos(beta), 0],
                        [0, 0, 0, 1]]

    flip_transform_z = [[np.cos(gamma), -np.sin(gamma), 0, 0],
                        [np.sin(gamma), np.cos(gamma), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]]

    flip_tot = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

    flip_tot = np.dot(flip_tot, flip_transform_y)
    flip_tot = np.dot(flip_tot, flip_transform_x)
    flip_tot = np.dot(flip_tot, flip_transform_z)
    return flip_tot


def collect_final(input_folder="./result/annotations", output_file="./result/output.json"):
    merged_dict = defaultdict(list)
    for f in glob.glob(str(input_folder) + "/*.json"):
        with open(f) as infile:
            result = json.load(infile)
        for key, value in result.items():
            for i in range(len(value)):
                merged_dict[key].append(value[i])

    with open(output_file, "w") as output_file:
        json.dump(merged_dict, output_file)


def reformat_detail(inidx, infile):
    outfile = "./povray2/detail{}_POV_geom_.inc".format(inidx)

    name_of_mesh = "detail{}_unnamed_material_".format(inidx)

    out = open(outfile, mode="w")
    out.write("//automatical generated inc file\n\r")
    out.write("#declare {} = mesh2{{\n\r".format(name_of_mesh))
    xx = []
    yy = []
    zz = []
    triangle = []
    with open(infile) as objfile:
        for lines in objfile:
            if lines[0] == 'v':
                trio = lines.rstrip().split(' ')
                xx.append(float(trio[1]))
                yy.append(float(trio[2]))
                zz.append(float(trio[3]))

            if lines[0] == 'f':
                trio = lines.rstrip().split(' ')
                if lines.find('/') > 0:
                    for idx in range(1, 4):
                        trio[idx] = trio[idx][0:(trio[idx].find('/'))]
                triangle.append("<{},{},{}>,\n".format(int(trio[1]) - 1, int(trio[2]) - 1, int(trio[3]) - 1))

    out.write("vertex_vectors{{\n{},\n".format(len(xx)))
    cx = (max(xx) + min(xx)) / 2
    cy = (max(yy) + min(yy)) / 2
    cz = (max(zz) + min(zz)) / 2

    # с масштаб при обработке детали
    scale = 1

    for idx in range(0, len(xx)):
        out.write("<{},{},{}>,\n".format((xx[idx] - cx) * scale, (yy[idx] - cy) * scale, (zz[idx] - cz) * scale))
    out.write("}}\n\rface_indices{{\n{},\n".format(len(triangle)))
    for strings in triangle:
        out.write(strings)

    out.write("}\n\rinside_vector <0,0,1> }\n\n")
    out.write("#declare detail{}".format(inidx) + "=object{" + "detail{}".format(
        inidx) + "_unnamed_material_  hollow } \n #version Temp_version;")

    out.close()
    return min(xx) - cx, max(xx) - cx, min(yy) - cy, max(yy) - cy, min(zz) - cz, max(zz) - cz


def create_json(detail_id=0, detail_name=None,
                file_name=None, file_path=None, width=0, height=0,
                image_id=0, area=0, segmentation=None, bbox=None, mask=None):
    merged_dict = {"categories": [{"id": int, "name": str, "color": str}],
                   "images": [{"id": int, "width": int, "height": int, "file_name": str, "path": str}],
                   "annotations": [{"id": int, "image_id": int, "category_id": int, "width": int, "height": int,
                                    "area": int, "segmentation": [], "mask": [], "bbox": [], "color": str,
                                    "iscrowd": int}]}

    merged_dict["categories"][0]["id"] = detail_id
    merged_dict["categories"][0]["name"] = detail_name
    merged_dict["categories"][0]["color"] = "#e97911"
    merged_dict["images"][0]["id"] = image_id
    merged_dict["images"][0]["width"] = width
    merged_dict["images"][0]["height"] = height
    merged_dict["images"][0]["file_name"] = file_name
    merged_dict["images"][0]["path"] = file_path
    merged_dict["annotations"][0]["id"] = image_id
    merged_dict["annotations"][0]["image_id"] = image_id
    merged_dict["annotations"][0]["category_id"] = detail_id
    merged_dict["annotations"][0]["width"] = width
    merged_dict["annotations"][0]["height"] = height
    merged_dict["annotations"][0]["area"] = area
    merged_dict["annotations"][0]["segmentation"] = segmentation
    merged_dict["annotations"][0]["mask"] = mask
    merged_dict["annotations"][0]["bbox"] = bbox
    merged_dict["annotations"][0]["color"] = "#e97911"
    merged_dict["annotations"][0]["iscrowd"] = 0

    return merged_dict


def np2pov(row):
    return "<{},{},{},{}>".format(row[0], row[1], row[2], row[3])


def main():
    stopN = 1
    if len(sys.argv) < 7:
        stopN = 2
        startnum = 0
        print(
            "no command string found: doing default: 1 set with detailstartnum = 1, do not clear folders, no_aruco, yes-overlap, config=genpovray.ini")
        print(
            "usage: genpovray.py {Img number:int} {Start_num:int} {clear_folders:0/1} {aruco:0/1} {overlap: 1/1} {configfile}")
        configname = './genpovray.ini'
        aruco = 0
        overlap = 1
    else:
        stopN = int(sys.argv[1])
        startnum = int(sys.argv[2])
        if int(sys.argv[3]) == 1:
            for file in glob.glob('./result/images/*.png'):
                os.remove(file)
            for file in glob.glob('./result/annotations/*.json'):
                os.remove(file)
        aruco = sys.argv[4]
        overlap = sys.argv[5]
        configname = sys.argv[6]

    stopN += 1
    config = configparser.ConfigParser()
    if not config:
        print("No Config File")
        exit(0)
    config.read(configname)

    global num
    global detail_nameset
    global light_pos
    global GlobalScale

    print("start processing objects:")
    print(str(config['DEFAULT']['OBJECTS']))
    print("with light")
    print(str(config['DEFAULT']['LIGHT']))

    detail_nameset = json.loads(str(config['DEFAULT']['OBJECTS']))
    light_pos = json.loads(str(config['DEFAULT']['LIGHT']))
    GlobalScale = float(config['DEFAULT']['SCALE'])

    np.random.seed()

    details_coordset = []

    details_coordset.append(([0, 0, 0, 220, 140, -120]))
    details_coordset.append(([0, 0, 0, -220, -110, -120]))
    details_coordset.append(([0, 0, 0, 0, 0, -120]))

    # тут bbox деталей, чтобы при рандомизации не попасть на прекрытия
    # bound boxes for avoid overlapping
    bbox_set = []
    # переформатируем все детали из набора путем центрирования и преобразуем их в inc
    # reformat details for inc
    incl_str = ""

    batch = 0
    for didx in range(0, len(detail_nameset)):
        # деталь возвращает bbox для генерации перекрытий и мы их складываем в bbox_set
        # bbox being stored to bbox_set
        bbox_set.append(reformat_detail(didx, detail_nameset[didx][0]))
        incl_str = incl_str + "#include \"detail{}_POV_geom_.inc\" \n".format(didx)
        details_coordset[didx][5] = batch
        batch += bbox_set[didx][5] - bbox_set[didx][4]
    # чтение шаблона общих данных: свет,сцена итд
    # common povray template item
    templ1 = open('./povray2/common_POV_scene.pov.templ').read()
    # чтение шаблона частных данных деталей - можно добавлять таких несколько, чтобы создать сцену из нескольких деталей
    # detail and material specific povray template item
    templ2 = open('./povray2/detail_POV_scene.pov.templ').read()
    if aruco == 1:
        templ3 = open('./povray2/aruco.pov.templ').read()
        templaruco = Template(templ3)
    # отрендерели шаблоны
    # teplate processing
    templatecommon = Template(templ1)
    templatedetail = Template(templ2)

    print(bbox_set)
    camera_position = 1000

    rotcamera = 0
    for datacase in range(1, stopN):
        treshset = []
        #        rotcamera += 10
        Cscale = 150
        if overlap == 1:
            camroll, campitch, camyaw, camtransx, camtransy, camtransz = [0, np.random.randint(-45, 45, 1)[0], 0, 0, 0,
                                                                          camera_position +
                                                                          np.random.randint(-int(camera_position / 6),
                                                                                            int(camera_position / 2),
                                                                                            1)[0]]
        else:
            camroll, campitch, camyaw, camtransx, camtransy, camtransz = [0, 0, rotcamera, 0, 0, camera_position]

        lyaw = 0

        # тут будут храниться контуры,которые мы наработали для сцены
        # array for conturs for annotation
        detailcontours = []
        # и маски*
        # and masks ( for future using )
        treshset = []
        # РАНДОМИЗАЦИЯ
        # RANDOMIZATION
        canvasize = 704
        fixed_set = [[canvasize / 5, -canvasize / 5],
                     [-canvasize / 5, canvasize / 5],
                     [0, 0],
                     [canvasize / 6, canvasize / 6]]

        for detailnum in range(0, len(detail_nameset)):
            # 1 рандомизация вращения
            # 1 rotation randomization
            details_coordset[detailnum][2] = np.random.randint(-180, 180, 1)[0]
            details_coordset[detailnum][1] = np.random.randint(-45, 45, 1)[0]
            details_coordset[detailnum][0] = np.random.randint(-45, 45, 1)[0]
            details_coordset[detailnum][5] = np.random.randint(-120, 120, 1)[0]
            # 2 рандомизация сдвигов по высоте ширине.
            # 2 shift randomization
            if overlap == 1:
                details_coordset[detailnum][3] = \
                    np.random.randint(-int((bbox_set[detailnum][1] - bbox_set[detailnum][0]) / 2),
                                      int((bbox_set[detailnum][1] - bbox_set[detailnum][0]) / 2), 1)[0]
                details_coordset[detailnum][4] = \
                    np.random.randint(-int((bbox_set[detailnum][3] - bbox_set[detailnum][2]) / 2),
                                      int((bbox_set[detailnum][3] - bbox_set[detailnum][2]) / 2), 1)[0]

        #  Собираем детали по отдельности масками и пишем их с именами с 0 до len()
        #  Индивидуальный признак для возможности параллельного запуска нескольких задач
        # detail image mask generation

        indidx = ""
        for detailnum in range(0, len(detail_nameset)):
            individual_det_povname = './povray2/detail{}_POV_scene.pov'.format(detailnum)
            roll, pitch, yaw, x_trans, y_trans, z_trans = details_coordset[detailnum]
            matrix = make_transform(roll / 180. * np.pi, pitch / 180. * np.pi, yaw / 180. * np.pi)

            print(matrix[0])
            indidx += str(int(x_trans)) + str(int(y_trans)) + str(int(z_trans)) + str(roll) + str(pitch) + str(
                yaw) + str(np.random.randint(0, 65535, 1)[0])
            # сборщик света и камеры для индивидуальной детали
            # camera and light for each detail
            open(individual_det_povname, mode='w').write(templatecommon.render(lroll=0, lpitch=0, lyaw=lyaw,
                                                                               camroll=camroll, campitch=campitch,
                                                                               camyaw=camyaw,
                                                                               camtransx=camtransx, camtransy=camtransy,
                                                                               camtransz=camtransz,
                                                                               geometry_include=incl_str,
                                                                               ablight_factor=100))

            # сборщик тела детали для индивидуальной
            # body for each detail
            open(individual_det_povname, mode='a').write(templatedetail.render(A=np2pov(matrix[0]), B=np2pov(matrix[1]),
                                                                               C=np2pov(matrix[2]), D=np2pov(matrix[3]),
                                                                               Ccolor='Black', Cscale=100,
                                                                               x_trans=x_trans, y_trans=y_trans,
                                                                               z_trans=z_trans,
                                                                               detail_num=detailnum))

            # контуры отдельных деталей не меняются в зависимости от направления освещения,поэтому мы отрисовываем их по
            # отдельности и рассчитываем контуры для coco датасета
            # detail conturs are same for all light position, we can do in once for each set
            runstring = 'detail{}_POV_scene.pov +H704 +W704 +O../result/{}.png Display=off Quality=5'.format(detailnum,
                                                                                                             detailnum)
            subprocess.call(["povray", runstring], cwd='./povray2')

        # теперь поехали по деталям -
        # details processing

        for detailnum in range(0, len(detail_nameset)):
            image_ = cv2.imread("./result/{}.png".format(detailnum), 3)
            imgray_ = cv2.cvtColor(image_, cv2.COLOR_BGR2GRAY)
            # обработка перекрытий
            # overlapping processing
            if detailnum < len(detail_nameset) - 1:
                for maskidx in range(detailnum + 1, len(detail_nameset)):
                    mask_ = cv2.imread("./result/{}.png".format(maskidx), 3)
                    mask_ = cv2.cvtColor(mask_, cv2.COLOR_BGR2GRAY)
                    _, mask_ = cv2.threshold(mask_, thresh=180, maxval=255, type=cv2.THRESH_BINARY)
                    mask_ = cv2.bitwise_not(mask_)
                    imgray_ = cv2.bitwise_and(image_, image_, mask=mask_)
                    cv2.imwrite("./result/{}_{}.png".format(detailnum, maskidx), mask_)
                gray = cv2.cvtColor(imgray_, cv2.COLOR_BGR2GRAY)
            else:
                gray = copy.copy(imgray_)

            cv2.imwrite("./result/{}_res.png".format(detailnum), imgray_)

            ret, thresh_ = cv2.threshold(gray, 0, 1, 0)
            contours, hierarchy = cv2.findContours(thresh_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contours) > 0:

                # контуры накапливаем в массиве detailcontours
                # conturs for annotation
                detailcontours.append(contours)
                img = np.zeros((704, 704, 3), np.uint8)
                img = cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
                print(np.asarray(contours).shape)
                cv2.imwrite("./result/{}_contours.png".format(detailnum), img)
                # detail boxes for correct bbox and for mask  in future

                treshset.append(thresh_)

            else:
                detailcontours.append([])
                treshset.append([])

        # цикл по позициям источника освещения
        # each light source processing
        for lroll, lpitch, lyaw in light_pos:
            ccolorgray = 'White*0.05'
            # сборщик света и камеры
            # light and camera
            heapname = './povray2/heap_POV_scene.pov'
            open(heapname, mode='w').write(templatecommon.render(lroll=lroll, lpitch=lpitch, lyaw=lyaw,
                                                                 camroll=camroll, campitch=campitch, camyaw=camyaw,
                                                                 camtransx=camtransx, camtransy=camtransy,
                                                                 camtransz=camtransz, geometry_include=incl_str,
                                                                 ablight_factor=0))

            outname = "datacase_{:d}_sh{:s}_l{:d}_{:d}_{:d}.png".format(datacase + startnum, indidx, lroll, lpitch,
                                                                        lyaw)

            # сборщик всех тел деталей
            # all batch of details
            for detailnum in range(0, len(detail_nameset)):
                roll, pitch, yaw, x_trans, y_trans, z_trans = details_coordset[detailnum]
                matrix = make_transform(roll / 180. * np.pi, pitch / 180. * np.pi, yaw / 180. * np.pi)
                np.savetxt("./result/images/" + outname + str(detail_nameset[detailnum][1]) + ".txt", matrix)
                #                open("./result/images/"+outname+str(detail_nameset[detailnum])+".txt",mode='w').write(matrix)

                open(heapname, mode='a').write(
                    templatedetail.render(A=np2pov(matrix[0]), B=np2pov(matrix[1]),
                                          C=np2pov(matrix[2]), D=np2pov(matrix[3]),
                                          lroll=lroll, lpitch1=lpitch,
                                          lyaw=lyaw, Ccolor=ccolorgray,
                                          Cscale=Cscale,
                                          x_trans=x_trans, y_trans=y_trans,
                                          z_trans=z_trans,
                                          ablight_factor=0, detail_num=detailnum))
            if aruco == 1:
                # сборка аруки
                open(heapname, mode='a').write(
                    templaruco.render())
            # отрисовка кучи деталей
            # all bodyes
            subprocess.call(["povray",
                             "heap_POV_scene.pov +H704 +W704 +O../result/images/result.png Display=off Quality=9 Output_Alpha=True"],
                            cwd='./povray2')
            # случайный фон
            # random background - commented
            #            img = np.random.randint(0,255,(704,704,3)).astype(np.uint8)
            #            kernel = np.ones((3,3),np.float32)/9.
            #            dst = cv2.filter2D(img,-1,kernel)
            #            cv2.imwrite("./result/images/random.png",dst)
            #            result = cv2.imread("./result/images/result.png")
            #            st = cv2.add(result,dst)
            #            cv2.imwrite(outname, dst)
            # объединение случайного фона
            # random background
            #            str_call = "./result.images/random.png ./result/images/result.png -background black -gravity center -flatten "+outname
            os.rename("./result/images/result.png", "./result/images/{}".format(outname))

        # Аннотируем картинку
        # Annotation section

        for idxl in range(0, len(light_pos)):
            lroll, lpitch, lyaw = light_pos[idxl]
            for detailnum in range(0, len(detail_nameset)):
                num += 1
                resultcc = []
                for c in detailcontours[detailnum]:
                    cc = c.reshape(-1, 2).reshape(1, -1)
                    cc.tolist()

                    if len(cc[0]) > 5:
                        resultcc.append(cc[0].tolist())

                #                print()
                # Маски площади и ограничивающий прямогугольник
                # BBoxes and masks
                points = cv2.findNonZero(treshset[detailnum])
                outname = "datacase_{:d}_sh{:s}_l{:d}_{:d}_{:d}.png".format(datacase + startnum, indidx, lroll, lpitch,
                                                                            lyaw)
                annot_ex = create_json(detail_id=detail_nameset[detailnum][2],
                                       detail_name=detail_nameset[detailnum][1],
                                       file_name=outname,
                                       file_path="./result/images",
                                       width=704,
                                       height=704,
                                       image_id=datacase * len(light_pos) + startnum + idxl,
                                       area=int(cv2.contourArea(detailcontours[detailnum][0])),
                                       bbox=cv2.boundingRect(points),
                                       segmentation=resultcc,
                                       mask=treshset[detailnum].tolist())

                with open("./result/annotations/{}_{}.json".format(datacase * len(light_pos) + startnum + idxl,
                                                                   detailnum), 'w') as f:
                    json.dump(annot_ex, f)
        collect_final()


#        for file in glob.glob('./result/*.png'):
#            os.remove(file)

if __name__ == "__main__":
    main()
