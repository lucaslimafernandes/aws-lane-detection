# aws-lane-detection

Aplicação de detecção de faixas em vídeos com processamento em Python, uso de filas (SQS) e armazenamento (S3), utilizando AWS emulada via LocalStack.

Autor: Lucas Lima Fernandes

---

## Componentes do Projeto

```
services/
├── api             # API REST (FastAPI) para upload de vídeos e envio para SQS
└── video_processor # Serviço que processa vídeos da fila e salva resultados no S3
```

---

## Tecnologias Utilizadas

- Python 3.12
- FastAPI
- OpenCV (cv2)
- boto3
- Docker & Docker Compose
- LocalStack (emulando AWS S3 e SQS)

---

## Como Executar

### 1. Suba o LocalStack

```bash
docker network create localstack-net

docker run -d \
  --name localstack-main \
  --network localstack-net \
  -p 4566:4566 \
  -e SERVICES=s3,sqs \
  -e DEBUG=1 \
  localstack/localstack
```

> Alternativamente, você pode usar a interface web gratuita em https://app.localstack.cloud para criar os recursos S3 e SQS.

---

### 2. Crie os recursos necessários

Certifique-se de ter o `awslocal` instalado:

```bash
pip install awscli-local
```

Crie o bucket e a fila:

```bash
awslocal s3 mb s3://lane-bucket
awslocal sqs create-queue --queue-name future-processing
```

---

### 3. Configure os serviços

Copie os arquivos `.env` de exemplo:

```bash
cp services/api/example.env services/api/.env
cp services/video_processor/example.env services/video_processor/.env
```

> Preencha as variáveis conforme necessário. Em geral, os valores padrão já funcionam com o LocalStack.

---

### 4. Execute tudo com Docker Compose

A partir da raiz do projeto:

```bash
docker-compose up --build
```

A API estará acessível via `http://localhost:8080`

---

## Endpoints Disponíveis

| Método | Endpoint       | Descrição                              |
|--------|----------------|----------------------------------------|
| GET    | `/`            | Health check                           |
| GET    | `/buckets`     | Lista os buckets disponíveis (S3)      |
| POST   | `/upload/`     | Faz upload do vídeo e envia para a fila SQS |

Acesse a documentação interativa da API via:  
`http://localhost:8080/docs`

Utilizado vídeos do dataset: `https://github.com/vonsj0210/Multi-Lane-Detection-Dataset-with-Ground-Truth?tab=readme-ov-file`

Recomendo cortar os vídeos em pedaços de 10 segundos para teste.


## Licença

MIT
