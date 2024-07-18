import scrapy
from urllib.parse import urljoin
from gc import callbacks



class AmazonreviewSpider(scrapy.Spider):
    name = "amazonreview" 
    custom_settings = {
        'FEEDS': { 'data.csv': { 'format': 'csv',}}
        }
    
    def start_requests(self):
        asin_list = ['B0CRDCXRK2'] 
        for asin in asin_list:
            review_url = f'https://www.amazon.com/product-reviews/{asin}/'
            yield scrapy.Request(url= review_url, callback=self.parse_details, meta= {'asin' : asin, 'retry_count' : 0})

    def parse_details(self, response):
        asin = response.meta['asin']
        retry_count = response.meta['retry_count']
        
        next_page = response.css(".a-pagination .a-last>a::attr(href)").get()
        if next_page is not None:
            retry_count = 0
            next_page_url =urljoin('https://www.amazon.com/', next_page)
            yield scrapy.Request(url = next_page_url, callback = self.parse_details, meta = {'asin' : asin, 'retry_count' : retry_count} )
            
        elif retry_count < 3:
            retry_count = retry_count + 1
            yield scrapy.Request(url = response.url, callback = self.parse_details, dont_filter=True , meta = {'asin' : asin, 'retry_count' : retry_count} )
            
        review_elements = response.css("#cm_cr-review_list div.review")
    
        
        for review_element in review_elements:
            text = "".join(review_element.css('span[data-hook=review-body] ::text').getall()).strip()
            if "The media could not be loaded" in text:
                text = text.replace("The media could not be loaded.","").strip()
                
            stars_title = review_element.css(".review-title-content span::text").getall()
            
            yield {
                "asin" : asin,
                "text" : text,
                "title": stars_title[1],
                "Verified": bool(review_element.css("a.a-link-normal span[data-hook=avp-badge]::text").get()),
                "location and date" :  review_elements.css("div.a-row span[data-hook=review-date]::text").get(),
                "stars": stars_title[0],
                
            }
        
        
