#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/14 14:46
# @Author  : TYQ
# @File    : vsfilecmp.py
# @Software: win10 python3

import os
import filecmp
from lib.readcfg import ReadCfg
from lib.Logger import logger
import difflib
from fnmatch import fnmatchcase as match
import time


def exclude_files(filename, excludes=[]):  # 是否属于不下载的文件判断
    # exclude 为具体配置，支持文件名配置及带目录的配置
    if filename in excludes:
        return True

    # exclude 为模糊配置，配置的话就不下载，跳过本次循环，进入下一循环
    for exclude in excludes:
        if match(filename, exclude):
            return True


def get_lines(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return f.readlines()
    except:
        try:
            with open(file, 'r', encoding='GBK') as f:
                return f.readlines()
        except:
            return 'open failed'


class vsfilecmp(object):
    def __init__(self, filepath=None):
        if filepath is None:
            self.cfg = ReadCfg().readcfg()
        else:
            self.cfg = ReadCfg().readcfg(filepath)

        self.mylog = logger("syslog" + time.strftime('%Y%m%d') + ".log")

    def compare(self):
        self.mylog.info("版本对比--开始！")
        home_dir = self.cfg["COMPARE"]["home_dir"]
        bak_name_feature = self.cfg["COMPARE"]["bak_name_feature"]
        ignore = self.cfg["COMPARE"]["ignore"]
        self.walk_path(home_dir, bak_name_feature, ignore)
        self.mylog.info("版本对比--结束！")

    def walk_path(self, path, bak_name_feature, ignore=[]):
        for maindir, subdir, file_name_list in os.walk(path):
            # print(maindir) #当前主目录
            # print(subdir) #当前主目录下的所有目录
            # print(file_name_list) #当前主目录下的所有文件
            for filename in file_name_list:
                apath = os.path.join(maindir, filename)  # 合并成一个完整路径
                # portion = os.path.splitext(apath)
                # ext = portion[1]  # 获取文件后缀 [0]获取的是除了文件名以外的内容

                if exclude_files(filename, ignore):
                    self.mylog.info("忽略差异文件：{}".format(apath))
                    continue
                # 合并bak文件
                if match(filename, bak_name_feature):
                    continue

                if bak_name_feature.startswith("*"):
                    bak_filename = filename + bak_name_feature.replace("*", "")
                if bak_name_feature.endswith("*"):
                    bak_filename = bak_name_feature.replace("*", "") + filename
                bak_apath = os.path.join(maindir, bak_filename)
                if not os.path.isfile(bak_apath):
                    self.mylog.info("文件不存在{}，跳过：".format(bak_apath))
                    continue

                left_lines = get_lines(apath)
                right_lines = get_lines(bak_apath)
                left_file = apath
                right_file = bak_apath

                if left_lines == 'open failed':
                    self.mylog.info("差异二进制文件：{file}".format(file=left_file))
                else:
                    self.mylog.info("差异文本文件：{file}".format(file=left_file))
                    context = difflib.context_diff(left_lines, right_lines, left_file, right_file,
                                                   n=self.cfg["COMPARE"]["context_diff.number"])
                    for item in context:
                        self.mylog.info("  {}".format(item.rstrip("\n")))
