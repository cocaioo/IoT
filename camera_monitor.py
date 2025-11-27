"""
Monitor de fila usando visão computacional com câmera
"""

import threading
import time

import cv2

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
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=500, varThreshold=50, detectShadows=True
            )
    
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
        
        print(f"✓ Câmera {self.camera_index} iniciada (monitoramento de fila)")
        
        ultimo_tempo = 0
        
        while self.rodando:
            ret, frame = cap.read()
            if not ret:
                print("❌ Falha ao ler frame da câmera")
                break
            
            # Processa frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fg_mask = self.bg_subtractor.apply(gray)
            
            # Limpa ruído
            _, th = cv2.threshold(fg_mask, 244, 255, cv2.THRESH_BINARY)
            th = cv2.medianBlur(th, 5)
            
            # Detecta contornos
            contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Conta "pessoas" (blobs grandes)
            min_area = 1500
            count = sum(1 for c in contours if cv2.contourArea(c) > min_area)
            
            # Atualiza periodicamente
            agora = time.time()
            if agora - ultimo_tempo >= self.intervalo_segundos:
                self.gerenciador.atualizar_fila(count)
                print(f"📹 Pessoas na fila: {count}")
                ultimo_tempo = agora
            
            time.sleep(0.1)
        
        cap.release()
        print("Câmera encerrada.")
    
    def parar(self):
        """Para o monitoramento"""
        self.rodando = False
