FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY python_bidi-0.4.2-py2.py3-none-any.whl six-1.17.0-py2.py3-none-any.whl /tmp/
RUN pip install --no-cache-dir /tmp/python_bidi-0.4.2-py2.py3-none-any.whl /tmp/six-1.17.0-py2.py3-none-any.whl

COPY requirements.txt .
RUN pip uninstall -y python-bidi six 2>/dev/null || true
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
