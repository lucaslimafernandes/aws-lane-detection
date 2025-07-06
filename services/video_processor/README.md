# Video Processor


Este serviço consome mensagens da fila SQS, faz o download de vídeos do S3, realiza o processamento com OpenCV para detecção de faixas e envia os resultados processados de volta ao S3.

Baseado no artigo "Vision-Based Robust Lane Detection and Tracking in Challenging Conditions"

Autor: Lucas Lima Fernandes

## Tecnologias

- Python 3.12
- OpenCV (cv2)
- boto3 (AWS SDK for Python)
- Docker

## Estrutura Esperada

Este serviço faz parte de um sistema composto por múltiplos serviços:

```plaintext
services/
├── api # Interface REST com FastAPI (envia vídeos e mensagens)
└── video_processor # Este serviço (consumidor do SQS + processador de vídeo)
```

## Funcionamento

1. O serviço entra em loop contínuo (daemon-like).
2. A cada 10 segundos, verifica se há novas mensagens na fila `future-processing`.
3. Quando há mensagem:
   - Faz download do vídeo do bucket `lane-bucket`.
   - Processa os frames aplicando o algoritmo de detecção de faixas.
   - Salva os frames e resultados processados no S3, em uma pasta única para cada vídeo.


## Requisitos

- Docker
- LocalStack
- Bucket S3 (`lane-bucket`) e fila SQS (`future-processing`) previamente criados.


## Configuração

Copie o arquivo de variáveis de ambiente:

example.env para .env e configure conforme necessidades.

