# Приклади SIPL

У корені каталогу залишено основні приклади `multiply.sipl`, `power.sipl` і `branch.sipl`. Додаткові файли розділено на правильні програми та приклади помилок.

## Правильні програми

| Файл | Вхідні дані | Очікуваний результат |
|---|---|---|
| `valid/simple_add.sipl` | `X=7,Y=5` | `R=12` |
| `valid/factorial.sipl` | `N=5` | `R=120`, `K=0` |
| `valid/sum_to_n.sipl` | `N=5` | `S=15`, `K=0` |
| `valid/logical_branch.sipl` | `X=2,Y=3` | `R=5`, `FLAG=1` |
| `valid/nested_loops.sipl` | `A=3,B=4` | `R=12`, `I=0`, `J=0` |

Приклад запуску

```powershell
.\.venv\Scripts\sipl.exe run .\examples\valid\factorial.sipl --state N=5
```

## Приклади помилок

| Файл | Очікувана поведінка |
|---|---|
| `errors/syntax_missing_end.sipl` | Повідомлення про відсутній `end` |
| `errors/syntax_missing_else.sipl` | Повідомлення про відсутню гілку `else` |
| `errors/syntax_invalid_operator.sipl` | Повідомлення про непідтримуваний оператор `/` |
| `errors/runtime_undefined_variable.sipl` | Помилка невизначеної змінної `MISSING` |
| `errors/runtime_infinite_loop.sipl` | Зупинка після перевищення `--max-steps` |

Команди для перевірки

```powershell
.\.venv\Scripts\sipl.exe check .\examples\errors\syntax_missing_end.sipl
.\.venv\Scripts\sipl.exe run .\examples\errors\runtime_undefined_variable.sipl --state X=2
.\.venv\Scripts\sipl.exe run .\examples\errors\runtime_infinite_loop.sipl --state X=1 --max-steps 20
```
