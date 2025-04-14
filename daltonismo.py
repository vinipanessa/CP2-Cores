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
    cv2.putText(
        img, texto, (x, y), fonte, escala, cor_texto, espessura, cv2.LINE_AA)


def simular_deuteranopia(img):
    transform = np.array([[0.625, 0.7, 0],
                          [0.7, 0.625, 0],
                          [0, 0, 1]])
    return cv2.transform(img, transform.astype(np.float32))


cor_clicada = None


def click_event(event, x, y, flags, param):
    global cor_clicada
    if event == cv2.EVENT_LBUTTONDOWN:
        frame = param
        b, g, r = frame[y, x]
        cor_clicada = (r, g, b)


def processar_video_daltonismo(video_path):
    global cor_clicada
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}")
        return

    cv2.namedWindow(
        'ColorEye - Detecção de Cor com Daltonismo', cv2.WINDOW_NORMAL)

    ultima_cor_falada = ""
    ultimo_tempo_fala = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Redimensiona para manter boa qualidade visual
        frame = cv2.resize(frame, (960, 540))

        height, width, _ = frame.shape
        centro_x, centro_y = width // 2, height // 2
        tamanho_roi = 20

        roi = frame[centro_y - tamanho_roi:centro_y + tamanho_roi,
                    centro_x - tamanho_roi:centro_x + tamanho_roi]

        if not roi.size:
            continue

        if cor_clicada:
            cor_media_rgb = tuple(map(int, cor_clicada))
            cor_clicada = None
        else:
            cor_media_bgr = cv2.mean(roi)[:3]
            cor_media_rgb = (
                int(cor_media_bgr[2]),
                int(cor_media_bgr[1]), int(cor_media_bgr[0]))

        nome, distancia, cor_proxima = encontrar_nome_cor_detalhado(
            cor_media_rgb)

        texto_exibicao = f'Cor: {nome}'
        if distancia > 0:
            texto_exibicao += f' (dist {distancia:.1f})'

        cor_texto = (255, 255, 255)
        y_base = 40

        cv2.circle(frame, (centro_x, centro_y),
                   tamanho_roi, (255, 255, 255), 2)

        desenhar_texto_com_fundo(
            frame, texto_exibicao, (10, y_base),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto, (0, 0, 0), 2)

        desenhar_texto_com_fundo(
            frame, f'RGB: {cor_media_rgb}',
            (10, y_base + 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, cor_texto, (0, 0, 0), 1)

        # Simula daltonismo (remova se quiser mostrar só o original)
        frame_dalt = simular_deuteranopia(frame.copy())
        frame_comparado = np.hstack((frame, frame_dalt))

        cv2.imshow(
            'ColorEye - Detecção de Cor com Daltonismo', frame_comparado)

        # Fala apenas se a cor mudar e com intervalo mínimo
        if nome != ultima_cor_falada and time.time() - ultimo_tempo_fala > 1.0:
            tts_engine.say(f"A cor detectada é {nome}")
            tts_engine.runAndWait()
            ultima_cor_falada = nome
            ultimo_tempo_fala = time.time()

        cv2.setMouseCallback(
            'ColorEye - Detecção de Cor com Daltonismo',
            click_event, param=frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


video_path = r"videoplayback.mp4"
processar_video_daltonismo(video_path)