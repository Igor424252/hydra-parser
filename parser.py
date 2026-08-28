import json
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://thelastgame.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# НАСТРОЙКА: Сколько страниц сайта обходить?
# На одной странице 10 игр. Если поставить 5, соберет 50 самых свежих игр.
MAX_PAGES = 5 

def parse_games():
    downloads = []
    
    for page in range(1, MAX_PAGES + 1):
        # Если страница первая — ссылка обычная, если дальше — добавляем /page/X/
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page}/"
            
        print(f"Парсим страницу {page} из {MAX_PAGES}... Ссылка: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Propпустили страницу {page}, ошибка: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            game_blocks = soup.find_all('h2')
            
            if not game_blocks:
                print("Игры на странице не найдены. Возможно, поменялась верстка.")
                break

            for block in game_blocks:
                link_tag = block.find('a')
                if not link_tag:
                    continue
                    
                title = link_tag.text.strip()
                game_url = link_tag['href']
                
                download_entry = {
                    "title": title,
                    "uris": [game_url],
                    "uploadDate": f"Страница {page}",
                    "fileSize": "Уточняется на сайте",
                    "descriptionHtml": f'<a href="{game_url}">Инструкция и скачивание на TheLastGame</a>',
                    "linksHidden": False
                }
                downloads.append(download_entry)
                
            # Небольшая пауза в 1 секунду между страницами, чтобы сайт нас не забанил
            time.sleep(1)
            
        except Exception as e:
            print(f"Ошибка при обработке страницы {page}: {e}")
            continue

    return downloads

def main():
    game_list = parse_games()
    
    hydra_source = {
        "name": "TheLastGame Расширенный",
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"Сборка завершена! Всего сохранено игр: {len(game_list)}")

if __name__ == "__main__":
    main()
