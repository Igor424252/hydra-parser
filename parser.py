import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://thelastgame.org"
# Маскируемся под обычный браузер, чтобы сайт нас не заблокировал
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_games():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Не удалось открыть сайт. Ошибка: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    downloads = []

    # Находим заголовки h2, в которых лежат названия игр на главной странице
    game_blocks = soup.find_all('h2')

    for block in game_blocks:
        try:
            link_tag = block.find('a')
            if not link_tag:
                continue
                
            title = link_tag.text.strip() # Название игры
            game_url = link_tag['href']  # Ссылка на страницу игры
            
            # Для Hydra Launcher нужны ссылки на скачивание. 
            # Пока мы не зашли внутрь страницы, даем лаунчеру ссылку на саму статью
            uris = [game_url]

            # Формируем карточку игры по стандарту Hydra Launcher
            download_entry = {
                "title": title,
                "uris": uris,
                "uploadDate": "Сегодня",
                "fileSize": "Уточняется на сайте",
                "descriptionHtml": f'<a href="{game_url}">Инструкция и скачивание на TheLastGame</a>',
                "linksHidden": False
            }
            downloads.append(download_entry)
            print(f"Добавлена игра: {title}")

        except Exception as e:
            print(f"Ошибка при обработке игры: {e}")
            continue

    return downloads

def main():
    game_list = parse_games()
    
    # Главная обертка, которую требует Hydra Launcher
    hydra_source = {
        "name": "TheLastGame Авто-Источник",
        "downloads": game_list
    }
    
    # Сохраняем результат в файл json
    with open("thelastgame_source.json", "w", encoding="utf-8") as f:
        json.dump(hydra_source, f, ensure_ascii=False, indent=2)
    print("Файл базы данных успешно обновлен!")

if __name__ == "__main__":
    main()
