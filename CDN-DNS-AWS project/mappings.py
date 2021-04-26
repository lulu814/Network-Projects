from ip_ranges import AWS_IP_RANGES
from ipaddress import ip_network, ip_address
import urllib.request
import math
import json

UNKNOWN = 'Unknown'
CDN_MAPPINGS = [
    {
        'hostname': 'ec2-54-159-99-25.compute-1.amazonaws.com',
        'ip_address': '54.159.99.25',
        'region': 'us-east-1',
        'latitude': 39.043701171875,
        'longitude': -77.47419738769531
    },
    {
        'hostname': 'ec2-50-18-189-64.us-west-1.compute.amazonaws.com',
        'ip_address': '50.18.189.64',
        'region': 'us-west-1',
        'latitude': 37.330528259277344,
        'longitude': -121.83822631835938
    },
    {
        'hostname': 'ec2-18-229-54-5.sa-east-1.compute.amazonaws.com',
        'ip_address': '18.229.54.5',
        'region': 'sa-east-1',
        'latitude': -23.5515193939209,
        'longitude': -46.633140563964844
    },
    {
        'hostname': 'ec2-13-244-183-11.af-south-1.compute.amazonaws.com',
        'ip_address': '13.244.183.11',
        'region': 'af-south-1',
        'latitude': -33.92490005493164,
        'longitude': 18.424100875854492
    },
    {
        'hostname': 'ec2-13-36-115-83.eu-west-3.compute.amazonaws.com',
        'ip_address': '13.36.115.83',
        'region': 'eu-west-3',
        'latitude': 48.8602294921875,
        'longitude': 2.3410699367523193},
    {
        'hostname': 'ec2-13-51-89-160.eu-north-1.compute.amazonaws.com',
        'ip_address': '13.51.89.160',
        'region': 'eu-north-1',
        'latitude': 59.315120697021484,
        'longitude': 18.051319122314453
    },
    {
        'hostname': 'ec2-65-1-183-44.ap-south-1.compute.amazonaws.com',
        'ip_address': '65.1.183.44',
        'region': 'ap-south-1',
        'latitude': 19.076000213623047,
        'longitude': 72.87770080566406
    },
    {
        'hostname': 'ec2-13-208-85-51.ap-northeast-3.compute.amazonaws.com',
        'ip_address': '13.208.85.51',
        'region': 'ap-northeast-3',
        'latitude': 34.67094039916992,
        'longitude': 135.50750732421875
    },
    {
        'hostname': 'ec2-54-79-190-216.ap-southeast-2.compute.amazonaws.com',
        'ip_address': '54.79.190.216',
        'region': 'ap-southeast-2',
        'latitude': -33.86714172363281,
        'longitude': 151.2071075439453
    }
]


# Use https://ip-ranges.amazonaws.com/ip-ranges.json to get aws region for given cdn hosts.
def find_aws_region(ip):
    prefixes = AWS_IP_RANGES['prefixes']
    my_ip = ip_address(ip)
    region = UNKNOWN
    for prefix in prefixes:
        if my_ip in ip_network(prefix['ip_prefix']):
            region = prefix['region']
            break
    return region


def find_best_cdn(ip):
    # use aws region
    region = find_aws_region(ip)
    if region != UNKNOWN:
        for m in CDN_MAPPINGS:
            if m['region'] == region:
                return m['ip_address']

    # use distance
    lat, lon = get_geo_location(ip)
    if lat is None or lon is None:
        return CDN_MAPPINGS[0]['ip_address']
    best_distance = None
    best_cdn_ip = None
    for m in CDN_MAPPINGS:
        dist = get_distance(lat, lon, m['latitude'], m['longitude'])
        if not best_distance or best_distance > dist:
            best_distance = dist
            best_cdn_ip = m['ip_address']
    return best_cdn_ip


# get lat, lon from given IP
def get_geo_location(ip):
    url = 'http://api.ipstack.com/{}?access_key=f7ac9367ea49996a45825cf37682d809'.format(ip)
    r = urllib.request.urlopen(url)
    try:
        result = json.load(r)
        latitude = result['latitude']
        longitude = result['longitude']
        return latitude, longitude
    except urllib.error.HTTPError as e:
        return None, None


# find distance between two coordinates
def get_distance(lat1, lon1, lat2, lon2):
    R = 6373.0  # radius of the Earth

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
