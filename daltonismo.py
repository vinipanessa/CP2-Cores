import cv2
import numpy as np
import pyttsx3
import time
from webcolors import CSS3_NAMES_TO_HEX, hex_to_rgb, rgb_to_name

# Inicializa o mecanismo de voz
tts_engine = pyttsx3.init()

def distancia_cor(rgb1, rgb2):
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def encontrar_nome_cor_detalhado(rgb):
    try:
        nome_exato = rgb_to_name(rgb, spec='css3')
        return nome_exato, 0, rgb
    except ValueError:
        min_distancia = float('inf')
        nome_proximo = 'Desconhecida'
        rgb_proximo = (0, 0, 0)
        for nome_css, hex_value in CSS3_NAMES_TO_HEX.items():
            rgb_css = hex_to_rgb(hex_value)
            dist = distancia_cor(rgb, rgb_css)
            if dist < min_distancia:
                min_distancia = dist
                nome_proximo = nome_css
                rgb_proximo = rgb_css
        return nome_proximo, min_distancia, rgb_proximo

def desenhar_texto_com_fundo(img, texto, pos, fonte, escala,
                             cor_texto, cor_fundo, espessura):
    (w, h), _ = cv2.getTextSize(texto, fonte, escala, espessura)
    x, y = pos
    cv2.rectangle(img, (x - 5, y - h - 5), (x + w + 5, y + 5), cor_fundo, -1)
    cv2.putText(img, texto, (x, y), fonte, escala, cor_texto, espessura, cv2.LINE_AA)

def simular_deuteranopia(img):
    transform = np.array([[0.625, 0.7, 0],
                          [0.7, 0.625, 0],
                          [0, 0, 1]])
    return cv2.transform(img, transform.astype(np.float32))
cor_clicada = None

def click_event(event, x, y, flags, param):
    global cor_clicada
    frame = param['frame']
    if event == cv2.EVENT_LBUTTONDOWN and x < frame.shape[1]:  # Considera apenas lado esquerdo
        b, g, r = frame[y, x]
        cor_clicada = (r, g, b)

def processar_video_daltonismo(video_path):
    global cor_clicada
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return
    cv2.namedWindow('ColorEye - Detecção de Cor com Daltonismo', cv2.WINDOW_NORMAL)
    ultima_cor_falada = ""
    ultimo_tempo_fala = time.time()
    cor_para_mostrar = None
    tempo_cor_mostrada = 0
    duracao_exibicao = 5  # segundos
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (960, 540))
        frame_dalt = simular_deuteranopia(frame.copy())
        frame_comparado = np.hstack((frame, frame_dalt))
        if cor_clicada:
            cor_para_mostrar = tuple(map(int, cor_clicada))
            tempo_cor_mostrada = time.time()
            cor_clicada = None
        if cor_para_mostrar and (time.time() - tempo_cor_mostrada <= duracao_exibicao):
            nome, distancia, cor_proxima = encontrar_nome_cor_detalhado(cor_para_mostrar)
            texto_exibicao = f'Cor: {nome}'
            if distancia > 0:
                texto_exibicao += f' (dist {distancia:.1f})'
            cor_texto = (255, 255, 255)
            y_base = 40
            desenhar_texto_com_fundo(
                frame_comparado, texto_exibicao, (10, y_base),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto, (0, 0, 0), 2)
            desenhar_texto_com_fundo(
                frame_comparado, f'RGB: {cor_para_mostrar}',
                (10, y_base + 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, cor_texto, (0, 0, 0), 1)
            if nome != ultima_cor_falada and time.time() - ultimo_tempo_fala > 1.0:
                tts_engine.say(f"A cor detectada é {nome}")
                tts_engine.runAndWait()
                ultima_cor_falada = nome
                ultimo_tempo_fala = time.time()
        else:
            cor_para_mostrar = None
        cv2.setMouseCallback(
            'ColorEye - Detecção de Cor com Daltonismo',
            click_event, param={'frame': frame})
        cv2.imshow('ColorEye - Deteccao de Cor com Daltonismo', frame_comparado)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Caminho para o vídeo local
video_path = r"tourVirtual-galeriaArte.mp4"
processar_video_daltonismo(video_path)