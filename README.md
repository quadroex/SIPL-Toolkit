# SIPL Language Toolkit

[![CI](https://github.com/quadroex/SIPL-Toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/quadroex/SIPL-Toolkit/actions/workflows/ci.yml)

Навчальний набір інструментів для мови SIPL з курсу теорії програмування.

## Обрані завдання

| ID | Зміст | Бали |
|---|---|---:|
| CORE-01 | Формальна граматика SIPL | 0.5 |
| CORE-02 | Парсер і типізоване AST з SourceSpan | 1.5 |
| CORE-03 | Інтерпретатор SIPL | 2.0 |
| CORE-04 | Подієва модель виконання та trace | 1.0 |
| CORE-05 | CLI та JSON-режим | 1.0 |
| VIS-01 | Візуалізація дерева синтаксичного виводу | 1.5 |
| SEM-01 | Автоматична побудова семантичного терму | 2.0 |
| REL-01 | Автоматичні перевірки в GitHub Actions | 0.5 |

Загальна заявлена оцінка становить 10 балів.

## Реалізовані можливості

- граматика SIPL у форматі Lark;
- власне типізоване AST з `SourceSpan`;
- інтерпретатор із лімітом кроків;
- подієвий trace у текстовому та JSON-форматах;
- команди `check`, `parse`, `run`, `trace`, `term`, `tree`;
- дерево синтаксичного виводу у text, JSON, DOT та SVG;
- семантичні терми у позначеннях курсу;
- автоматичні тести, перевірка типів, стилю та збірки в CI.

## Встановлення

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Запуск

```powershell
sipl check examples\multiply.sipl
sipl parse examples\multiply.sipl
sipl run examples\multiply.sipl --state X=4,Y=3
sipl run examples\multiply.sipl --state X=4,Y=3 --json
sipl trace examples\multiply.sipl --state X=4,Y=3
sipl trace examples\multiply.sipl --state X=4,Y=3 --json
sipl term examples\multiply.sipl
sipl tree examples\multiply.sipl --format text
sipl tree examples\multiply.sipl --format json --output out\tree.json
sipl tree examples\multiply.sipl --format dot --output out\tree.dot
sipl tree examples\multiply.sipl --format svg --output out\tree.svg
```

Очікуваний кінцевий стан

```text
K = 0
R = 12
X = 4
Y = 3
```

## Підтримуваний синтаксис

Підтримуються присвоювання, послідовне виконання, `if`, `while`, `begin/end`, `skip`, цілі числа, змінні, операції `+`, `-`, `*`, порівняння `=` і `>`, логічні операції `or`, `not`, `∨` та `¬`.

Складене тіло розгалуження або циклу записується в блоці `begin/end`. Це усуває неоднозначність оператора послідовного виконання відповідно до пріоритетів конструкцій SIPL.

Семантичні терми будуються рекурсивно з AST у позначеннях курсу `AS`, `IF`, `WH`, `S¹`, `S²`, `·` та `⇒`. Дерево синтаксичного виводу будується з реального результату парсингу. Кожен вузол містить позицію та відповідний фрагмент вихідного тексту.

## Тести

```powershell
python -m ruff check .
python -m mypy src
python -m pytest --cov=sipl --cov-report=term-missing
python -m build
```

Проєкт не прив'язаний до конкретного варіанта практичної роботи. Він обробляє довільні програми в межах зафіксованої граматики SIPL.

## Документація

- [Архітектура](docs/architecture.md)
- [JSON-режим і коди завершення](docs/json.md)
- [План демонстрації на захисті](docs/defense.md)

## Обмеження

Реалізовано базову версію SIPL із матеріалів курсу. Немає введення-виведення, процедур, складних типів і рекурсивних функцій. Складене тіло `if` або `while` потрібно оформлювати блоком `begin/end`.
