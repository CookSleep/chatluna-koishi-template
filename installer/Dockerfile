FROM docker:27-cli

RUN apk add --no-cache docker-cli-compose

WORKDIR /template

COPY .env.example docker-compose.yml docker-compose.koishi.yml ./
COPY koishi ./koishi
COPY installer/install.sh /usr/local/bin/chatluna-template-install

RUN chmod +x /usr/local/bin/chatluna-template-install

ENTRYPOINT ["chatluna-template-install"]
