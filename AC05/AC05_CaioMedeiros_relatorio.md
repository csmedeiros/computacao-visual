# AC05 — Evolução da Cena: Materiais PBR e Texturas

**Aluno:** Caio Medeiros · **Disciplina:** Computação Gráfica (CG_26.2_8001) · **Ferramenta:** Blender 5.2.2

## Arquivos entregues

| Item | Arquivo |
|------|---------|
| Cena com materiais, UVs e texturas (imagens empacotadas) | `AC05_CaioMedeiros.blend` |
| Render final pela câmera principal (`Cam_Main`, quadro 300, 1920×1080) | `AC05_CaioMedeiros_render.png` |
| Captura do Shader Editor (Base Color + Roughness + Metallic + Normal) | `AC05_CaioMedeiros_shader_editor.png` |
| Captura do UV Editor (cadeira) | `AC05_CaioMedeiros_uv_editor.png` |
| Script que aplica tudo (reprodutível) | `ac05_materiais_pbr.py` |
| Texturas PBR externas (também empacotadas no `.blend`) | `textures_pbr/` |

## Continuidade da cena

- A AC04 não tem arquivo no repositório (a pasta `AC04/` está vazia), então a cópia de partida foi a cena mais recente, a **AP2** (`AP2/ap2_ibmec.blend`), salva como `AC05_CaioMedeiros.blend`. Os arquivos da AP1 e da AP2 não foram alterados.
- Composição, câmera, animação e iluminação foram preservadas. A palavra **Ibmec** mantém a cor branca e o ponto/“e” amarelo, sem textura nem relevo.
- Todos os materiais da cena foram renomeados com nomes descritivos (`MAT_*`).

## 1. Objetos autorais e materiais aplicados

| # | Objeto autoral | Objetos no Blender | Material | Tipo de superfície |
|---|----------------|--------------------|----------|--------------------|
| 1 | **Cadeiras** (estrutura/pernas) | `Cad_01`…`Cad_04`, `Sala_Cad1`…`Sala_Cad6` (malha `Cad` compartilhada) | `MAT_Metal_Escovado_PBR` | Metal (chapa de aço) com texturas de imagem |
| 2 | **Carteiras e mesa do professor** | `Sala_Cart`, `Sala_Cart2`, `Sala_Mesa` | `MAT_Madeira_PBR` | Madeira com texturas de imagem |
| 3 | **Espelho** (fachada da Barra + painel na sala) | `Barra_Vidro` e `Espelho_Sala` (coleção `AC05_Materiais_Texturas`) | `MAT_Espelho_PBR` | Espelho, cor sólida |

Os assentos das cadeiras usam `MAT_Assento_Azul_PBR` (plástico, mesma cor azul-escura da AP2). A palavra Ibmec usa `MAT_Ibmec_Branco_PBR` e `MAT_Ibmec_Amarelo_PBR`.

> O 3º objeto: a fachada 3D da Barra quase não aparece na câmera principal (só as bordas, no quadro ~258). Por isso adicionei, como elemento auxiliar, o painel `Espelho_Sala` (2,6 × 2,8 m, girado ~26°) pendurado à direita das letras, para o espelho ser visto no render final. Ele está na coleção `AC05_Materiais_Texturas`.

## 2. Propriedades principais dos materiais

| Material | Base Color | Roughness | Metallic | Outros |
|----------|-----------|-----------|----------|--------|
| `MAT_Metal_Escovado_PBR` | mapa `metal_plate_diff` (sRGB) | mapa `metal_plate_rough` | mapa `metal_plate_metal` | Normal Map (força 1,0); mapeamento 2× (textura de 0,5 m) |
| `MAT_Madeira_PBR` | mapa `wood_table_001_diff` (sRGB) | mapa `wood_table_001_rough` | 0 (não metal) | Normal Map (força 1,0); mapeamento 1/1,5 (textura de 1,5 m) |
| `MAT_Espelho_PBR` | (0,92; 0,94; 0,97) | 0,03 | 1,0 | sem textura |
| `MAT_Assento_Azul_PBR` | cor sólida da AP2 | 0,45 | 0 | — |
| `MAT_Ibmec_Branco_PBR` | (1,0; 1,0; 1,0) | 0,35 | 0 | sem textura/relevo |
| `MAT_Ibmec_Amarelo_PBR` | (0,91; 0,41; 0,0) | 0,35 | 0 | sem textura/relevo |

Metalicidade alta só no metal e no espelho; madeira, plástico e a palavra Ibmec usam Metallic = 0.

## 3. Mapas utilizados e ligações

Verificado no arquivo salvo (ver captura `AC05_CaioMedeiros_shader_editor.png`):

