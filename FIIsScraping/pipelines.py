import re
from itemadapter import ItemAdapter
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


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

            if field == 'last_management_report':
                if report_link := adapter.get('last_management_report').get('link'):
                    adapter['last_management_report']['link'] = report_link.replace('downloadDocumento', 'exibirDocumento')

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


            if field == 'last_management_report':
                if report_link := adapter.get('last_management_report').get('link'):
                    parsed_url = urlparse(report_link.replace('frmDownloadDocumento', 'frmExibirArquivoIPEExterno'))
                    query_params = parse_qs(parsed_url.query)
                    new_query_params = {
                        'NumeroProtocoloEntrega': int(query_params['numProtocolo'][0])
                    }
                    new_query_string = urlencode(new_query_params)
                    new_url = urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query_string,
                        parsed_url.fragment
                    ))
                    adapter['last_management_report']['link'] = new_url 

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
