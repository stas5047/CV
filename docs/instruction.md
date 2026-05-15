# Инструкции по настройке и обучению AeroVision для нетехнического пользователя

## Что я уже сделал локально

Я выполнил части, которые не требуют ваших внешних аккаунтов или обученных файлов модели:

1. Создал локальный файл `.env` из `.env.example`.
2. Заменил демонстрационные секреты-заглушки случайными значениями.
3. Создал папки хранилища в `storage/`.
4. Запустил приложение через Docker Compose с изолированным именем проекта:

```powershell
docker compose --project-name aerovision_local_demo --env-file .env up --build -d
```

5. Проверил работу сервисов:
   - PostgreSQL работает корректно.
   - Бэкенд отвечает по адресу `http://localhost:8000/api/health`.
   - База данных доступна по адресу `http://localhost:8000/api/health/db`.
   - Фронтенд открывается по адресу `http://localhost:5173`.
   - CV-воркер запущен и выбрал режим CPU.
   - Вход с предустановленными данными администратора работает.

Приложение можно открыть прямо сейчас, однако реальное обнаружение дронов не заработает до тех пор, пока не будет загружен и зарегистрирован файл модели YOLO.

## Что нужно сделать вам

Вы должны выполнить часть, связанную с обучением модели, так как для этого требуется внешний облачный аккаунт для ноутбуков и обученный файл модели.

Вам необходимо подготовить следующие файлы:

```text
storage/models/yolo26s-seraphim-subset-v1/weights.pt
storage/models/yolo26s-seraphim-subset-v1/model_card.json
storage/models/yolo26s-seraphim-subset-v1/metrics.json
```

Самый важный файл:

```text
weights.pt
```

Без файла `weights.pt` приложение запустится, но не сможет обрабатывать загруженные изображения и видео.

## Важные правила безопасности

1. Не добавляйте файл `.env` в коммит.
2. Не добавляйте в коммит веса модели, датасеты, загружаемые файлы и сгенерированные результаты.
3. Не вставляйте содержимое `.env` или пароль администратора в чат без явной необходимости.
4. Используйте этот проект только для обнаружения объектов на загружаемых изображениях и видео. Это не система управления дронами или наведения.

## Как открыть приложение прямо сейчас

1. Откройте браузер.
2. Перейдите по адресу:

```text
http://localhost:5173
```

3. Чтобы войти как администратор, откройте файл `.env` в Блокноте:

```powershell
notepad .env
```

4. Найдите следующие строки:

```env
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
```

5. Используйте эти значения на странице входа.

Не публикуйте и не передавайте пароль третьим лицам. Он предназначен только для локальной демонстрации.

## Как остановить или перезапустить приложение

Остановить текущую локальную демонстрацию:

```powershell
docker compose --project-name aerovision_local_demo --env-file .env down
```

Запустить снова:

```powershell
docker compose --project-name aerovision_local_demo --env-file .env up --build -d
```

Проверить состояние сервисов:

```powershell
docker compose --project-name aerovision_local_demo --env-file .env ps
```

Посмотреть логи в случае ошибки:

```powershell
docker compose --project-name aerovision_local_demo --env-file .env logs backend
docker compose --project-name aerovision_local_demo --env-file .env logs cv-worker
docker compose --project-name aerovision_local_demo --env-file .env logs frontend
```

## Общий план дальнейших действий

Вам необходимо выполнить следующие этапы:

1. Получить датасет с дронами.
2. Обучить модель YOLO в Colab или Kaggle.
3. Скачать обученный файл `weights.pt`.
4. Разместить файлы модели в `storage/models/yolo26s-seraphim-subset-v1/`.
5. Попросить меня зарегистрировать и активировать модель.
6. Разместить несколько тестовых медиафайлов в `storage/temp/e2e/`.
7. Попросить меня провести финальную сквозную проверку.

## Этап 1 — Получение датасета

В документации проекта в качестве основного датасета указан Seraphim Drone Detection Dataset. Он доступен на Hugging Face:

```text
https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset
```

Датасет большой — около 9 ГБ. Убедитесь, что у вас достаточно свободного места на диске.

### Вариант A — Скачать через браузер

1. Откройте страницу:

```text
https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset
```

2. Создайте аккаунт на Hugging Face или войдите в существующий, если сайт этого потребует.
3. Найдите вкладку `Files and versions`.
4. Скачайте файлы датасета или архивы с данными.
5. Поместите скачанные файлы в удобное место, например:

```text
C:\Users\Kotletka\Downloads\seraphim
```

6. Распакуйте все файлы `.zip`.

После распаковки у вас должны появиться файлы изображений и файлы меток. Ожидаемая структура папок:

```text
seraphim/
  train/
    images/
    labels/
  test/
    images/
    labels/
```

Если возникнут затруднения на этом этапе, остановитесь и сообщите мне, где находится скачанная папка. Я смогу проверить и подготовить локальный датасет.

### Вариант Б — Скачать через ноутбук

Если скачать файлы через браузер затруднительно, Colab может загрузить датасет в облаке. Это позволяет не заполнять память компьютера, однако в конце вам всё равно нужно будет скачать итоговые обученные артефакты.

