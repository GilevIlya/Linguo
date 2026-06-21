#### *Заметка сделана 27 февр. 2026*

# CardService Documentation
Описание сервиса для управления карточками (Card), включая создание, обновление, удаление и получение детальной информации.

---
## DTOs:
### CardSimpleView:
Базовая модель представления карточки.
```python
class CardView:
    """
    Упрощенное представление карточки.
    """
	id_: uuid,
	term: str,      # Термин/слово
	def_: str,      # Определение
	deck_id: uuid,  # ID колоды
	
```

### CardDetailedView:

##### AdditionalFields:
Модель для дополнительных полей карточки (например, картинки, аудио).
```python
class AdditionalFields:
	type_: str,   # Тип поля (image, sound, context, synonyms)
	content: Any  # Содержимое поля
	
```
##### View:
Полное представление карточки со всеми дополнительными полями.
```python
class CardDetailedView:
	id_: uuid,
	term: str,
	def_: str,
	deck_id: uuid,
	additional_fields: tuple[AdditionalFields],
	created_at: timestamp,
	updated_at: timestamp
```


---
## CardService:
Сервис, реализующий бизнес-логику работы с карточками.

### create_card:
Создает новую карточку в указанной колоде.
```python
def create_card(
	actor_id: uuid,                # ID пользователя, выполняющего действие
	term: str,                     # Термин
	def_: str,                     # Определение
	deck_id: UUID,                 # ID целевой колоды
	sound: BinaryIO | None = None, # (Опционально) Аудио файл
	image: BinaryIO | None = None, # (Опционально) Изображение
	context: str | None = None,    # (Опционально) Пример использования
	synonyms: tuple[str] | None = None # (Опционально) Список синонимов
); -> CardSimpleView
```
---
### delete_card:
Удаляет карточку по её ID.
```python
def delete_card(
	actor_id: uuid,
	id_: uuid
); -> CardSimpleView
```

### update_card:
Обновляет данные существующей карточки.
```python
def update_card(
	actor_id: uuid,
	card_id: uuid,
	term: str | None,              # Новый термин (если нужно обновить)
	def_: str | None = None,       # Новое определение
	sound: BinaryIO | None = None, # Обновить аудио
	image: BinaryIO | None = None, # Обновить изображение
	context: str | None = None,    # Обновить контекст
	synonyms: tuple[str] | None = None # Обновить синонимы
); -> CardSimpleView
```

### change_card_deck;
Перемещает карточку в другую колоду.
```python
def change_card_deck(
	actor_id: uuid,
	card_id: uuid,
	new_deck_id: uuid,
); -> CardSimpleView
```

### get_card_details;
Получает полную информацию о карточке, включая дополнительные поля.
```python
def get_card_details(actor_id: uuid, card_id: uuid); -> CardDetailedView
```

---
### get_cards_by_deck;
Получаем все карты из колоды
```python
def get_cards_by_deck(actor_id: uuid, deck_id: uuid) -> tuple[CardSingleView]
```

## Ссылки на другие страницы:
...
