# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class OxygenItem(Item):
    code = Field()
    color = Field()
    description = Field()
    designer = Field()
    gender = Field()
    image_urls = Field()
    link = Field()
    name = Field()
    raw_color = Field()
    sale_discount = Field()
    stock_status = Field()
    type = Field()
    usd_price = Field()
