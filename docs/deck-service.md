---
tags:
Важность:
---
#### *Заметка сделана 27 февр. 2026*

---

## DTOs:

### DeckSimpleView:

```python
class DeckSimpleView:
	id_: uuid
	title: str
	description: str
	is_public: bool

```

### DeckDetailedView

```python
class DeckDetailedView:
	id_: uuid
	title: str
	description: str
	is_public: bool,
	created_at: timestamp,
	updated_at: timestamp
```
---
## DeckService:

### get_decks_for_user;
```python
def get_decks_for_user(
	actor_id: uuid,
	offset: int,
	limit: int
	) -> tuple[DeckSimpleView]
```
Описание: Возвращает постраничный список простых представлений колод (DeckSimpleView) для указанного пользователя; используйте offset/limit для пагинации.

---

### create_deck;
```python
def create_deck(
	actor_id: uuid,
	name: str,
	desc: str,
	is_public: bool = False
) -> DeckSimpleView
```
Описание: Создаёт новую колоду; проверяет, что name не пустое, и возвращает DeckSimpleView с базовыми полями.

---
### update_deck;
```python
def update_deck(
	actor_id: uuid,
	new_name: str | None = None,
	new_desc: str | None = None,
	is_public: bool | None = None
) -> DeckSimpleView
```
Описание: Частичное обновление полей колоды — поля, переданные как None, остаются без изменений; возвращает обновлённое DeckSimpleView.

---
### delete_deck;

```python
def delete_deck(actor_id: uuid, deck_id: uuid) -> DeckSimpleView;
```
Описание: Удаляет (или архивирует) колоду в зависимости от реализации; возвращает представление удалённой колоды или бросает NotFound/PermissionDenied.

---
### get_deck_details;
```python
def get_deck_details(actor_id: uuid, deck_id: uuid) -> DeckDetailedView
```
Описание: Возвращает подробную информацию о колоде (DeckDetailedView) с метками created_at и updated_at; проверяет права доступа при необходимости.

---
## Ссылки на другие страницы:
...
