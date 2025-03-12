FROM python:3.13

WORKDIR /app

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH"

# Указываем переменную среды для PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --no-root

COPY . /app/

CMD ["poetry", "run", "python", "main.py"]
