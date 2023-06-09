FROM python:3-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# .env has to be in the same directory as Dockerfile
COPY . .
EXPOSE 3001
#TODO Prod and Dev env vars
#TODO add .env in CD process 
CMD ["dotenv" , "run", "python3", "-u", "./api/index.py"]