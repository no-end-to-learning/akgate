FROM python:3.8

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt -i

COPY . .

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
