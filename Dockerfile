FROM python:3.13

WORKDIR /app

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без создания виртуального окружения
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction

# Копируем все файлы проекта
COPY . /app/

CMD ["python", "main.py"]
