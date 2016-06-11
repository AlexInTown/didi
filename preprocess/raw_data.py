# -*- coding:utf-8 -*-
__author__ = 'alexintown'

import os
import re
import pandas as pd
import cPickle as cp
import numpy as np
from collections import defaultdict
from utils.config_utils import Config



def load_part_data(path, file_pattern, columns):
    """
    Load data like order, traffic, weather with daily parts.

    :param path: absolute path of the dir
    :param file_pattern: file pattern of files in the dir
    :param columns: columns to read.
    :return: data frame of the files
    """
    reg = re.compile(file_pattern)
    df_list = list()
    for fname in os.listdir(path):
        match = reg.match(fname)
        fname = os.path.join(path, fname)
        if match:
            df =  pd.read_csv(fname,sep='\t', header=None, names=columns)
            df_list.append((match.group(1),df))
    df_list = sorted(df_list, key=lambda x: x[0])
    res = pd.concat([x[1] for x in df_list])
    return res

def load_order_data(path):
    """
    Load order data.

    :param path:  root path of the dataset.
    :return: data frame of order data
    """
    path = os.path.join(path, 'order_data')
    file_pattern = 'order_data_(.*)'
    columns = ['order_id', 'driver_id', 'passenger_id', 'start_district', 'dest_district', 'price', 'time']
    df = load_part_data(path, file_pattern, columns)
    return df

def load_traffic_data(path):
    """
    Load traffic data.

    :param path:  root path of the dataset.
    :return: data frame of traffic data
    """
    path = os.path.join(path, 'traffic_data')
    file_pattern = 'traffic_data_(.*)'
    columns = ['district_hash', 'l1', 'l2', 'l3', 'l4', 'time']
    df = load_part_data(path, file_pattern, columns)
    return df


def load_weather_data(path):
    """
    Load weather data.

    :param path:  root path of the dataset.
    :return: data frame of weather data
    """
    path = os.path.join(path, 'weather_data')
    file_pattern = 'weather_data_(.*)'
    columns = ['time', 'weather', 'temperature', 'pm2.5']
    df = load_part_data(path, file_pattern, columns)
    return df

def load_poi_data(path):
    """
    Load poi data.
    :param path:
    :return: hash->poi counts,  poi -> total counts
    """
    f = open(os.path.join(path, 'poi_data/poi_data'), 'r')
    poi_cnt = defaultdict(int)
    l1_cnt = defaultdict(int)
    l2_cnt = defaultdict(int)
    poi_data = defaultdict(dict)
    for line in f:
        strs = line.rstrip(' \r\n').split('\t')
        dist_hash = strs[0]
        for s in strs[1:]:
            k, v = s.split(':')
            poi_data[dist_hash][k] = v
            levels = k.split('#')
            if len(levels) == 2:
                l1_cnt[levels[0]] += 1
                l2_cnt[levels[1]] += 1
            elif len(levels) == 1:
                l1_cnt[levels[0]] += 1
            else:
                print k
            poi_cnt[k] += 1
        pass
    f.close()
    print 'number of districts: {0}'.format(len(poi_data))
    print 'l1_types:{0}\tl2_types:{1}\tpoi_types:{2} '.format(len(l1_cnt), len(l2_cnt), len(poi_cnt))
    return poi_data, poi_cnt

def load_raw_data(dataset_name):
    pkl_fname = os.path.join(Config.get_string('data.path'), 'input', dataset_name + '.pkl')
    if not os.path.exists(pkl_fname):
        path = os.path.join(Config.get_string('data.path'), 'input', dataset_name)
        order_df = load_order_data(path)
        traffic_df = load_traffic_data(path)
        weather_df = load_weather_data(path)
        cluster_map = pd.read_csv(os.path.join(path, 'cluster_map/cluster_map'), sep='\t', names=['district_hash', 'district_id'])
        poi_data, poi_cnt = load_poi_data(path)
        data = order_df, traffic_df, weather_df, cluster_map, poi_data, poi_cnt
        cp.dump(data, open(pkl_fname, 'wb'), protocol=2)
    else:
        data = cp.load(open(pkl_fname, 'rb'))
    return data

