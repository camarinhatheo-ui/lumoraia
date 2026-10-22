# Lumora — anúncio de 30s (todas as funções)

Vídeo para a landing page, animado em HTML e renderizado em MP4 (1920×1080, 30 fps, com narração e trilha).

- `lumora-anuncio-30s.mp4` — master (≈16 MB)
- `lumora-anuncio-30s-web.mp4` — versão leve para a LP (≈7 MB)

Roteiro (cada cena acompanha a narração): gancho "acende a luz" → busca (país/estado/cidade/nicho, 150+ nichos, BR + EUA) →
resultados sem duplicados → filtro "sem site" + exportação CSV → biblioteca de mensagens (PT/EN, campos preenchidos com os dados do lead)
→ CRM Kanban (Ultra) → histórico, créditos, indique e ganhe, dados isolados, IA (em breve) → planos Pro/Max/Ultra + CTA "Assinar agora".
Preços, créditos e funções vêm do repositório `lumorasite` (`src/config/plans.ts`, `LUMORA.md`). As linhas da tabela e os cartões do CRM são
ilustrativos (categorias e cidades, telefones mascarados — nenhuma empresa real).

## Como regenerar (`source/`)

```bash
pip install kokoro-onnx soundfile numpy      # narração neural pt-BR (modelo kokoro-v1.0.onnx + voices-v1.0.bin)
python3 -I tts.py <pasta-do-modelo>          # gera narracao/n1..n8.wav
python3 -I audio.py                          # trilha + efeitos + narração -> mix.wav
node shot.js frames 0 900 <pasta>            # 900 quadros JPG (Playwright + Chromium) a partir de video.html
ffmpeg -framerate 30 -i <pasta>/f%04d.jpg -i mix.wav -map 0:v -map 1:a -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -t 30 lumora-anuncio-30s.mp4
```

`video.html` é determinístico: `window.render(t)` desenha qualquer instante `t` (em segundos). Abra no navegador e rode `render(12.3)` no console para inspecionar.
Fontes (Sora e Manrope, OFL) e a logo oficial ficam em `source/assets/`.
