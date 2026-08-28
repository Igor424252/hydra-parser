import json
from curl_cffi import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://thelastgame.org/"

# НАСТРОЙКА: Количество страниц (по 10 игр на каждой)
MAX_PAGES = 5 

def parse_games():
    downloads = []
    
    # Используем сессию curl_cffi с имитацией браузера Chrome версии 120
    with requests.Session() as session:
        for page in range(1, MAX_PAGES + 1):
            if page == 1:
                url = BASE_URL
            else:
                url = f"{BASE_URL}page/{page}/"
                
            print(f"Запрос к странице {page}: {url}")
            
            try:
                # impersonate='chrome120' заставляет сайт думать, что это реальный пользователь
                response = session.get(url, impersonate="chrome120", timeout=15)
                
                if response.status_code != 200:
                    print(f"Ошибка загрузки страницы {page}: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем заголовки постов на сайте (обычно это h2 с классом или ссылкой)
                links = soup.find_all('a', href=True)
                
                page_games_count = 0
                for link_tag in links:
                    game_url = link_tag['href']
                    title = link_tag.text.strip()
                    
                    # Проверяем, что ссылка ведет именно на статью с игрой
                    # Ссылки на игры на сайте обычно имеют вид https://thelastgame.org
                    if not game_url.startswith(BASE_URL) or len(game_url) <= len(BASE_URL):
                        continue
                        
                    # Фильтруем служебные разделы сайта
                    black_list = ["do=", "rules", "index.php", "/page/", "category", "search", "tags", "about"]
                    if any(garbage in game_url for garbage in black_list):
                        continue
                        
                    # Игнорируем пустые или слишком короткие заголовки
                    if not title or len(title) < 3 or title in ["Регистрация", "Вход", "Правила", "Главная", "Популярные игры"]:
                        continue

                    # Защита от дубликатов в списке
                    if any(d["title"] == title or d["uris"][0] == game_url for d in downloads):
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
                    
                print(f"Успешно обработано игр со страницы {page}: {page_games_count}")
                
                if page_games_count == 0:
                    print("Предупреждение: Не удалось извлечь игры. Возможно, структура изменилась.")
                    
                time.sleep(2) # Пауза между страницами
                
            except Exception as e:
                print(f"Ошибка при чтении страницы {page}: {e}")
                continue

    return downloads

def main():
    game_list = parse_games()
    
    hydra_source = {
        "name": "TheLastGame Обход Блокировок",
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[ФИНАЛ] Сборка завершена. Игр добавлено: {len(game_list)}")

if __name__ == "__main__":
    main()
