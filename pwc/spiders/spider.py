import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PwcItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'

class PwcSpider(scrapy.Spider):
	name = 'pwc'
	start_urls = ['https://pwcbank.com/news/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="button red"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="pagination"]/a[text()="< Older Posts"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		data = response.xpath('//script[@type="application/ld+json"]/text()').get()
		date = json.loads(data)
		try:
			date = date['@graph'][2]['datePublished'].split('T')[0]
		except KeyError:
			date = date['@graph'][1]['datePublished'].split('T')[0]

		title = response.xpath('(//h1)[2]/text()').get()
		content = response.xpath('//div[@class="entry-content"]//text()[not (ancestor::h1 or ancestor::img)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PwcItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
