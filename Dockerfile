FROM ubuntu:18.04
RUN apt-get update && apt-get install -y libfontforge2 \
    libopenjp2-7 \
    libfontconfig1 \
    python3 \
    python3-pip \
    git
COPY pdf2htmlEX /usr/bin/pdf2htmlEX
COPY libpoppler.so.73 /usr/lib/libpoppler.so.73
RUN git clone https://github.com/SwiftLaTeX/htmlizer.git /app && \
    pip3 install -r /app/requirements.txt && \
    chmod +x /usr/bin/pdf2htmlEX

WORKDIR /app
CMD ["python3", "WSGI.py"]