Используйте следующий код в ячейке Colab:

```python
!pip install -q huggingface_hub

from huggingface_hub import snapshot_download
from pathlib import Path
import zipfile

repo_path = Path(snapshot_download(
    repo_id="lgrzybowski/seraphim-drone-detection-dataset",
    repo_type="dataset",
    local_dir="/content/seraphim_raw",
))

for zip_path in repo_path.rglob("*.zip"):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(zip_path.parent)

print("Датасет загружен в:", repo_path)
```

## Этап 2 — Обучение в Google Colab

Colab обычно удобнее для начинающих, чем Kaggle.

### 2.1 Открыть Colab

1. Откройте:

```text
https://colab.research.google.com/
```

2. Войдите с помощью аккаунта Google.
3. Если появится всплывающее окно, выберите `Upload`.
4. Загрузите файл проекта:

```text
training/notebooks/yolo26s_finetune_template.ipynb
```

Если всплывающее окно не появилось:

1. Нажмите `File`.
2. Нажмите `Upload notebook`.
3. Выберите файл:

```text
training/notebooks/yolo26s_finetune_template.ipynb
```

### 2.2 Включить GPU

1. В верхнем меню нажмите `Runtime`.
2. Нажмите `Change runtime type`.
3. В поле `Hardware accelerator` выберите GPU, например `T4 GPU`.
4. Нажмите `Save`.

Если GPU недоступен, подождите и повторите попытку позже. Доступность бесплатного GPU меняется. Обучение на CPU будет очень медленным.

### 2.3 Установить пакеты

Добавьте новую ячейку с кодом в начало ноутбука и выполните:

```python
!pip install -q ultralytics huggingface_hub
```

### 2.4 Скачать датасет в Colab

Добавьте новую ячейку и выполните:

```python
from huggingface_hub import snapshot_download
from pathlib import Path
import zipfile

repo_path = Path(snapshot_download(
    repo_id="lgrzybowski/seraphim-drone-detection-dataset",
    repo_type="dataset",
    local_dir="/content/seraphim_raw",
))

for zip_path in repo_path.rglob("*.zip"):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(zip_path.parent)

print("Датасет готов:", repo_path)
```

### 2.5 Создать файл `data.yaml` для YOLO

Добавьте новую ячейку и выполните:

```python
from pathlib import Path

dataset_root = Path("/content/seraphim_raw")

data_yaml = dataset_root / "data.yaml"
data_yaml.write_text(
    f"""path: {dataset_root}
train: train/images
val: test/images
test: test/images
nc: 1
names:
  0: drone
""",
    encoding="utf-8",
)

print(data_yaml.read_text())
```

Здесь для обучения используются тренировочные изображения, а для валидации и тестирования — тестовые. Этого достаточно для запуска приложения. Более строгое разбиение для финальных исследований можно подготовить позднее.

### 2.6 Обучить YOLO26s

Найдите в ноутбуке ячейку, содержащую:

```python
DATA_YAML = '/kaggle/input/aerovision-seraphim-subset/data.yaml'
MODEL_WEIGHTS = 'yolo26s.pt'
```

Замените на:

```python
DATA_YAML = '/content/seraphim_raw/data.yaml'
MODEL_WEIGHTS = 'yolo26s.pt'
```

Затем запустите ячейку обучения.

Ожидаемая команда обучения внутри ноутбука:

```python
from ultralytics import YOLO

DATA_YAML = '/content/seraphim_raw/data.yaml'
MODEL_WEIGHTS = 'yolo26s.pt'

model = YOLO(MODEL_WEIGHTS)
model.train(
    data=DATA_YAML,
    task='detect',
    imgsz=640,
    epochs=50,
    patience=10,
    seed=42,
    name='yolo26s-seraphim-subset-v1',
)
```

Обучение может занять много времени. Не закрывайте вкладку браузера. Если Colab отключится, используйте лучший доступный чекпоинт из папки с результатами обучения.

### 2.7 Найти обученные веса

После завершения обучения выполните:

```python
!find /content -name "best.pt" -o -name "last.pt"
```

Обычно лучшая модель находится по пути вида:

```text
/content/runs/detect/yolo26s-seraphim-subset-v1/weights/best.pt
```

Используйте `best.pt` как финальную модель. Переименуйте файл в:

```text
weights.pt
```

### 2.8 Скачать `weights.pt`

Выполните:

```python
from google.colab import files
files.download('/content/runs/detect/yolo26s-seraphim-subset-v1/weights/best.pt')
```

Браузер скачает файл `best.pt`. Переименуйте его на компьютере в:

```text
weights.pt
```

## Этап 3 — Если YOLO26 не работает

YOLO26 является основным обязательным вариантом. Используйте резервный только в том случае, если Colab сообщит о недоступности весов или пакета YOLO26.

Резервный вариант:

1. Замените:

```python
MODEL_WEIGHTS = 'yolo26s.pt'
```

на:

```python
MODEL_WEIGHTS = 'yolo11s.pt'
```

2. Проведите обучение заново.
3. Явно сообщите мне:

```text
YOLO26 был недоступен. Я использовал резервный вариант YOLO11.
```

