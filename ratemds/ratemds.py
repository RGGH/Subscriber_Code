from scrapy.crawler import CrawlerProcess
import scrapy
import os
import json

class Ratemds(scrapy.Spider):
    name = 'ratemds'

    custom_settings = {"FEEDS": {"resultsX.csv": {"format": "csv"}}}
    start_urls = ['https://www.ratemds.com/best-doctors/?specialty=acupuncturist']
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }

    try:
        os.remove('results.csv')
    except OSError:
        pass

    def start_requests(self):
        yield scrapy.Request('https://www.ratemds.com/best-doctors/?specialty=acupuncturist',
            headers=self.headers,
            callback=self.doctor_url)

    def doctor_url(self, response):
        for a in response.css('.search-item-doctor-link'):
            yield response.follow(url=a,
                headers=self.headers,
                callback=self.doctor)

        # Add next page back in once happy with first page results from testing



#        next_page = response.css('.pagination-sm a::attr(href)')[-1].get()
#        if next_page is not None:
#            next_page = response.urljoin(next_page)
#            yield scrapy.Request(next_page,
#                                 headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.50747 OPRGX/60.0.3255.50747"},
#                                 callback=self.doctor_url)

    def doctor(self, response):

        if response.xpath('.//*[contains(text(),"female")]/text()').get():
            gender = 'female'
        else:
            gender = 'male'

        script = response.xpath("//script[@type='application/ld+json']/text()").get()
        json_data = json.loads(script)
        #print(json_data)
        #
        yield {
            'Image': json_data['image'],
            'Name': json_data['name'],
            'Telephone' : json_data['telephone'],
            'Reviews':json_data['aggregateRating']['ratingValue'],
            'Gender': gender,
        }


        #         'First_and_Last_Name': response.css('h1::text').get(),
        #         'Position': response.css('.col-sm-6 .search-item-info~ .search-item-info+ .search-item-info span::text').getall(),
        #         'Reviews': response.css('.star-rating-count span span::text').get(),
        #         'Gender': response.xpath('.//*[@class="search-item-info"]/text()').get(),
        #         'Facilities': response.css('.search-item-extra a span::text').getall()
        #         }


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(Ratemds)
    process.start()
