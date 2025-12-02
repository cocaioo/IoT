import time
import threading
import random
from gerenciador import GerenciadorRestaurante

class SimuladorRestaurante:
    """Simula dados de sensores para testes sem hardware"""

    def __init__(self, gerenciador: GerenciadorRestaurante):
        self.gerenciador = gerenciador
        self.ativo = False
        self.thread = None

    def gerar_rfid_aleatorio(self):
        """Gera um ID fictício ou escolhe um da lista de conhecidos"""
        return f"SIM_{random.randint(1000, 9999)}"

    def simular_entrada(self):
        """Simula a entrada de uma pessoa aleatória"""
        rfid = self.gerar_rfid_aleatorio()
        # Garante que não tente entrar alguém que já está (para evitar erro no log, embora o gerenciador trate)
        while rfid in self.gerenciador.pessoas_dentro:
            rfid = self.gerar_rfid_aleatorio()

        print(f"🤖 [SIMULADOR] Tentando entrar: {rfid}")
        return self.gerenciador.registrar_entrada(rfid)

    def simular_saida(self):
        """Simula a saída de uma pessoa que já está dentro"""
        pessoas_dentro = list(self.gerenciador.pessoas_dentro)

        if not pessoas_dentro:
            print("🤖 [SIMULADOR] Ninguém dentro para sair.")
            return {'sucesso': False, 'mensagem': 'Restaurante vazio'}

        # Escolhe aleatoriamente alguém que está dentro
        rfid_saida = random.choice(pessoas_dentro)
        print(f"🤖 [SIMULADOR] Tentando sair: {rfid_saida}")
        return self.gerenciador.registrar_saida(rfid_saida)

    def simular_fila(self, quantidade: int):
        """Define um valor arbitrário para a fila"""
        print(f"🤖 [SIMULADOR] Fila alterada para: {quantidade}")
        self.gerenciador.atualizar_fila(quantidade)

    def iniciar_modo_automatico(self, intervalo=2.0):
        """(Opcional) Fica gerando dados aleatórios sozinho"""
        self.ativo = True
        self.thread = threading.Thread(target=self._loop_auto, args=(intervalo,), daemon=True)
        self.thread.start()
        print("🤖 [SIMULADOR] Modo automático iniciado.")

    def _loop_auto(self, intervalo):
        while self.ativo:
            acao = random.choice(['entrar', 'entrar', 'entrar', 'sair', 'fila'])

            if acao == 'entrar':
                self.simular_entrada()
            elif acao == 'sair':
                self.simular_saida()
            elif acao == 'fila':
                qtd = random.randint(0, 15)
                self.simular_fila(qtd)

            time.sleep(intervalo + random.uniform(-0.5, 0.5))

    def parar(self):
        self.ativo = False