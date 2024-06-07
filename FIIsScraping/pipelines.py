import re
from itemadapter import ItemAdapter


class FiisScrapingPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        fields = adapter.field_names()

        for field in fields:
            field_type = type(adapter.get(field))

            if field_type is str:
                adapter[field] = adapter.get(field).strip()

            elif field_type is list:
                for value in adapter.get(field):
                    strip_dict_values(value)

            elif field_type is dict:
                strip_dict_values(adapter.get(field))

            if field == 'dividend_yield':
                adapter[field] += '%'
            
            if field == 'net_worth':
                pattern = r'(</?(b|small)>)|(\s+)'
                adapter[field] = '$ '.join(re.sub(pattern, '', adapter.get(field)).strip().split('$'))

            if field in ['last_dividend', 'average_daily']:
                adapter[field] = 'R$ ' + adapter.get(field)

        return item


class StocksScrapingPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        fields = adapter.field_names()

        for field in fields:
            field_type = type(adapter.get(field))

            if field_type is str:
                adapter[field] = adapter.get(field).strip()

            if field == 'operation_sector':
                seen = set()
                unrepeated_sectors = []
                sectors = adapter.get(field).split(' - ')
                for sector in sectors:
                    if sector not in seen:
                        seen.add(sector)
                        unrepeated_sectors.append(sector.strip())
                adapter[field] = ' - '.join(unrepeated_sectors)

            if field == 'dividend_yield' and not '%' in adapter[field]:
                adapter[field] += '%'
            
            if field in ['average_daily', 'total_stock_paper', 'net_worth']:
                quantifiers = [
                    {'word': ' Bilhão', 'letter': 'B'},
                    {'word': ' Bilhões', 'letter': 'B'},
                    {'word': ' Milhão', 'letter': 'M'},
                    {'word': ' Milhões', 'letter': 'M'},
                    {'word': ' Mil', 'letter': 'K'},
                ]
                for word in quantifiers:
                    adapter[field] = adapter.get(field).replace(word.get('word'), word.get('letter'))

            if field in ['current_price', 'average_daily', 'net_worth']:
                adapter[field] = adapter.get(field)
            
        return item

def strip_dict_values(dict):
    for key in dict.keys():
        dict[key] = dict.get(key).strip()
        if key == 'dividend':
            dict[key] = re.findall('R\$\s[\d+]+\,\d+', dict[key])[0]
        if key == 'future_pay_day':
            dict[key] = re.findall('(\d+\/\d+\/\d+)+', dict[key])[0]
        if key == 'date':
            dict[key] = '/'.join(re.split('[\/|\.]', dict.get(key).split(' ')[-1]))
