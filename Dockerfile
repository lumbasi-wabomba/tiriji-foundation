
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=tiriji.settings 
# ENV SECRET_KEY= {{SECRET_KEY}}
ENV DEBUG=False

WORKDIR /core

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p media staticfiles

ENV STATIC_ROOT=/core/staticfiles
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]