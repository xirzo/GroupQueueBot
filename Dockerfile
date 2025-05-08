FROM alpine:3.17.0

RUN apk add --no-cache \
    python3 \
    py3-pip

RUN pip3 install --no-cache-dir \
    pyTelegramBotAPI \
    python-dotenv \
    requests

RUN addgroup -S group-queue-bot && \
    adduser -S group-queue-bot -G group-queue-bot

USER group-queue-bot

WORKDIR /app
COPY --chown=group-queue-bot:group-queue-bot \
    main.py \
    .

ENTRYPOINT ["/usr/bin/python3", "main.py"]
