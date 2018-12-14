FROM ubuntu:18.04
RUN apt-get update && apt-get install -y libfontforge2 \
    libopenjp2-7 \
    libfontconfig1 \
    python3 \
    python3-pip \
    git && \
    git clone https://github.com/SwiftLaTeX/htmlizer.git /app && \
    pip3 install -r /app/requirements.txt
WORKDIR /app
CMD ["python3", "WSGI.py"]


