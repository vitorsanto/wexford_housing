import scrapy
import requests
import json

class WexfordWexfordTownSpider(scrapy.Spider):
    name = "wexford_wexford_town"
    allowed_domains = ["www.rent.ie"]
    start_urls = ["https://www.rent.ie/houses-to-let/wexford/wexford-town/"]
    mem_cache = set()
    token = ""
    chat_id = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_mem_cache()
        self.init_tokens()

    def init_tokens(self):
        try:
            with open("config.json", 'r') as reader:
                configs = json.load(reader)
                self.token = configs.get("token", "")
                self.chat_id = configs.get("chat_id", "")
        except FileNotFoundError:
            with open("config.json", 'w+') as writer:
                configs = {"token": "", "chat_id": ""}
                writer.write(json.dumps(configs))
    def init_mem_cache(self):
        if not self.mem_cache:
            try:
                with open("mem_cache.txt", 'r') as reader:
                    self.mem_cache = set(line.strip() for line in reader.readlines())
            except FileNotFoundError:
                with open("mem_cache.txt", 'w+') as writer:
                    pass

    def update_mem_cache(self, key):
        self.mem_cache.add(key)
        with open("mem_cache.txt", 'a+') as writer:
            writer.write(f"{key}\n")

    def parse(self, response, **kwargs):
        links = set(
            response.xpath(
                "//div[contains(@class, 'search_result')]"
            ).xpath(
                "//h2/a/@href"
            ).getall()
        )
        for link in links:
            yield scrapy.Request(link, self.parse_ad)

    def parse_ad(self, response):
        request_url = response.request.url.strip().lstrip()

        if request_url not in self.mem_cache:
            ad_header = "".join(response.xpath(
                "//div[contains(@class, 'smi_details_box')]"
            ).xpath(
                "//div[contains(@class, 'text')]/text()"
            ).getall()[1]).strip().lstrip().replace("\n", '')

            ad_price = response.xpath(
                "//div[contains(@class, 'smi_details_box')]"
            ).xpath(
                "//div[contains(@class, 'text')]/h2/text()"
            ).get().strip().lstrip()
            self.update_mem_cache(request_url)
            message = f"""Link: {request_url}\nDescricao: {ad_header}\nPreco: {ad_price}\n"""
            self.send_message(message)
    
    def send_message(self, text):
        # token = "6426070828:AAEuQ3yTh7R9-SV56Elp0-ACw5XiRsRe1KY"
        # chat_id = "617583448"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        response = requests.post(url, json={'chat_id': self.chat_id, 'text': text})
        print(response)


