# 🎨 ColorEye - Detecção de Cores com Simulação de Daltonismo

Um projeto em Python que detecta cores em vídeos, exibe o nome da cor com base nos padrões CSS3 e simula como essas cores são vistas por pessoas com **deuteranopia** (tipo de daltonismo). Além disso, o sistema utiliza síntese de voz para anunciar a cor detectada.

---

## 🧩 Funcionalidades

- 🎯 Detecção da cor central ou de pontos clicados no vídeo.
- 🎨 Identificação da cor exata ou a mais próxima da tabela CSS3.
- 🧠 Cálculo da distância entre cores RGB.
- 🗣️ Anúncio da cor via voz (TTS).
- 👁️ Simulação de daltonismo (deuteranopia).
- 📺 Visualização lado a lado: vídeo original e simulado.

---

## ⚙️ Requisitos

Antes de iniciar, certifique-se de ter:

- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)

---

## 📦 Instalação das dependências

Execute os comandos abaixo no terminal para instalar as bibliotecas necessárias:

```bash
pip install opencv-python
pip install numpy
pip install pyttsx3
pip install webcolors
```

## ▶️ Como executar o projeto

1. Clone ou baixe este repositório.
2. Certifique-se de que o vídeo video.mp4 esteja presente na raiz do projeto (já incluso no repositório).
3. Execute o script:
```bash
python daltonismo.py
```
4. Pressione Q para sair a qualquer momento.