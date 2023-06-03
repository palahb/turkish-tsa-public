FROM python:3.9-slim-buster

COPY . /workspace
WORKDIR /workspace

RUN apt-get update -y
RUN apt-get install wget -y

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN wget -q -r -nH --cut-dirs=1  --no-parent -e robots=off https://tulap.cmpe.boun.edu.tr/staticFiles/turkish-tsa-public/model/
RUN wget -q -r -nH --cut-dirs=1  --no-parent -e robots=off https://tulap.cmpe.boun.edu.tr/staticFiles/turkish-tsa-public/tokenizer/

EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
