"""
Módulo para captura de fotos da webcam do notebook
Usado para registrar imagem da pessoa ao passar o cartão RFID
"""

import cv2
import os
from datetime import datetime
from typing import Optional


class CapturaWebcam:
    
    def __init__(self, camera_index: int = 0, pasta_fotos: str = "fotos_acesso"):
        """
        Args:
            camera_index: Índice da câmera (0 = webcam padrão)
            pasta_fotos: Pasta onde as fotos serão salvas
        """
        self.camera_index = camera_index
        self.pasta_fotos = pasta_fotos
        
        os.makedirs(self.pasta_fotos, exist_ok=True)
        print(f"Módulo de captura de fotos inicializado (pasta: {self.pasta_fotos})")
    
    def capturar_foto(self, rfid: str, tipo: str) -> Optional[str]:
        """
        Captura uma foto da webcam e salva com nome baseado no RFID e tipo
        
        Args:
            rfid: ID do cartão RFID
            tipo: "entrada" ou "saida"
        
        Returns:
            Caminho do arquivo salvo, ou None se falhar
        """
        try:
            cam = cv2.VideoCapture(self.camera_index)
            
            if not cam.isOpened():
                print(f"Erro: Não foi possível abrir a webcam (índice {self.camera_index})")
                return None
            
            ret, frame = cam.read()
            cam.release()
            
            if not ret or frame is None:
                print("Erro: Falha ao capturar frame da webcam")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rfid_limpo = rfid.replace(":", "_").replace(" ", "_")
            filename = f"{tipo.upper()}_{rfid_limpo}_{timestamp}.jpg"
            filepath = os.path.join(self.pasta_fotos, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"Foto capturada: {filename}")
            return filepath
            
        except Exception as e:
            print(f"Erro ao capturar foto: {e}")
            return None
    
    def capturar_video(self, rfid: str, tipo: str, duracao_segundos: int = 3) -> Optional[str]:
        """
        Captura um vídeo curto da webcam
        
        Args:
            rfid: ID do cartão RFID
            tipo: "entrada" ou "saida"
            duracao_segundos: Duração do vídeo em segundos
        
        Returns:
            Caminho do arquivo salvo, ou None se falhar
        """
        try:
            cam = cv2.VideoCapture(self.camera_index)
            
            if not cam.isOpened():
                print(f"Erro: Não foi possível abrir a webcam (índice {self.camera_index})")
                return None
            
            fps = 20.0
            width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rfid_limpo = rfid.replace(":", "_").replace(" ", "_")
            filename = f"{tipo.upper()}_{rfid_limpo}_{timestamp}.avi"
            filepath = os.path.join(self.pasta_fotos, filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
            
            frames_total = int(fps * duracao_segundos)
            for _ in range(frames_total):
                ret, frame = cam.read()
                if ret:
                    out.write(frame)
            
            cam.release()
            out.release()
            
            print(f"Vídeo capturado: {filename} ({duracao_segundos}s)")
            return filepath
            
        except Exception as e:
            print(f"Erro ao capturar vídeo: {e}")
            return None