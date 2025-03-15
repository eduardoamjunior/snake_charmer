# Jogo da cobrinha com movimento da mão

## Requisitos

- Python 3.10.x ```www.python.org/downloads/release/python-3100/```
- Camera
- Windows/Linux

## Dependências

!- ATUALIZE O PIP ANTES -!

Pygame 
```pip install pygame```

OpenCV
```pip install opencv-python```

MediaPipe
```pip install mediapipe```

Numpy
```pip install numpy```

Multiprocessing
```pip install multiprocessing```

## Para Jogar

Execute o "jogo.py"
```python jogo.py```

## Erros comuns

###Detectar a camera
Configuração do caminho da camera, pode variar entre 0,1,2...

Na linha 14 onde está localizado
```video = cv2.VideoCapture(0)```
Altere o valor entre os parenteses até a aplicação abrir


