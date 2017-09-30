# -*- coding: utf-8 -*-

import requests
import math

bd_key = 'A9f77664caa0b87520c3708a6750bbdb'  # 百度开放平台的key
gd_key = '199ceeb5e3843a3bb1b225957227f536'  # 高德开放平台的key

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def geocode_bd(address, city=""):
    """
    根据地址获取经纬度
    :param address:
    :param city:
    :return:
    """
    params = {
        'address': address,
        'city': city,
        'ak': bd_key,
        'output': 'json'
    }

    response = requests.get('http://api.map.baidu.com/geocoder/v2/', params=params)
    if response and response.status_code == 200:
        result = response.json()
        if result['status'] == 0:
            return 0, result['result']['location']
        else:
            return result['status'], None
    else:
        return None, None


def regeocode_bd(location):
    """
    根据经纬度确定地址
    :param lat:
    :param lon:
    :return:
    """
    params = {
        'location': location,
        'ak': bd_key,
        'output': 'json'
    }

    response = requests.get('http://api.map.baidu.com/geocoder/v2/', params=params)
    if response and response.status_code == 200:
        result = response.json()
        if result['status'] == 0:
            return 0, result['result']
        else:
            return result['status'], None
    else:
        return None, None


def geocode_gd(address, city=None):
    """
    根据经纬度确定地址
    :param address:
    :param city:
    :return:
    """
    params = {
        'key': gd_key,
        'city': city,
        'address': address
    }
    response = requests.get("http://restapi.amap.com/v3/geocode/geo", params=params)
    if response and response.status_code == 200:
        result = response.json()
        if result['status'] == '1' and int(result['count']) >= 1:
            return result['geocodes'][0]['location']
        else:
            return None
    else:
        return None


def regeocode_gd(location):
    """
    根据经纬度确定地址
    :param location:
    :return:
    """
    params = {
        'location': location,
        'key': gd_key
    }
    base = 'http://restapi.amap.com/v3/geocode/regeo'
    response = requests.get(base, params)
    if response and response.status_code == 200:
        result = response.json()
        print result
        if result.get('status') == '1':
            return result['regeocode']
        else:
            return None
    else:
        return None


def transform(location, coordsys='gps'):
    """
    gps坐标通过高德API转换
    :param location:
    :return:
    """
    params = {
        'coordsys': coordsys,
        'locations': location,
        'key': gd_key
    }
    base = 'http://restapi.amap.com/v3/assistant/coordinate/convert'
    response = requests.get(base, params)
    if response and response.status_code == 200:
        result = response.json()
        if result.get('status') == '1':
            return result['locations']
        else:
            return None
    else:
        return None


def gcj02tobd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09togcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


if __name__ == '__main__':
    lng = 116.475323
    lat = 39.929214
    result1 = gcj02tobd09(lng, lat)
    result2 = bd09togcj02(lng, lat)
    result3 = wgs84togcj02(lng, lat)
    result4 = gcj02towgs84(lng, lat)

    _, result5 = geocode_bd('北京市朝阳区朝阳公园')
    _, result6 = regeocode_bd(str(lat) + ',' + str(lng))

    result7 = geocode_gd('北京市朝阳区朝阳公园')
    result8 = regeocode_gd(str(lng) + ',' + str(lat))

    print "origin: lng:%s lat:%s" % (lng, lat)
    print "gcj02tobd09:%s" % result1
    print "bd09togcj02:%s" % result2
    print "wgs84togcj02:%s" % result3
    print "gcj02towgs84:%s" % result4
    print "geocode_bd:%s" % result5
    print "regeocode_bd:%s" % result6
    print "geocode_gd:%s" % result7
    print "regeocode_gd:%s" % result8