| Mapa | Espaço de cor | Ligação |
|------|---------------|---------|
| Base Color (`*_diff_2k.jpg`) | **sRGB** | Color → **Base Color** do Principled BSDF |
| Roughness (`*_rough_2k.jpg`) | **Non-Color** | Color → **Roughness** |
| Metallic (`metal_plate_metal_2k.jpg`, opcional, só no metal) | **Non-Color** | Color → **Metallic** |
| Normal OpenGL (`*_nor_gl_2k.jpg`) | **Non-Color** | Color → nó **Normal Map** (espaço tangente, UV `UVMap`) → **Normal** do Principled BSDF |

Os três canais (Base Color, Roughness e Normal) estão no material do metal e também no da madeira, ou seja, **dois objetos** recebem texturas de imagem completas. Todas as texturas passam por `Texture Coordinate (UV)` → `Mapping` (repetição ligada).

## 4. UVs

- **Método:** projeção em caixa (*box projection*) em escala real. Cada face é projetada no plano do eixo dominante da sua normal, com coordenadas em **metros** (1 unidade de UV = 1 m). Assim a densidade da textura é a mesma em todas as faces e as faces planas não sofrem distorção.
- **Malhas com UV nova:** `Cad` (cadeiras), `Sala_Cart` (carteiras) e `Sala_Mesa` (mesa). Mapa `UVMap` em cada uma.
- **Escala:** o nó Mapping ajusta a repetição ao tamanho real de cada textura (0,5 m para a chapa de metal, 1,5 m para a madeira).
- **Limitação conhecida:** na projeção em caixa, faces opostas (frente/trás) caem no mesmo lugar do UV e **as ilhas se sobrepõem** (visível no UV Editor). Isso não atrapalha texturas repetidas (*tileable*), mas não serviria para *baking* de mapas únicos. As cadeiras do fundo da sala usam escala de objeto 1,6, o que amplia levemente a textura nelas em relação às de escala 1,0.

## 5. Origem e licença das texturas

Todas vêm do **Poly Haven**, licença **CC0** (domínio público, uso livre, sem exigência de crédito; creditadas aqui mesmo assim). Resolução 2K, JPG.

| Textura | Autoria | Link |
|---------|---------|------|
| Metal Plate (cor, roughness, metallic, normal GL) | Rob Tuytel | https://polyhaven.com/a/metal_plate |
| Wood Table 001 (cor, roughness, normal GL) | Dimitrios Savva (fotografia) e Rico Cilliers (processamento) | https://polyhaven.com/a/wood_table_001 |

As demais imagens da cena (fachada, Rio, rua) são as da AP1/AP2 e continuam com os créditos já registrados em `AP1/ref/creditos_imagens.txt`.

## 6. Ajustes de cena registrados

- **Ray tracing do EEVEE ligado** (`use_raytracing = True`) para que o espelho e o metal mostrem reflexos reais. Estava desligado na AP2. Nenhuma luz foi movida nem alterada; câmera e iluminação são as da AP2.
- Adição do painel `Espelho_Sala` (descrito acima).
- Imagens empacotadas no `.blend` (`File > External Data > Pack Resources`): sem caminhos locais quebrados.

## 7. Como a iluminação influenciou a aparência

Observado no render final (`AC05_CaioMedeiros_render.png`):

- **Madeira:** o veio da textura e o relevo do normal map aparecem no tampo e nas bordas das carteiras. As carteiras da frente têm reflexo especular com tom azulado/arroxeado, ou seja, a rugosidade da madeira (vinda do mapa) deixa o reflexo ainda visível. O mundo (`World`) é um fundo azul uniforme (0,45; 0,66; 0,95, intensidade 0,5) e não há HDRI.
- **Metal:** a cena não tem HDRI para o metal refletir, então ele aparece escuro e o padrão de chapa xadrez só é percebido nos trechos visíveis das pernas (por exemplo, embaixo da carteira à esquerda). Um HDRI de ambiente deixaria o metal mais legível (não aplicado, para preservar a iluminação da AP2).
- **Espelho:** com ray tracing ligado, o painel mostra as carteiras e cadeiras refletidas na parte inferior; o restante da superfície aparece em cinza-azulado liso. Antes de girar o painel ~26°, ele refletia só uma área uniforme e parecia um retângulo cinza.
- **Palavra Ibmec:** continua legível e com as mesmas cores; o branco e o amarelo mantêm a leitura contra o painel azul.
- A madeira PBR ficou **mais escura** (marrom-avermelhado) que a cor lisa original da AP2 (bege). É a cor real da fotografia da textura, e aumenta o contraste da palavra Ibmec que está apoiada sobre a mesa.

## 8. Observações

- O arquivo foi gerado com o **Blender 5.2.2** (não o 4.5 LTS pedido no enunciado), pois é a versão disponível no ambiente de trabalho. Um `.blend` salvo na 5.x pode não abrir no 4.5; o script `ac05_materiais_pbr.py` aplica os mesmos passos e pode ser executado em uma cópia da AP2 em qualquer versão 4.5+.
- O render entregue é do modo Rendered (EEVEE), pela câmera principal. Não fiz capturas separadas do Material Preview.
