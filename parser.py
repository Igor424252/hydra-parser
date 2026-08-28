import json
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://thelastgame.org/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# НАСТРОЙКА: Сколько страниц обходить. Поставьте 5 для теста (будет до 50 игр)
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
            
            # Находим карточки игр по точному классу контейнера на сайте
            game_blocks = soup.find_all('div', class_='post') or soup.find_all('article', class_='post')
            
            # Если специфичные классы не нашлись, откатываемся к h2
            if not game_blocks:
                game_blocks = soup.find_all('h2')

            page_games_count = 0
            for block in game_blocks:
                link_tag = block.find('a')
                if not link_tag or not link_tag.text.strip():
                    continue
                    
                title = link_tag.text.strip()
                game_url = link_tag['href']
                
                # ЖЕСТКИЙ ФИЛЬТР: игнорируем служебные страницы, правила и регистрацию
                black_list = ["do=register", "rules", "index.php", "/page/", "category", "search"]
                if any(garbage in game_url for garbage in black_list) or game_url == BASE_URL:
                    continue
                
                # Защита от дублирования служебных пунктов вроде заголовков виджетов
                if title in ["Регистрация", "Вход", "Правила", "Главная", "Популярные игры"]:
                    continue

                # Защита от повторов в итоговом файле
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
                
            print(f"Успешно отфильтровано и собрано игр со страницы {page}: {page_games_count}")
            
            if page_games_count == 0:
                print("Игры кончились или сработал блок.")
                
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
            continue

    return downloads

def main():
    game_list = parse_games()
    
    hydra_source = {
        "name": "TheLastGame Чистый Каталог",
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[УСПЕХ] Скрипт отработал. Всего чистых игр в файле: {len(game_list)}")

if __name__ == "__main__":
    main()
