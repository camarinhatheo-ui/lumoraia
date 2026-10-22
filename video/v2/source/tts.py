"""Gera a narração (Kokoro TTS, pt-BR) — uma frase por cena — e imprime as durações."""
import sys, os, soundfile as sf
from kokoro_onnx import Kokoro
M = sys.argv[1]  # pasta com kokoro-v1.0.onnx e voices-v1.0.bin
VOICE, SPEED = os.environ.get('VOICE', 'pf_dora'), float(os.environ.get('SPEED', '1.18'))
LINES = {
  'n1': 'Cansou de prospectar no escuro? Acende a luz: Lumora!',
  'n2': 'Escolha país, cidade e nicho. Mais de cento e cinquenta prontos!',
  'n3': 'Buscou? Pronto! Empresas reais, com telefone, site e nota. Sem duplicados!',
  'n4': 'Só quem não tem site? Filtra! E exporta em CSV num clique.',
  'n5': 'A mensagem de venda já vem prontinha, em português ou inglês!',
  'n6': 'Aí é só arrastar no CRM até fechar negócio!',
  'n7': 'Histórico, créditos transparentes, indique e ganhe... e mais!',
  'n8': 'Planos a partir de setenta e nove e noventa. Assine o Lumora e acenda suas vendas!',
}
k = Kokoro(os.path.join(M, 'kokoro-v1.0.onnx'), os.path.join(M, 'voices-v1.0.bin'))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'narracao')
for n, txt in LINES.items():
    s, sr = k.create(txt, voice=VOICE, speed=SPEED, lang='pt-br')
    sf.write(os.path.join(out, n + '.wav'), s, sr)
    print(n, round(len(s) / sr, 2), sr)
