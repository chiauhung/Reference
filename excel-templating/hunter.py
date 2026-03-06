# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess

class HunterSpider(scrapy.Spider):
	name = "hunter"
	allowed_domains = ["hunterxhunter.wikia.com"]
	start_urls = ['http://hunterxhunter.wikia.com/wiki/Gon_Freecss',
				  'http://hunterxhunter.wikia.com/wiki/Killua_Zoldyck',
				  'http://hunterxhunter.wikia.com/wiki/Kurapika',
				  'http://hunterxhunter.wikia.com/wiki/Leorio_Paradinight']

	def parse(self, response):
		character_json = {}

		character_json['ability'] = {}
		ability = response.xpath('//table[@class= "wikitable" and @cellspacing="1/6"]//tr')
		for row in ability:
			if row.xpath('.//font[contains(text(),"Type:")]'):
				nen_type = row.xpath('.//a/text()').extract_first()
				if not nen_type:
					nen_type = row.xpath('.//font/text()').extract_first()
					if 'Nen Type:' in nen_type:
						continue
					else:
						nen_type = nen_type.replace('Type: ','')
				name = row.xpath('.//b/text()').extract_first()
				if not name:
					name = row.xpath('.//font/text()').extract()[-1]
				character_json['ability'].update({name.strip():nen_type.strip()})

		character_json['name'] = response.xpath('//h1[@class="page-header__title"]/text()').extract_first()
		
		
		nen_type = response.xpath('//font[contains(text(),"Nen Type")]/text()').extract_first()
		character_json['nen_type'] = nen_type.split(':')[1].strip()
		character_json['statistics'] = []

		statistics = response.xpath('//table[@class= "article-table" and @style="margin: 0 auto;"]//tr')
		features = statistics.xpath('.//th/text()').extract()
		
		for row in statistics:
			stats = row.xpath('.//td/text()').extract()
			if not stats: continue
			correspond_stat = {i.strip():j.strip().strip('/5') for i,j in zip(features, stats)}
			character_json['statistics'].append(correspond_stat)
		
		yield character_json

if __name__ == '__main__':
	process = CrawlerProcess({
		'FEED_URI':'hunter.json',
		'FEED_FORMAT':'json'
		})
	process.crawl(HunterSpider)
	process.start()
