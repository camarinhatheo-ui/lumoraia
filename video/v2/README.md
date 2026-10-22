# Lumora — anúncio de 30s (todas as funções)

Vídeo para a landing page, animado em HTML e renderizado em MP4 (1920×1080, 30 fps). **Sem voz e sem legenda**: a mensagem vai no texto grande da tela
(título 3D, subtítulo e chips, contador "02 / 09") sobre fundo quadriculado, com trilha e efeitos sonoros sincronizados.

- `lumora-anuncio-30s.mp4` — master (≈16 MB)
- `lumora-anuncio-30s-web.mp4` — versão leve para a LP (≈7 MB)

Cenas: 1 gancho "acende a luz" → 2 busca (país/estado/cidade/nicho, 150+ nichos, BR + EUA) → 3 resultados sem duplicados → 4 filtro "sem site" + CSV →
5 biblioteca de mensagens (PT/EN) → 6 CRM Kanban (Ultra) → 7 histórico, créditos, indique e ganhe, dados isolados, IA (em breve) → 8 planos → 9 CTA "Assinar agora".
Preços, créditos e funções vêm do repositório `lumorasite` (`src/config/plans.ts`, `LUMORA.md`). Linhas da tabela e cards do CRM são ilustrativos
(categorias e cidades, telefones mascarados — nenhuma empresa real).

## Como regenerar (`source/`)

```bash
python3 -I audio.py                          # trilha + efeitos -> trilha.wav (numpy)
node shot.js frames 0 900 <pasta>            # 900 quadros JPG (Playwright + Chromium) a partir de video.html
ffmpeg -framerate 30 -i <pasta>/f%04d.jpg -i trilha.wav -map 0:v -map 1:a -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -t 30 lumora-anuncio-30s.mp4
```

`video.html` é determinístico: `window.render(t)` desenha qualquer instante `t` (em segundos). Os tempos dos textos da tela (`LC` em `video.html`) e dos
efeitos de palavra/chip (`SCENES` em `audio.py`) precisam ficar iguais. Fontes (Sora e Manrope, OFL) e a logo oficial ficam em `source/assets/`.
