# AP2 — Peça audiovisual “Ibmec em 15 segundos”

**Aluno:** Caio Medeiros · **Disciplina:** Computação Gráfica (CG_26.2_8001) · **Ferramenta:** Blender 4.5.14 LTS (Eevee)

## Arquivos entregues

| Item | Arquivo |
|------|---------|
| Cena com animação, materiais PBR, texturas (empacotadas), luzes, câmera e saída | `AP2_CaioMedeiros.blend` |
| Vídeo final, H.264, 1920×1080, 24 fps, 360 quadros (15 s) | `AP2_CaioMedeiros.mp4` |
| Storyboard atualizado (6 quadros do vídeo final, por momento) | `AP2_CaioMedeiros_storyboard.png` |
| Captura do Graph Editor (curvas da câmera, marcadores M1–M3) | `AP2_CaioMedeiros_graph_editor.png` |
| Quadros representativos | `AP2_CaioMedeiros_frame_040.png`, `_150.png`, `_220.png`, `_330.png` |
| Texturas PBR da AC05 (também empacotadas) | `textures_pbr/` |

## Conceito e resumo

A palavra **Ibmec** nasce letra a letra, a câmera voa por uma trajetória sobre a baía e o campus (a “Barra” da AP1) e chega a uma sala de aula, onde a palavra reaparece em grande escala sobre o quadro, cercada por mesas e cadeiras. Início: a marca se forma; desenvolvimento: voo até a Barra; encerramento: a marca em destaque na sala.

## Momentos (marcadores na linha do tempo)

| Momento | Quadros | Ação | Enquadramento |
|---------|---------|------|---------------|
| `M1_Inicio` | 1–119 | Letras I, b, m, e, c e o pingo amarelo surgem em sequência (escala 0 → 1,12 → 1,0) | Plano fixo baixo, frente da palavra |
| `M2_Destaque` | 120–264 | Câmera segue a curva `Voo_Foguete` (constraint Follow Path); o cenário de rua aparece só nesse trecho; as letras somem no quadro 264 | Voo sobre baía e fachada da Barra |
| `M3_Sala` | 265–360 | A palavra reaparece (posição e escala animadas no `Letras`) sobre o quadro da sala; a câmera se afasta e sobe levemente | Plano frontal da sala, com 3 mesas e 6 cadeiras |

## Storyboard

O storyboard foi atualizado para refletir a duração final (15 s, 24 fps) e os três momentos: ver `AP2_CaioMedeiros_storyboard.png`. A ideia da AP1 (palavra Ibmec + Barra + cadeiras) foi mantida; a mudança é a ordem: a marca se forma, a câmera voa até a Barra e termina na sala.

## Propriedades animadas e timing

- **Câmera (`Cam_Main`):** posição, rotação e *influence* da constraint Follow Path (0 → 1 no quadro 120; 1 → 0 no 265). Corte seco entre M2 e M3 (quadros 264/265) com mudança de ambiente; dentro de cada plano o movimento é suave.
- **Letras (`L_I`, `L_b`, `L_m`, `L_e`, `L_c`, `L_I_dot`):** escala; cada letra entra com 6 a 8 quadros de defasagem (efeito de revelação), com *overshoot* a 1,12 e acomodação em 1,0 (Bézier).
- **`Letras` (empty pai):** posição e escala, para reposicionar a marca na sala (quadro 265).
- **`Voo_Foguete`:** `eval_time` do caminho (quadros 120–264) (0 em 120, 13,4 em 158, 99,3 em 264), curva Bézier.
- **Cenário de rua:** `hide_render` com interpolação constante (visível só em 120–236).
- Interpolação Bézier (entrada e saída suaves) em todos os movimentos; constante apenas na visibilidade.

## Iluminação e renderização

- Luzes: `Luz_Key` (principal, acima e à frente), `Luz_Fill` (preenchimento lateral), `Luz_Rim` (contraluz), `Sol` (cena externa) e `Luz_Sala` (interna do M3). As quatro primeiras são as da AC04.
- Eevee, 1920×1080, 100 %, 24 fps, quadros 1–360, saída FFmpeg MPEG-4 / H.264 (qualidade alta), sem áudio.

## Materiais e texturas (reaproveitados da AC05)

Os materiais da AP2 antiga (cores simples) foram trocados pelos materiais PBR da AC05, anexados do arquivo da AC05:

