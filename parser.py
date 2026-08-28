import json
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://thelastgame.org/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# НАСТРОЙКА: Сколько страниц обходить. Поставим 5 для теста (будет 50 игр)
MAX_PAGES = 5 

def parse_games():
    downloads = []
    
    for page in range(1, MAX_PAGES + 1):
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page}/"
            
        print(f"Запрос к странице {page}: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Ошибка загрузки страницы {page}: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Находим посты строго через тег article (это исключит дубли и мусор из сайдбара)
            articles = soup.find_all('article')
            
            # Если тегов article нет, ищем h2, но строго внутри основного контента
            if not articles:
                articles = soup.find_all('h2')

            page_games_count = 0
            for block in articles:
                # Ищем ссылку и заголовок внутри блока
                link_tag = block.find('a') if block.name != 'h2' else block.find('a')
                
                # Если в h2 нет ссылки или текст пустой, пропускаем
                if not link_tag or not link_tag.text.strip():
                    continue
                    
                title = link_tag.text.strip()
                game_url = link_tag['href']
                
                # Исключаем ссылки на категории, правила или дубли главной страницы
                if "/page/" in game_url or game_url == BASE_URL or "category" in game_url:
                    continue

                # Проверяем, нет ли уже этой игры в списке (защита от дублей)
                if any(d["title"] == title for d in downloads):
                    continue

                download_entry = {
                    "title": title,
                    "uris": [game_url],
                    "uploadDate": f"Страница {page}",
                    "fileSize": "Уточняется на сайте",
                    "descriptionHtml": f'<a href="{game_url}">Инструкция и скачивание на TheLastGame</a>',
                    "linksHidden": False
                }
                downloads.append(download_entry)
                page_games_count += 1
                
            print(f"Успешно собрано игр со страницы {page}: {page_games_count}")
            
            # Если страница оказалась пустой, значит мы дошли до конца каталога
            if page_games_count == 0:
                print("Больше игр не найдено, останавливаем обход страниц.")
                break
                
            time.sleep(1.5) # Пауза, чтобы сайт не заблокировал за частые запросы
            
        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
            continue

    return downloads

def main():
    game_list = parse_games()
    
    hydra_source = {
        "name": "TheLastGame Полный Каталог",
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[УСПЕХ] Сборка завершена! Всего сохранено игр в файл: {len(game_list)}")

if __name__ == "__main__":
    main()
