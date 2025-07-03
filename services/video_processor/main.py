import os
import time
import boto3

import json
import uuid
import math
import shutil

import cv2
import numpy as np


from dotenv import load_dotenv

load_dotenv()

ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", None)
QUEUE_NAME   = os.getenv("SQS_QUEUE_NAME", "queue1")
QUEUE_URL    = f"{ENDPOINT_URL}/000000000000/{QUEUE_NAME}"
REGION_NAME  = os.getenv("AWS_REGION", "ue-east-1")

# sqs = boto3.client("sqs", endpoint_url=ENDPOINT_URL)  # ajuste se necessário
# s3 = boto3.client('s3')

sqs = boto3.client("sqs", endpoint_url=ENDPOINT_URL, region_name=REGION_NAME)
s3  = boto3.client("s3", endpoint_url=ENDPOINT_URL, region_name=REGION_NAME)


def download_video_from_s3(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)

def upload_dir_to_s3(local_dir, bucket, s3_prefix):
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, local_dir)
            s3_key = os.path.join(s3_prefix, relative_path)
            s3.upload_file(full_path, bucket, s3_key)
            print(f"✅ Upload: {s3_key}")

def regiao_interesse_original(img):
    h, w = img.shape
    # Define os vértices de um trapézio isósceles (base inferior exclui capô)
    vertices = np.array([[
        # (int(w*0.2), int(h*0.65)),
        # (int(w*0.8), int(h*0.65)),
        (int(w*0.2), int(h*0.65)),
        (int(w*0.8), int(h*0.65)),
        (w, h),
        (0, h)
    ]], dtype=np.int32)

    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    
    return masked

def regiao_interesse_sugestao(img):
    h, w = img.shape

    # Ampliamos a base (horizontalmente) e subimos o topo (verticalmente)
    vertices = np.array([[
        (int(w * 0.05), h),               # canto inferior esquerdo
        (int(w * 0.45), int(h * 0.55)),   # topo esquerdo (mais alto)
        (int(w * 0.55), int(h * 0.55)),   # topo direito
        (int(w * 0.95), h)                # canto inferior direito
    ]], dtype=np.int32)


    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    
    return cv2.bitwise_and(img, mask)

