from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from oxygen.items import OxygenItem

import pyquery

## My imports
import re
from resources import colors
from resources import accessories
from resources import jewelry
from resources import shoes

class OxygenSpider(CrawlSpider):
    name = 'oxygenboutique.com'
    allowed_domains = ['oxygenboutique.com']
    start_urls = ['http://www.oxygenboutique.com']

    rules = (
        # items
        Rule(SgmlLinkExtractor(restrict_xpaths='//div[@class="DataContainer"]'), callback='parse_item'),
        # main menu
        Rule(SgmlLinkExtractor(restrict_xpaths='//ul[@class="topnav"]', allow=(r'(Sale\-In|clothing|[Aa]ll)\.aspx')),
             process_links='viewAll', follow=True),
    )

    def viewAll(self, links):
        '''add parameter to view all items on same site'''
        for link in links:
            link.url = link.url + '?ViewAll=1'
        return links

    def parse_item(self, response):
        self.pq = pyquery.PyQuery(response.body)
        item = OxygenItem()


        # Gender
        item['gender'] = 'F' # Women's Clothing Store

        # Designer
        designer = self.pq('.brand_name')('a').text()
        if designer == 'Land by Land':  # Homewear
            return None
        item['designer'] = designer

        # Code
        item['code'] = response.url.split('/')[-1].replace('.aspx', '')

        # Name
        item['name'] = self.pq('.right h2').text()

        # Description
        item['description'] = self.pq('#accordion > div:first').text()

        # Type ('A'-apparel, 'S'-shoes, 'B'-bags, 'J'-jewlery, 'R'-accessories)
        item['type'] = None
        desc = item['description'].lower()  # used also for 'raw_color'
        if any(map(lambda word: re.search(r'\b%s\b' % word, desc), jewelry)):
            item['type'] = 'J'
        elif any(map(lambda word: re.search(r'\b%s\b' % word, desc), accessories)):
            item['type'] = 'R'
        elif any(map(lambda word: re.search(r'\b%s\b' % word, desc), shoes)):
            item['type'] = 'S'
        else:
            item['type'] = 'A'

        # Raw color
        item['raw_color'] = None
        for color in colors:
            if re.search(r'\b%s\b' % color, desc):
                item['raw_color'] = color
                break

        # Image urls
        item['image_urls'] = ['http://www.oxygenboutique.com/'+a.attrib['href'] for a in self.pq('#thumbnails-container a')]

        # GBP price & discount:
        price_node = self.pq('span.price')
        if price_node('.offsetMark').text():
            item['usd_price'] = price_node('.offsetMark').text()
            item['sale_discount'] = 100.0-((float(price_node('span:last').text())*100)/float(item['usd_price']))
        else:
            item['usd_price'] = float(re.search('\d+\.\d{2}', self.pq('span.price').text()).group())
            item['sale_discount'] = 0.0

        # Stock status
        stock = {}
        for option in [opt for opt in self.pq('#ctl00_ContentPlaceHolder1_ddlSize option') if opt.attrib['value'] != '-1']:
            if option.attrib['value'] == '0':
                stock[option.text.split(' - ')[0]] = 1
            else:
                stock[option.text] = 3
        item['stock_status'] = stock

        # Source url
        item['link'] = response.url

        return item

