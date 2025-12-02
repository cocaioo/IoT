import threading
import time
import cv2
import numpy as np
from gerenciador import GerenciadorRestaurante

class MonitorFilaCamera:
    """Monitora a fila usando câmera e visão computacional"""

    def __init__(self, gerenciador: GerenciadorRestaurante,
                 camera_index: int = 0,
                 intervalo_segundos: int = 2,
                 habilitar: bool = True):
        self.gerenciador = gerenciador
        self.camera_index = camera_index
        self.intervalo_segundos = intervalo_segundos
        self.habilitar = habilitar
        self.rodando = False

        # Buffer do último frame para streaming
        self.ultimo_frame_jpeg = None
        self.lock_frame = threading.Lock()

        if self.habilitar:
            # HOG Detector
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def iniciar(self):
        """Inicia monitoramento da câmera"""
        if not self.habilitar:
            print("⚠ Monitor de câmera desabilitado")
            return False

        self.rodando = True
        thread = threading.Thread(target=self._loop_camera, daemon=True)
        thread.start()
        return True

    def _loop_camera(self):
        """Loop principal da câmera"""
        # Tenta abrir a câmera (pode ser index 0 ou 1 dependendo do USB)
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print(f"Não foi possível abrir a câmera {self.camera_index}")
            return

        print(f"Câmera iniciada (Index: {self.camera_index})")

        ultimo_tempo_atualizacao = 0

        while self.rodando:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao capturar frame")
                time.sleep(1)
                continue

            largura_alvo = 500
            proporcao = largura_alvo / frame.shape[1]
            altura_alvo = int(frame.shape[0] * proporcao)
            frame = cv2.resize(frame, (largura_alvo, altura_alvo))

            # --- DETECÇÃO ---
            # Detecta pessoas
            # winStride: passo da janela (menor = mais preciso e mais lento)
            # padding: margem
            # scale: fator de escala (1.05 é padrão, aumentar deixa mais rápido mas perde detalhes)
            boxes, weights = self.hog.detectMultiScale(
                frame,
                winStride=(4, 4),
                padding=(4, 4),
                scale=1.05
            )

            count = 0
            # Desenha os retângulos
            for (x, y, w, h) in boxes:
                # Filtra retângulos muito pequenos (ruído) ou muito grandes (tela toda)
                if w > 30 and h > 50:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    count += 1

            # Adiciona contagem na tela
            cv2.putText(frame, f"Fila: {count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # --- ATUALIZAÇÃO DO SISTEMA ---
            agora = time.time()
            if agora - ultimo_tempo_atualizacao >= self.intervalo_segundos:
                self.gerenciador.atualizar_fila(count)
                # print(f"📹 Fila atualizada: {count}")
                ultimo_tempo_atualizacao = agora

            # --- PREPARA PARA STREAMING ---
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                with self.lock_frame:
                    self.ultimo_frame_jpeg = buffer.tobytes()

            time.sleep(0.05)

        cap.release()
        print("Câmera encerrada.")

    def obter_frame(self):
        """Retorna o último frame codificado em JPEG para o feed"""
        with self.lock_frame:
            return self.ultimo_frame_jpeg

    def parar(self):
        self.rodando = False