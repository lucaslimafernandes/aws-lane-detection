# Notifier Service

Este serviço recebe mensagens de um tópico SNS (Amazon Simple Notification Service) e envia notificações para um bot do Telegram.


## Visão Geral

Este microserviço expõe um endpoint HTTP (`/sns-telegram`) que recebe notificações JSON do SNS e as envia para um chat do Telegram usando a Bot API.


## Estrutura

```
notifier/
├── main.py              # FastAPI App que recebe as notificações
├── requirements.txt     # Dependências Python
├── Dockerfile           # Container do serviço
├── .env                 # Variáveis de ambiente (token/chat ID)
└── services/
    └── telegram.py      # Lógica para enviar mensagens ao Telegram
```


## Variáveis de Ambiente

Crie um arquivo `.env` com o seguinte conteúdo:

```env
TELEGRAM_TOKEN="bot0123:ABCDeFgHiJkLmNoPqRsTuVwXyZ"
TELEGRAM_CHAT_ID="-123456789"
```

- **TELEGRAM_TOKEN**: Token do seu bot (criado via @BotFather)
- **TELEGRAM_CHAT_ID**: ID do chat para onde as mensagens serão enviadas. Pode ser obtido usando [@userinfobot](https://t.me/userinfobot)


## Instalação

### Usando Docker

```bash
docker build -t notifier .
docker run --env-file .env -p 8081:8081 notifier
```

### Localmente

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8081
```


## Teste

```bash
curl -X POST http://localhost:8081/sns-telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "🚨 Alerta de teste!"}'
```

Você deverá receber a mensagem no seu Telegram 


## Integração com LocalStack SNS

1. Criar tópico SNS:

```bash
awslocal sns create-topic --name alertas
```

2. Criar subscription apontando para este serviço:

```bash
awslocal sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:000000000000:alertas \
  --protocol http \
  --notification-endpoint http://localhost:8081/sns-telegram
```

3. Enviar mensagem para o tópico:

```bash
awslocal sns publish \
  --topic-arn arn:aws:sns:us-east-1:000000000000:alertas \
  --message "🔔 Notificação enviada com sucesso!"
```


## Notas

- O SNS envia mensagens com o campo `Message` como string.
- Se quiser adaptar o serviço para lidar com o payload padrão do SNS (com `Type`, `Timestamp`, etc.), edite o handler `handle_sns`.


## Status

- [x] Envio via Telegram Bot
- [x] Recebe POST padrão do SNS
- [ ] Suporte a múltiplos canais (e-mail, webhook, etc.)
