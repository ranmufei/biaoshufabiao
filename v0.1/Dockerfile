FROM ranmufei/biaoshufabiao:latest

ENV ALPINE_VERSION=3.6

# ranmufei/biaoshufabiao layer have include python lib: beautifulsoup4 openpyxl requests urllib3 xlrd xlwt PyMySQL

COPY run.sh /

RUN  chmod 777 /run.sh

# so next add cron

RUN apk add crond && \
    rm -r /var/lib/apt/lists/*

WORKDIR /

ENTRYPOINT sh -C './run.sh';'sh'
#ENTRYPOINT ["/usr/bin/dumb-init", "bash", "/entrypoint.sh"]