import json
from curl_cffi import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

BASE_URL = "https://thelastgame.org"

def parse_games():
    downloads = []
    page = 1
    
    # Открываем сессию с имитацией реального браузера Google Chrome
    with requests.Session() as session:
        while True:
            if page == 1:
                url = BASE_URL
            else:
                url = f"{BASE_URL}/page/{page}/"
                
            print(f"Парсим страницу {page} -> {url}")
            
            try:
                response = session.get(url, impersonate="chrome120", timeout=10)
                
                # Если сайт вернул 404, значит мы долистали до самого конца каталога
                if response.status_code == 404:
                    print(f"Достигли конца сайта на странице {page}. Сборка окончена.")
                    break
                elif response.status_code != 200:
                    print(f"Ошибка загрузки страницы {page}: {response.status_code}. Пробуем дальше.")
                    page += 1
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                page_games_count = 0
                for link_tag in links:
                    game_url = link_tag['href']
                    title = link_tag.text.strip()
                    
                    # Проверяем, что ссылка ведет именно на страницу с игрой
                    if not game_url.startswith(BASE_URL) or len(game_url) <= len(BASE_URL):
                        continue
                        
                    # Фильтруем служебный мусор (комментарии, правила, регистрацию)
                    black_list = ["do=", "rules", "index.php", "/page/", "category", "search", "tags", "about"]
                    if any(garbage in game_url for garbage in black_list):
                        continue
                        
                    # Отсекаем пустые ссылки и пункты меню
                    if not title or len(title) < 3 or title in ["Регистрация", "Вход", "Правила", "Главная", "Популярные игры"]:
                        continue

                    # Защита от дублирования игр в итоговом файле
                    if any(d["title"] == title for d in downloads):
                        continue

                    # Формируем карточку игры под стандарт Hydra Launcher
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
                
                print(f"Cо страницы {page} успешно добавлено новых игр: {page_games_count}")
                
                # Если на странице вообще не нашлось уникальных игр, останавливаемся
                if page_games_count == 0:
                    print(f"На странице {page} нет новых игр. Завершаем обход.")
                    break
                
                page += 1
                time.sleep(0.1) # Микропауза для стабильности, чтобы не терять скорость
                
            except Exception as e:
                print(f"Ошибка на странице {page}: {e}")
                page += 1
                continue

    return downloads

def main():
    game_list = parse_games()
    
    # Корректируем время под ваш часовой пояс (+5 часов к UTC)
    current_time = datetime.utcnow() + timedelta(hours=5)
    time_str = current_time.strftime("%d.%m %H:%M")
    
    # Генерируем уникальный ID источника на основе текущей минуты.
    # Это заставит Hydra Launcher принудительно обновлять базу игр у вас на ПК!
    unique_timestamp = current_time.strftime("%Y%m%d%H%M")
    
    hydra_source = {
        "id": f"thelastgame-source-{unique_timestamp}", # Каждое обновление ID будет новым!
        "name": f"TheLastGame [База: {time_str}]",
        "downloads": game_list
    }
    
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
        
    print(f"\n[УСПЕХ] Сборка всей базы завершена!")
    print(f"Всего игр сохранено в файл: {len(game_list)}")
    print(f"Новый ID источника: thelastgame-source-{unique_timestamp}")

if __name__ == "__main__":
    main()