| Objeto(s) | Material da AC05 |
|-----------|------------------|
| Cadeiras da fachada e da sala (`Cad_*`, `Sala_Cad*`) | `MAT_Madeira_PBR` (assento/encosto) e `MAT_Metal_Azul_PBR` (pernas) |
| Arco, pilares da fachada | `MAT_Metal_Azul_Arco_PBR`, `MAT_Metal_Azul_PBR` |
| Corpo da Barra (coberturas e vidro) | `MAT_Espelho_PBR`, `MAT_Fachada_Janelas_PBR`, `MAT_Vidro_Escuro_PBR`, `MAT_Laje_Branca_PBR` |
| Palavra Ibmec | `MAT_Ibmec_Branco_PBR`, `MAT_Ibmec_Amarelo_PBR` (cores originais, sem relevo) |
| Mesas da sala | `MAT_Madeira_PBR` (UVs em escala real, 1 UV = 1 m, geradas por projeção em caixa) |
| Quadro, rodapé da sala | `MAT_Metal_Azul_PBR` |
| Chão, asfalto, calçada | `MAT_Gramado_PBR`, `MAT_Asfalto_PBR`, `MAT_Calcada_PBR` |

Mapas: Base Color em sRGB; Roughness e Normal em Non-Color; o Normal passa pelo nó **Normal Map**. As malhas das cadeiras e dos pilares são as da AC05 (com UVs). Todas as imagens estão empacotadas no `.blend`. O Principled BSDF é um modelo baseado em física, não uma implementação de Phong/Blinn-Phong.

## Desafios e soluções

- **Texturas em movimento:** as cadeiras compartilham uma única malha com UVs em metros, então a escala da textura é igual na fachada e na sala.
- **Legibilidade da marca:** letras brancas com rugosidade 0,35, sem normal map, para que não sejam prejudicadas pela luz nem pelas texturas.
- **Mesas sem UV:** geradas por projeção em caixa em script antes de aplicar a madeira.
- **Revisão das curvas:** conferi por script que todas as chaves de câmera e letras são Bézier com alças *auto clamped* (sem ultrapassar os valores das chaves, exceto o overshoot intencional de 1,12 nas letras); mapas Roughness/Normal em Non-Color e Normal ligado ao nó Normal Map nos três materiais com textura.
- **Revisão no Graph Editor (GUI do Blender 4.5.14):** a captura mostra as curvas da câmera: trechos suaves (Bézier, alças *auto clamped*) em cada momento e dois degraus intencionais nos marcadores `M2_Destaque` (quadro 120) e `M3_Sala` (quadro 265), que são os cortes entre planos.
- **Análise de movimento quadro a quadro (360 quadros):** a diferença média entre quadros consecutivos só passa de 60 nos dois cortes (quadros 120 e 265, previstos). Não há saltos isolados fora deles; o movimento é contínuo e aumenta durante a aproximação final do voo (quadros ~238–263).
- **Calçada estourada:** a calçada saía branca (superexposta) no plano baixo do M1 e no piso da sala; escureci a cor base de `MAT_Calcada_PBR` (0,22; 0,23; 0,25) e re-renderizei o vídeo.
- **Bloco verde na descida para a rua (quadros ~237–250):** era o plano de gramado (`Rua_Chao`, `Rua_Chao2`) aparecendo ao lado das fotos. Estendi a invisibilidade do gramado até o quadro 264 (chave de `hide_render` movida de 237 para 265); o fundo passa a mostrar a foto da baía e do campus.
- **Arquivo antigo a 30 fps/450 quadros:** o vídeo anterior da pasta não atendia ao enunciado; foi re-renderizado a 24 fps, 360 quadros.

## Fontes e licenças

- Texturas PBR (Poly Haven, CC0): Blue Metal Plate (Rob Tuytel, https://polyhaven.com/a/blue_metal_plate) e Wood Table 001 (Dimitrios Savva e Rico Cilliers, https://polyhaven.com/a/wood_table_001).
- Imagens da fachada, da baía e da rua: as da AP1/AC04, com créditos em `AP1/ref/creditos_imagens.txt`.
- Fontes tipográficas incluídas em `fonts/`: PT Serif Bold e Krub Bold.
- Sem áudio (o vídeo anterior da pasta, `Ibmec_AP2_final.mp4`, tinha música e foi mantido apenas como histórico, não é a entrega).
