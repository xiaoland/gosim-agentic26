"""校验铁路边界：乘车日、跨日、金额与库存不可混淆。"""
import unittest
from rail_provider import parse_service


def record(start='23:50', arrival='01:20', duration='01:30'):
    row = [''] * 58
    for index, value in {2: '650000K52806', 3: 'K528', 6: 'GZQ', 7: 'SZQ',
                         8: start, 9: arrival, 10: duration, 11: 'Y', 13: '20261011',
                         26: '无', 30: '有', 31: '16',
                         39: 'O013600021M022800016O013603060'}.items():
        row[index] = value
    return '|'.join(row)


class RailContractTest(unittest.TestCase):
    def parse(self, raw):
        return parse_service(raw, '2026-10-12', {'GZQ': '广州', 'SZQ': '深圳'}, 'https://example.test', 1)

    def test_boarding_date_is_distinct_from_train_origin_and_arrival_rolls(self):
        service = self.parse(record())
        self.assertEqual(service['train_start_date'], '2026-10-11')
        self.assertEqual(service['departure_at'], '2026-10-12T23:50:00+08:00')
        self.assertEqual(service['arrival_at'], '2026-10-13T01:20:00+08:00')
        self.assertEqual(service['arrival_ts'] - service['departure_ts'], 90 * 60)
        self.assertIn('2026-10-12|GZQ|SZQ', service['service_ref'])

    def test_prices_are_cents_and_available_is_not_a_count(self):
        seats = self.parse(record())['seats']
        self.assertEqual(seats[0]['price_cents'], 13600)
        self.assertEqual(seats[0]['availability'], 'available')
        self.assertIsNone(seats[0]['remaining'])
        self.assertEqual(seats[1]['remaining'], 16)
        self.assertEqual(seats[2]['code'], 'W')
        self.assertEqual(seats[2]['availability'], 'unavailable')

    def test_inconsistent_arrival_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '不一致'):
            self.parse(record(arrival='02:20'))

    def test_unknown_inventory_does_not_mean_available(self):
        row = record().split('|')
        row[30] = '--'
        self.assertEqual(self.parse('|'.join(row))['seats'][0]['availability'], 'unknown')


if __name__ == '__main__':
    unittest.main()
