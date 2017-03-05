import os, re, sys, time
import xml.etree.ElementTree as ET
from os import path
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

_g_usage_msg = "Usage: {} track.gpx cardio.xml".format(sys.argv[0])
_g_timer_interval = 5  # seconds

_g_server = "localhost"  # 127.0.0.1
_g_server_port = 2017
_g_server_path = "data"  # http://localhost:2017/data


def _check_args():
    if len(sys.argv) < 3:
        exit(_g_usage_msg)

    gpx_file = sys.argv[1]
    cardio_file = sys.argv[2]
    if '.gpx' not in gpx_file:
        exit(_g_usage_msg)
    if '.xml' not in cardio_file:
        exit(_g_usage_msg)
    return path.abspath(gpx_file), path.abspath(cardio_file)


def _parse_gpx(gpx_file):
    list_points = []
    f = open(gpx_file)
    gpx_str = f.read()
    f.close()
    gpx_xml = ET.fromstring(gpx_str)
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    rte_tag = gpx_xml.find('gpx:rte', ns)
    rte_name = rte_tag.find('gpx:name', ns).text
    rtept_tags = rte_tag.findall('gpx:rtept', ns)
    for rtept_tag in rtept_tags:
        list_points.append(rtept_tag.attrib)
    return rte_name, list_points


def _parse_cardio(cardio_file):
    list_cardios = []
    f = open(cardio_file)
    cardio_str = f.read()
    f.close()
    cardio_xml = ET.fromstring(cardio_str)
    cardio_logs = cardio_xml.findall('cardio_log')
    for cardio_log in cardio_logs:
        list_cardios.append(cardio_log.attrib["bpm"])
    return list_cardios


def _process_data(track_name, track_points, track_cardios):
    response_status = True
    url = 'http://{}:{}/{}'.format(_g_server, _g_server_port, _g_server_path)
    url += '?name={}&lat={}&lon={}&bpm={}'

    for i in range(len(track_points)):
        new_url = url.format(track_name, track_points[i]['lat'], track_points[i]['lon'], track_cardios[i])
        print ("Sending data to server")
        response = ''
        try:
            response = urlopen(new_url).read()
        except Exception as e:
            exit("Error sending request")
        if "ok" not in response:
            response_status = False
            break
        print ("ok")
        time.sleep(_g_timer_interval)
    return response_status


def _main():
    gpx_file, cardio_file = _check_args()
    track_name, track_points = _parse_gpx(gpx_file)
    track_cardios = _parse_cardio(cardio_file)

    if len(track_points) != len(track_cardios):
        exit('Error: points({}) != cardio_logs({})'.format(len(track_points), len(track_cardios)))

    if not _process_data(track_name, track_points, track_cardios):
        exit('Error')


if __name__ == '__main__':
    _main()
