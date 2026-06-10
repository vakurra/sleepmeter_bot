import requests
import asyncio
from collections import deque
from html import unescape


# Парсер KWORK
class KworkMonitor:

    def __init__(self):

        self.task = None
        self.session = requests.Session()
        self.seen_ids = set()
        self.id_queue = deque(maxlen=100)
        self.category = 41
        self.enabled = False
        self.initialized = False
        self.url = "https://kwork.ru/projects"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://kwork.ru/projects"
        }


    def get_projects(self):
        """Получение текущих проектов по категории"""
        
        response = self.session.post(
            self.url,
            data={"c": str(self.category)},
            headers=self.headers,
            timeout=15
        )

        response.raise_for_status()
        projects = response.json()["data"]["wants"]
        return projects


    def remember_project(self, pid):
        """Запоминает до 100 последних проектов"""
        if len(self.id_queue) == self.id_queue.maxlen:
            oldest_id = self.id_queue.popleft()
            self.seen_ids.discard(oldest_id)

        self.id_queue.append(pid)
        self.seen_ids.add(pid)


    def initialize(self):
        """Получение проектов в первый раз(чтоб не печатать их)"""

        projects = self.get_projects()

        for project in projects:
            pid = project["id"]
            self.remember_project(pid)

        self.initialized = True
        return len(self.seen_ids)

    def get_new_projects(self):
        """Находит проекты, которых еще не было в памяти"""
        if not self.initialized:
            raise RuntimeError("KworkMonitor not initialized")

        projects = self.get_projects()
        new_projects = []

        for project in projects:
            pid = project["id"]

            if pid not in self.seen_ids:
                self.remember_project(pid)
                new_projects.append(project)

        return new_projects
    

monitor = KworkMonitor()

async def monitoring_loop(bot, chat_id):
    """Цикл мониторинга"""    
    
    while True:
        try:
            
            if monitor.enabled:
                projects = monitor.get_new_projects()
                
                for project in projects:
                    description = unescape(project["description"])
                    text = (
                        f"💼 <b>{project['name']}</b>\n\n"
                        f"💰 {project['priceLimit']} - "
                        f"{project['possiblePriceLimit']} ₽\n\n"
                        f"📅 {project['date_create']}\n\n"
                        f"📝Описание\n"
                        f"{description[:4096]}\n\n"
                        f"🔗 https://kwork.ru/projects/"
                        f"{project['id']}/view"
                    )

                    await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        disable_web_page_preview=True
                    )
            await asyncio.sleep(120)

        except Exception as e:
            print(f"Kwork monitoring error: {e}")
            await asyncio.sleep(60)