def regiao_interesse_c(img):
    height, width = img.shape
    mask = np.zeros_like(img)

    # Trapezoide isósceles
    top_width = int(width * 0.4)
    top_y = int(height * 0.4)
    bottom_y = height

    points = np.array([[
        ((width - top_width) // 2, top_y),
        ((width + top_width) // 2, top_y),
        (width, bottom_y),
        (0, bottom_y)
    ]], dtype=np.int32)

    cv2.fillPoly(mask, points, 255)
    return cv2.bitwise_and(img, mask)


def detectar_linhas(masked_edges, original_frame):
    # Detecta linhas usando a Hough Transform Probabilística
    linhas = cv2.HoughLinesP(
        masked_edges,
        rho=1,
        theta=np.pi / 180,
        threshold=30,           # 50
        minLineLength=20,       # 40
        maxLineGap=150          # 100
    )

    frame_linhas = original_frame.copy()
    if linhas is not None:
        for linha in linhas:
            x1, y1, x2, y2 = linha[0]
            cv2.line(frame_linhas, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame_linhas, linhas


def classificar_linhas_por_inclinacao(linhas):
    linhas_esquerda = []
    linhas_direita = []

    if linhas is not None:
        for linha in linhas:
            x1, y1, x2, y2 = linha[0]

            # Evita divisão por zero
            if x2 - x1 == 0:
                continue

            m = (y2 - y1) / (x2 - x1)

            # Descarte linhas horizontais ou quase horizontais
            # if abs(m) < 0.5:
                # continue

            if m < 0:
                linhas_esquerda.append((x1, y1, x2, y2))
            elif m > 0:
                linhas_direita.append((x1, y1, x2, y2))

    return linhas_esquerda, linhas_direita


def desenhar_linhas(frame, linhas_esq, linhas_dir):

    saida = frame.copy()

    for (x1, y1, x2, y2) in linhas_esq:
        cv2.line(saida, (x1, y1), (x2, y2), (255, 0, 0), 3)  # Azul = esquerda

    for (x1, y1, x2, y2) in linhas_dir:
        cv2.line(saida, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Vermelho = direita

    return saida


def verificar_faixas(linhas_esq, linhas_dir, c=np.pi / 18):  # c = 10 graus

    def calcular_angulo(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            return math.pi / 2  # 90 graus
        return math.atan2(dy, dx)

    def calcular_comprimento(x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    fclll = []
    for (x1, y1, x2, y2) in linhas_esq:
        ang = calcular_angulo(x1, y1, x2, y2)
        if (math.pi/4 - c) <= abs(ang) <= (math.pi/4 + c):  # ~45°
            fclll.append((x1, y1, x2, y2))

    fcrll = []
    for (x1, y1, x2, y2) in linhas_dir:
        ang = calcular_angulo(x1, y1, x2, y2)
        # print(f"🟥 Linha direita – Ângulo: {math.degrees(abs(ang)):.2f}")
        if (3*math.pi/4 - c) <= abs(ang) <= (3*math.pi/4 + c):  # ~135°
            fcrll.append((x1, y1, x2, y2))

    # LGC – seleciona a mais longa de cada lado
    lane_left = max(fclll, key=lambda l: calcular_comprimento(*l), default=None)
    lane_right = max(fcrll, key=lambda l: calcular_comprimento(*l), default=None)

    return lane_left, lane_right

def verificar_faixas_sug(linhas_esq, linhas_dir):
    def calcular_angulo(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            return 90.0
        return abs(math.degrees(math.atan2(dy, dx)))

    def calcular_comprimento(x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    fclll = [l for l in linhas_esq if 20 <= calcular_angulo(*l) <= 70]
    # fcrll = [l for l in linhas_dir if 10 <= calcular_angulo(*l) <= 60]
    fcrll = [l for l in linhas_dir if 20 <= calcular_angulo(*l) <= 60]

    lane_left = max(fclll, key=lambda l: calcular_comprimento(*l), default=None)
    lane_right = max(fcrll, key=lambda l: calcular_comprimento(*l), default=None)

    return lane_left, lane_right

def dentro_do_rhlp(linha_atual, linha_prev, w, margem_pct=6):
    """Verifica se a linha atual está dentro do intervalo permitido (RHLP) da anterior."""
    if not linha_prev or not linha_atual:
        return False

    d = w * margem_pct / 100  # desvio permitido em pixels
    x1_prev, _, x2_prev, _ = linha_prev
    x1_atual, _, x2_atual, _ = linha_atual

    return (x1_prev - d <= x1_atual <= x1_prev + d) and (x2_prev - d <= x2_atual <= x2_prev + d)


def lambda_handler(event, context):

    print("Iniciando processamento...")

    base_output = "/tmp/save_all"


    for record in event.get("Records", []):
        msg = json.loads(record["body"])

        filename = msg["filename"]
        bucket = msg.get("bucket")

        # Caminhos temporários para Lambda
        local_input = f"/tmp/{filename}"
        output_dir = f"/tmp/out_{uuid.uuid4()}"

        print(f"⬇️ Baixando {filename} de {bucket}")
        download_video_from_s3(bucket, filename, local_input)

        # Cria diretórios temporários
        os.makedirs(output_dir, exist_ok=True)

        print(f"⚙️ Processando vídeo com main.py...")

        ######################
        ######################

        path, file = os.path.split(local_input)
        if path and not path.endswith("/"):
            path += "/"

        cap = cv2.VideoCapture(path + file)

        # save_all paths
        sa_frames_gray      = os.path.join(base_output, "frames/gray")
        sa_frames_bilateral = os.path.join(base_output, "frames/bilateral")
        sa_frames_mask      = os.path.join(base_output, "frames/mask")
        sa_frames_canny     = os.path.join(base_output, "frames/canny")
        sa_frames_final     = os.path.join(base_output, "frames/final")
        # sa_frames_candH     = os.path.join(base_output, "frames/cadidatas_h")
        # sa_frames_candV     = os.path.join(base_output, "frames/cadidatas_v")

        # sa_video_gray       = os.path.join(base_output, "video/gray")
        # sa_video_bilateral  = os.path.join(base_output, "video/bilateral")
        # sa_video_mask       = os.path.join(base_output, "video/mask")
        # sa_video_canny      = os.path.join(base_output, "video/canny")
        # sa_video_final      = os.path.join(base_output, "video/final")


        os.makedirs(sa_frames_gray, exist_ok=True)
        os.makedirs(sa_frames_bilateral, exist_ok=True)
        os.makedirs(sa_frames_mask, exist_ok=True)
        os.makedirs(sa_frames_canny, exist_ok=True)
        os.makedirs(sa_frames_final, exist_ok=True)
        # os.makedirs(sa_frames_candH, exist_ok=True)
        # os.makedirs(sa_frames_candV, exist_ok=True)
        # os.makedirs(sa_video_gray, exist_ok=True)
        # os.makedirs(sa_video_bilateral, exist_ok=True)
        # os.makedirs(sa_video_mask, exist_ok=True)
        # os.makedirs(sa_video_canny, exist_ok=True)
        # os.makedirs(sa_video_final, exist_ok=True)

        # configurar salvar video
        # out_video = None
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # ou 'XVID'
        # fps = cap.get(cv2.CAP_PROP_FPS)
        # h, w = 480, 720  # tamanho usado no resize

        # out_gray        = cv2.VideoWriter(f"{sa_video_gray}/{file}", fourcc, fps, (w, h))
        # out_bilateral   = cv2.VideoWriter(f"{sa_video_bilateral}/{file}", fourcc, fps, (w, h))
        # out_mask        = cv2.VideoWriter(f"{sa_video_mask}/{file}", fourcc, fps, (w, h))
        # out_canny       = cv2.VideoWriter(f"{sa_video_canny}/{file}", fourcc, fps, (w, h))
        # out_final       = cv2.VideoWriter(f"{sa_video_final}/{file}", fourcc, fps, (w, h))


        if not cap.isOpened():
            print("Erro: Não foi possível abrir o vídeo.")
            exit()

        start_time  = time.time()
        frame_count = 0
        
        lane_left_prev = None
        lane_right_prev = None

        while True:

            ret, frame = cap.read()
            if not ret:
                break

            t0 = time.time()
            
            # Redimensiona para 720p (altura=480, largura=720)
            frame = cv2.resize(frame, (720, 480)) # Comentar para desativar

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Aplicação do filtro bilateral
            bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

            # Detecção de bordas com CITR (Canny)
            lower_thresh = 10
            upper_thresh = 30
            # lower_thresh = 50
            # upper_thresh = 100
            edges = cv2.Canny(bilateral, lower_thresh, upper_thresh)

            # ROI em forma de trapézio isósceles
            # masked_edges = regiao_interesse_original(edges)
            masked_edges = regiao_interesse_sugestao(edges)
            # masked_edges = regiao_interesse_c(edges)
            # masked_edges = edges

            # Detectar linhas e desenhar sobre o frame original
            frame_linhas, linhas = detectar_linhas(masked_edges, frame)

            # linhas esquerda, direita
            linhas_esq, linhas_dir = classificar_linhas_por_inclinacao(linhas)
            # frame_final = desenhar_linhas(frame, linhas_esq, linhas_dir)

            # AGC + LGC – Verificação geométrica (ângulo + comprimento)
            # lane_left, lane_right = verificar_faixas(linhas_esq, linhas_dir)
            lane_left, lane_right = verificar_faixas_sug(linhas_esq, linhas_dir)

            # Tamanho da imagem
            h, w = frame.shape[:2]

            # Verificação geométrica (AGC + LGC)
            # lane_left, lane_right = verificar_faixas(linhas_esq, linhas_dir)
            lane_left, lane_right = verificar_faixas_sug(linhas_esq, linhas_dir)

            # Aplica rastreamento se uma faixa estiver ausente
            if lane_left is None and lane_left_prev is not None:
                # print("↪️ Usando faixa esquerda do frame anterior (RHLP)")
                lane_left = lane_left_prev
            elif lane_left and lane_left_prev and not dentro_do_rhlp(lane_left, lane_left_prev, w):
                # print("⛔ Faixa esquerda fora do intervalo RHLP. Descartando.")
                lane_left = None

            if lane_right is None and lane_right_prev is not None:
                # print("↪️ Usando faixa direita do frame anterior (RHLP)")
                lane_right = lane_right_prev
            elif lane_right and lane_right_prev and not dentro_do_rhlp(lane_right, lane_right_prev, w):
                # print("⛔ Faixa direita fora do intervalo RHLP. Descartando.")
                lane_right = None

            # candidatas
            frame_candH = frame.copy()
            for (x1, y1, x2, y2) in linhas_esq:
                cv2.line(frame_candH, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Azul = esquerda
            for (x1, y1, x2, y2) in linhas_dir:
                cv2.line(frame_candH, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Vermelho = direita

            frame_candV = frame.copy()
            if lane_left:
                cv2.line(frame_candV, lane_left[:2], lane_left[2:], (255, 255, 0), 4)  # Ciano
            if lane_right:
                cv2.line(frame_candV, lane_right[:2], lane_right[2:], (0, 255, 255), 4)  # Amarelo

            # cv2.imwrite(f"{sa_frames_candH}/frame_{frame_count:05d}.jpg", frame_candH)
            # cv2.imwrite(f"{sa_frames_candV}/frame_{frame_count:05d}.jpg", frame_candV)

            # Atualiza os valores anteriores
            lane_left_prev = lane_left
            lane_right_prev = lane_right

            frame_final = frame.copy()
            if lane_left:
                cv2.line(frame_final, lane_left[:2], lane_left[2:], (255, 255, 0), 4)  # Ciano (esquerda)
            if lane_right:
                cv2.line(frame_final, lane_right[:2], lane_right[2:], (0, 255, 255), 4)  # Amarelo (direita)

            # save all frames
            cv2.imwrite(f"{sa_frames_gray}/frame_{frame_count:05d}.jpg", gray)
            cv2.imwrite(f"{sa_frames_bilateral}/frame_{frame_count:05d}.jpg", bilateral)
            cv2.imwrite(f"{sa_frames_mask}/frame_{frame_count:05d}.jpg", masked_edges)
            cv2.imwrite(f"{sa_frames_canny}/frame_{frame_count:05d}.jpg", frame_linhas)
            cv2.imwrite(f"{sa_frames_final}/frame_{frame_count:05d}.jpg", frame_final)
            
            # out_gray.write(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
            # out_bilateral.write(cv2.cvtColor(bilateral, cv2.COLOR_GRAY2BGR))
            # out_mask.write(cv2.cvtColor(masked_edges, cv2.COLOR_GRAY2BGR))
            # out_canny.write(frame_linhas)
            # out_final.write(frame_final)
        
        ######################
        ######################

        print("📤 Enviando resultados para o S3...")
        output_s3_prefix = f"resultados/{os.path.splitext(filename)[0]}_{uuid.uuid4()}"
        upload_dir_to_s3(base_output, bucket, output_s3_prefix)

        shutil.rmtree(base_output)
        print("✅ Finalizado. Resultado em s3://{}/{}".format(bucket, output_s3_prefix))


def event_get():

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    messages = response.get("Messages", [])
    if not messages:
        return []

    events = []
    for msg in messages:
        receipt_handle = msg["ReceiptHandle"]
        events.append({
            "Records": [{"body": msg["Body"]}]
        })

        # Apaga da fila após leitura
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

    return events

if __name__ == "__main__":

    while True:
        events = event_get()
        if events:
            for event in events:
                lambda_handler(event=event, context=None)
        else:
            print("Nenhuma mensagem. Aguardando...")
        time.sleep(10)