4. В карточке модели должно быть указано:

```json
"model_family": "YOLO11"
```

Не используйте YOLO11 молча, не сообщив мне об этом.

## Этап 4 — Размещение файлов модели в проекте

На вашем компьютере создайте папку:

```text
storage/models/yolo26s-seraphim-subset-v1/
```

Поместите туда файл:

```text
storage/models/yolo26s-seraphim-subset-v1/weights.pt
```

Затем скопируйте шаблон карточки модели:

```powershell
Copy-Item training/templates/model_card.placeholder.json storage/models/yolo26s-seraphim-subset-v1/model_card.json
```

Скопируйте шаблон файла метрик:

```powershell
Copy-Item training/templates/metrics.placeholder.json storage/models/yolo26s-seraphim-subset-v1/metrics.json
```

Если вы использовали резервный вариант YOLO11, откройте `model_card.json` и измените:

```json
"model_family": "YOLO26"
```

на:

```json
"model_family": "YOLO11"
```

Если обучение остановилось раньше 50 эпох из-за отключения Colab, откройте `model_card.json` и замените:

```json
"epochs": 50
```

на фактическое количество выполненных эпох.

## Этап 5 — Проверка файлов модели

Выполните из корня проекта:

```powershell
python -m pip install -e "training[dev]"

python -m aerovision_training.validate_artifacts `
  --model-card storage/models/yolo26s-seraphim-subset-v1/model_card.json `
  --metrics storage/models/yolo26s-seraphim-subset-v1/metrics.json
```

Успешный результат содержит:

```text
VALID
```

Если проверка завершится ошибкой, пришлите мне текст ошибки.

## Этап 6 — Попросите меня зарегистрировать и активировать модель

После размещения файлов сообщите мне:

```text
Файлы модели готовы в storage/models/yolo26s-seraphim-subset-v1. Пожалуйста, зарегистрируйте и активируйте модель.
```

После этого я смогу:

1. Войти с локальными учётными данными администратора из `.env`.
2. Зарегистрировать `models/yolo26s-seraphim-subset-v1/weights.pt`.
3. Активировать модель.
4. Импортировать метрики.
5. Провести проверку приложения.

## Этап 7 — Подготовка тестовых медиафайлов

Создайте папку:

```powershell
New-Item -ItemType Directory -Force storage/temp/e2e
```

Поместите туда три файла:

```text
storage/temp/e2e/drone-image.jpg
storage/temp/e2e/drone-video.mp4
storage/temp/e2e/no-drone.jpg
```

Требования:

- `drone-image.jpg`: изображение с как минимум одним дроном.
- `drone-video.mp4`: короткое видео с дроном.
- `no-drone.jpg`: изображение без дрона.

Для тестирования лучше подходят короткие видео. По возможности используйте ролики длиной несколько секунд.

Затем сообщите мне:

```text
Тестовые медиафайлы готовы в storage/temp/e2e.
```

## Этап 8 — Что я сделаю после вас

После того как файлы модели и тестовые медиафайлы будут готовы, я выполню:

1. Проверку запуска Docker.
2. Проверку здоровья бэкенда и базы данных.
3. Вход под администратором.
4. Регистрацию и активацию модели.
5. Сквозное тестирование обработки изображений.
6. Сквозное тестирование обработки видео.
7. Сквозное тестирование на отсутствие обнаружения.
8. Проверку скачивания CSV.
9. Проверку скачивания JSON.
10. Проверку скачивания аннотированных медиафайлов.
11. Проверку маршрутов фронтенда.
12. Проверку безопасности и конфиденциальности логов.

## Распространённые проблемы и их решения

### Colab сообщает о недоступности GPU

Подождите и повторите попытку позже. Доступность бесплатного GPU меняется. Снова откройте `Runtime` -> `Change runtime type`.

### Обучение остановилось раньше 50 эпох

Используйте лучший существующий чекпоинт. Сообщите мне, сколько эпох было выполнено.

### Браузерная загрузка идёт медленно

Это ожидаемо. Датасет и файлы модели имеют большой размер.

### Файл `weights.pt` не найден

Поищите файлы `best.pt` или `last.pt` в папке вывода ноутбука:

```python
!find /content -name "best.pt" -o -name "last.pt"
```

### Приложение открывается, но обнаружение не работает

Скорее всего, модель не зарегистрирована и не активирована, либо файл `weights.pt` отсутствует в хранилище.

### Вход в систему не работает

Откройте `.env` и используйте точные значения:

```env
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
```

Если вы изменяли `.env` после того, как база данных уже была создана, попросите меня сбросить изолированную демонстрационную базу данных.

## Полезные ссылки

- Локальный фронтенд AeroVision: `http://localhost:5173`
- Проверка здоровья бэкенда: `http://localhost:8000/api/health`
- Google Colab: `https://colab.research.google.com/`
- Ноутбуки Kaggle: `https://www.kaggle.com/code`
- Датасет Seraphim: `https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset`
- Документация по обучению Ultralytics: `https://docs.ultralytics.com/modes/train/`
- Документация CLI Ultralytics: `https://docs.ultralytics.com/usage/cli/`