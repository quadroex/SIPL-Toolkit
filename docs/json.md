# JSON-режим

Команди `check`, `run`, `trace` і `term` підтримують параметр `--json`. Команда `parse` завжди повертає AST у JSON. Команда `tree` використовує `--format json`.

Успішне виконання `run`

```json
{
  "command": "run",
  "ok": true,
  "state": {"X": 4, "R": 5},
  "steps": 1
}
```

Синтаксична помилка

```json
{
  "ok": false,
  "error": {
    "type": "SiplSyntaxError",
    "message": "expected one of: INT, LPAR, MINUS, NAME",
    "line": 1,
    "column": 12,
    "context": "begin X := end"
  }
}
```

Коди завершення

| Код | Значення |
|---:|---|
| 0 | Успішне виконання |
| 2 | Синтаксична помилка |
| 3 | Помилка виконання або ліміт кроків |
| 4 | Помилка файлу або початкового стану |

