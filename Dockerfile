FROM ubuntu:18.04
RUN apt-get update && apt-get install -y libfontforge2 wget \
    libopenjp2-7 \
    libfontconfig1 \
    python3 \
    python3-pip \
    git
RUN git clone https://github.com/SwiftLaTeX/htmlizer.git /app && \
    pip3 install -r /app/requirements.txt && \
    wget http://130.216.216.196/201812/pdf2htmlEX -O /usr/bin/pdf2htmlEX && \
    wget http://130.216.216.196/201812/libpoppler.so.73 -O /usr/lib/libpoppler.so.73 && \
    chmod +x /usr/bin/pdf2htmlEX

WORKDIR /app
CMD ["python3", "WSGI.py"]


