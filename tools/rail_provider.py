#!/usr/bin/env python3
"""低频匿名查询 12306 网页班次，输出应用可消费的铁路记录。"""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlencode

BASE = 'https://kyfw.12306.cn/otn/'
BEIJING = timezone(timedelta(hours=8))
SEATS = {
    '9': ('商务座', 32), 'P': ('特等座', 25), 'M': ('一等座', 31),
    'D': ('优选一等座', 31), 'O': ('二等座', 30), 'S': ('二等包座', 30),
    '6': ('高级软卧', 21), 'A': ('高级动卧', 21), '4': ('软卧', 23),
    'I': ('一等卧', 23), 'F': ('动卧', 23), '3': ('硬卧', 28),
    'J': ('二等卧', 28), '2': ('软座', 24), '1': ('硬座', 29), 'W': ('无座', 26),
}


def parse_service(raw, boarding_date, station_names, source_url, source_ts):
    row = raw.split('|')
    if len(row) < 40:
        raise ValueError('12306 班次字段不足，拒绝猜测解析')
    departure = datetime.fromisoformat(boarding_date + 'T' + row[8]).replace(tzinfo=BEIJING)
    hours, minutes = map(int, row[10].split(':'))
    arrival = departure + timedelta(hours=hours, minutes=minutes)
    if arrival.strftime('%H:%M') != row[9]:
        raise ValueError('12306 到达时间与历时不一致')
    encoded = row[39]
    if len(encoded) % 10:
        raise ValueError('12306 席别价格字段格式变化')
    seats = []
    for offset in range(0, len(encoded), 10):
        value = encoded[offset:offset + 10]
        if not value[1:].isdigit():
            raise ValueError('12306 席别价格不是数字编码')
        code = 'W' if int(value[6:]) >= 3000 else value[0]
        if code not in SEATS:
            raise ValueError('12306 返回未支持席别编码：' + code)
        label, index = SEATS[code]
        remaining = row[index]
        availability = ('available' if remaining == '有' or remaining.isdigit() and int(remaining) > 0
                        else 'unavailable' if remaining in ('无', '0') else 'unknown')
        seats.append({'code': code, 'label': label, 'price_cents': int(value[1:6]) * 10,
                      'currency': 'CNY', 'availability': availability,
                      'remaining': int(remaining) if remaining.isdigit() else None,
                      'raw_availability': remaining})
    return {'service_ref': '|'.join(['12306', row[2], row[13], boarding_date, row[6], row[7]]),
            'train_id': row[2], 'train_code': row[3], 'boarding_date': boarding_date,
            'train_start_date': datetime.strptime(row[13], '%Y%m%d').date().isoformat(),
            'from': {'code': row[6], 'name': station_names[row[6]]},
            'to': {'code': row[7], 'name': station_names[row[7]]},
            'departure_ts': int(departure.timestamp()), 'arrival_ts': int(arrival.timestamp()),
            'departure_at': departure.isoformat(), 'arrival_at': arrival.isoformat(),
            'seats': seats, 'source': '12306_web', 'source_ts': source_ts,
            'source_url': source_url, 'bookable': row[11] == 'Y'}


def query(boarding_date, origin, destination, exact_stations=False):
    datetime.strptime(boarding_date, '%Y-%m-%d')
    if not all(re.fullmatch('[A-Z]{3}', code) for code in (origin, destination)):
        raise ValueError('请输入三个大写字母的车站 telecode')
    with tempfile.TemporaryDirectory(prefix='navigation-rail-') as directory:
        cookie = str(Path(directory) / 'anonymous.cookie')

        def get(url):
            response = subprocess.run(['curl', '-fsSL', '--max-time', '20', '-b', cookie, '-c', cookie,
                                       '-e', BASE + 'leftTicket/init', url], capture_output=True, text=True)
            if response.returncode:
                raise RuntimeError('12306 网络请求失败，curl code=' + str(response.returncode))
            return response.stdout

        page = get(BASE + 'leftTicket/init')
        match = re.search(r"var CLeftTicketUrl = '([^']+)'", page)
        if not match or not re.fullmatch(r'leftTicket/query[A-Za-z]*', match[1]):
            raise RuntimeError('12306 页面没有可识别的查询路径')
        url = BASE + match[1] + '?' + urlencode({'leftTicketDTO.train_date': boarding_date,
            'leftTicketDTO.from_station': origin, 'leftTicketDTO.to_station': destination,
            'purpose_codes': 'ADULT'})
        try:
            response = json.loads(get(url))
        except json.JSONDecodeError:
            raise RuntimeError('12306 没有返回 JSON，可能是访问限制') from None
        if response.get('status') is not True or not isinstance(response.get('data', {}).get('result'), list):
            raise RuntimeError('12306 查询失败或响应契约变化')
        source_ts = int(datetime.now(timezone.utc).timestamp())
        services = [parse_service(raw, boarding_date, response['data']['map'], url, source_ts)
                    for raw in response['data']['result']]
        if exact_stations:
            services = [s for s in services if s['from']['code'] == origin and s['to']['code'] == destination]
        return {'success': True, 'source': '12306_web', 'source_ts': source_ts,
                'query': {'boarding_date': boarding_date, 'from_code': origin, 'to_code': destination,
                          'exact_stations': exact_stations}, 'services': services}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--from-code', required=True)
    parser.add_argument('--to-code', required=True)
    parser.add_argument('--exact-stations', action='store_true')
    args = parser.parse_args()
    try:
        result = query(args.date, args.from_code, args.to_code, args.exact_stations)
    except (ValueError, KeyError, RuntimeError) as error:
        result = {'success': False, 'source': '12306_web', 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['success'] else 1)
