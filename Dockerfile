FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit requests pandas
COPY app.py .
RUN mkdir data
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]