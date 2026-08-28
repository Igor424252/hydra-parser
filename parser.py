import json
from curl_cffi import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

BASE_URL = "https://thelastgame.org"

def get_max_pages(session):
    """Функция автоматически находит последнюю страницу на сайте"""
    try:
        response = session.get(BASE_URL, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Ищем блок пагинации
            navigation = soup.find('div', class_='navigation') or soup.find('div', class_='pages')
            if navigation:
                links = navigation.find_all('a')
                page_numbers = []
                for link in links:
                    if link.text.isdigit():
                        page_numbers.append(int(link.text))
                if page_numbers:
                    return max(page_numbers)
    except Exception as e:
        print(f"Не удалось определить максимальное число страниц: {e}")
    return 100  # Запасной вариант, если пагинация не спарсилась

def parse_games():
    downloads = []
    
    with requests.Session() as session:
        # Автоматически определяем, сколько страниц на сайте всего
        max_pages = get_max_pages(session)
        print(f"Найдено страниц для обхода: {max_pages}")
        
        for page in range(1, max_pages + 1):
            url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
            print(f"Парсим страницу {page} из {max_pages}...")
            
            try:
                # Ставим быстрый таймаут, чтобы скрипт не зависал долго на плохих страницах
                response = session.get(url, impersonate="chrome120", timeout=10)
                if response.status_code != 200:
                    print(f"Пропущена страница {page} (код {response.status_code})")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                page_games_count = 0
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

                    # Чтобы скрипт не падал по тайм-ауту GitHub Actions на 1000+ страницах, 
                    # мы НЕ заходим внутрь каждой игры, а берем прямую ссылку на пост.
                    # Hydra Launcher это отлично переваривает!
                    download_entry = {
                        "title": title,
                        "uris": [game_url],
                        "uploadDate": f"Страница {page}",
                        "fileSize": "Доступно на сайте",
                        "descriptionHtml": f'<a href="{game_url}">Открыть страницу загрузки игры</a>',
                        "linksHidden": False
                    }
                    downloads.append(download_entry)
                    page_games_count += 1
                
                # Маленькая пауза, чтобы не нагружать сайт
                time.sleep(0.3)
                
            except Exception as e:
                print(f"Ошибка на странице {page}: {e}")
                continue

    return downloads

def main():
    game_list = parse_games()
    
    current_time = datetime.utcnow() + timedelta(hours=5)
    time_str = current_time.strftime("%d.%m %H:%M")
    source_name = f"TheLastGame [Вся База: {time_str}]"
    
    hydra_source = {
        "name": source_name,
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[УСПЕХ] Сборка всей базы завершена!")
    print(f"Всего игр сохранено в файл: {len(game_list)}")

if __name__ == "__main__":
    main()
