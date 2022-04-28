FROM python:3.8-buster
COPY requirements.txt run_django.sh /root
COPY basedjango /root/basedjango
WORKDIR /root
RUN pip3 install requirements.txt
WORKDIR /root/basedjango
EXPOSE 8000
CMD ['bash /root/run_django.sh']