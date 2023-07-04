import asyncio
import aiohttp
from PySide6.QtCore import QThread, Signal 
from bs4 import BeautifulSoup
from status import Status

class ProductStatusWorker(QThread):
    updated = Signal()

    def __init__(self, product_availability):
        super().__init__()
        self.product_availability = product_availability


    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.get_item_status(self.product_availability))
        except Exception as e:
            print(f'Error in run {e}')
        finally:
            self.updated.emit()

    async def get_item_status(self, product_availability):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for product_key, status in product_availability.items():
                if status != Status(0).name:
                    url = f'https://www.nike.com/pl/w?q={product_key}&vst={product_key}'
                    task = asyncio.ensure_future(self.fetch_data(session, url, product_key, product_availability))
                    tasks.append(task)

            await asyncio.gather(*tasks)
        

    async def fetch_data(self, session, url, product_key, product_availability):
        try:
            async with session.get(url) as response:
                html = await response.text()
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
            return product_availability

        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            data = soup.find('div', id='skip-to-products')
        except Exception as e:
            print(f'Error parsing HTML from {url}')


        if data is None:
            product_availability[product_key] = Status(1).name
        else:
            data = data.contents
            if len(data) == 1:
                product_availability[product_key] = Status(1).name
            else:
                product_availability[product_key] = Status(0).name
        
        return product_availability