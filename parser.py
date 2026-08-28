import json
from curl_cffi import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

BASE_URL = "https://thelastgame.org"
MAX_PAGES = 5  # Сколько страниц обходить

def parse_games():
    downloads = []
    
    with requests.Session() as session:
        for page in range(1, MAX_PAGES + 1):
            url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
            print(f"Запрос к странице {page}: {url}")
            
            try:
                response = session.get(url, impersonate="chrome120", timeout=15)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link_tag in links:
                    game_url = link_tag['href']
                    title = link_tag.text.strip()
                    
                    if not game_url.startswith(BASE_URL) or len(game_url) <= len(BASE_URL):
                        continue
                        
                    black_list = ["do=", "rules", "index.php", "/page/", "category", "search", "tags", "about"]
                    if any(garbage in game_url for garbage in black_list):
                        continue
                        
                    if not title or len(title) < 3 or title in ["Регистрация", "Вход", "Правила", "Главная", "Популярные игры"]:
                        continue

                    if any(d["title"] == title for d in downloads):
                        continue

                    print(f" -> Страница игры: {title}")
                    try:
                        inner_res = session.get(game_url, impersonate="chrome120", timeout=10)
                        if inner_res.status_code == 200:
                            inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
                            
                            download_uris = []
                            for a_tag in inner_soup.find_all('a', href=True):
                                href = a_tag['href']
                                if ".torrent" in href or "magnet:" in href or "datanodes" in href or "download" in href:
                                    download_uris.append(href)
                            
                            if not download_uris:
                                download_uris = [game_url]
                        else:
                            download_uris = [game_url]
                    except Exception as inner_err:
                        download_uris = [game_url]
                    
                    time.sleep(0.5)

                    download_entry = {
                        "title": title,
                        "uris": download_uris,
                        "uploadDate": f"Страница {page}",
                        "fileSize": "Уточняется на сайте",
                        "descriptionHtml": f'<a href="{game_url}">Инструкция на TheLastGame</a>',
                        "linksHidden": False
                    }
                    downloads.append(download_entry)
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"Ошибка на странице {page}: {e}")
                continue

    return downloads

def main():
    game_list = parse_games()
    
    # Создаем метку времени (корректируем UTC время GitHub под ваш часовой пояс, добавим примерные +5 часов)
    current_time = datetime.utcnow() + timedelta(hours=5)
    time_str = current_time.strftime("%d.%m %H:%M")
    
    # Динамическое имя, которое заставит Hydra Launcher сбросить кэш
    source_name = f"TheLastGame [Обновлено: {time_str}]"
    
    hydra_source = {
        "name": source_name,
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[ФИНАЛ] Сборка завершена. Источник назван: '{source_name}'. Игр: {len(game_list)}")

if __name__ == "__main__":
    main()
