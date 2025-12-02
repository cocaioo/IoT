"""
Monitor de fila usando visão computacional com câmera
"""

import threading
import time

import cv2
import numpy as np

from gerenciador import GerenciadorRestaurante


class MonitorFilaCamera:
    """Monitora a fila usando câmera e visão computacional"""
    
    def __init__(self, gerenciador: GerenciadorRestaurante,
                 camera_index: int = 0,
                 intervalo_segundos: int = 3,
                 habilitar: bool = True):
        self.gerenciador = gerenciador
        self.camera_index = camera_index
        self.intervalo_segundos = intervalo_segundos
        self.habilitar = habilitar
        self.rodando = False
        
        if self.habilitar:
            # Detector de pessoas HOG + SVM (mais preciso)
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
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print(f"❌ Não foi possível abrir a câmera {self.camera_index}")
            return
        
        # Configura resolução menor para melhor performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f"✓ Câmera {self.camera_index} iniciada (detecção HOG+SVM)")
        
        ultimo_tempo = 0
        frame_skip = 0
        
        while self.rodando:
            ret, frame = cap.read()
            if not ret:
                print("❌ Falha ao ler frame da câmera")
                time.sleep(0.5)
                continue
            
            # Processa a cada 3 frames para melhor performance
            frame_skip += 1
            if frame_skip % 3 != 0:
                time.sleep(0.03)
                continue
            
            # Redimensiona para performance
            frame_resized = cv2.resize(frame, (320, 240))
            
            # Detecta pessoas usando HOG
            try:
                boxes, weights = self.hog.detectMultiScale(
                    frame_resized,
                    winStride=(4, 4),
                    padding=(8, 8),
                    scale=1.05,
                    useMeanshiftGrouping=False
                )
                
                # Filtra detecções com baixa confiança
                pessoas = [box for box, weight in zip(boxes, weights) if weight > 0.5]
                count = len(pessoas)
                
            except Exception as e:
                print(f"⚠ Erro na detecção: {e}")
                count = 0
            
            # Atualiza periodicamente
            agora = time.time()
            if agora - ultimo_tempo >= self.intervalo_segundos:
                self.gerenciador.atualizar_fila(count)
                print(f"📹 Pessoas detectadas na fila: {count}")
                ultimo_tempo = agora
            
            time.sleep(0.1)
        
        cap.release()
        print("Câmera encerrada.")
    
    def parar(self):
        """Para o monitoramento"""
        self.rodando = False
