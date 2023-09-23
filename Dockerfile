FROM python:3.10.12-alpine3.18

RUN apk add git
RUN git clone https://github.com/kaiyga/TeaVK /home/teavk
RUN cd /home/teavk && \ 
pip install -r requirements.txt

WORKDIR /home/teavk
CMD [ "python", "main.py" ]
