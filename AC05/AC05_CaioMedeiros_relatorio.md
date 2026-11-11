# AC05 — Evolução da Cena: Materiais PBR e Texturas

**Aluno:** Caio Medeiros · **Disciplina:** Computação Gráfica (CG_26.2_8001) · **Ferramenta:** Blender 4.5.14 LTS

## Arquivos entregues

| Item | Arquivo |
|------|---------|
| Cena com materiais, UVs e texturas (imagens empacotadas) | `AC05_CaioMedeiros.blend` |
| Render final pela câmera principal (`Cam_Main`, 1920×1080, quadro 59 como na AC04) | `AC05_CaioMedeiros_render.png` |
| Render de detalhe (`Cam_Comparacao`, a mesma câmera de apoio da AC04) | `AC05_CaioMedeiros_render_detalhe.png` |
| Captura do Shader Editor (Base Color + Roughness + Normal) | `AC05_CaioMedeiros_shader_editor.png` |
| Captura do UV Editor (cadeira) | `AC05_CaioMedeiros_uv_editor.png` |
| Texturas PBR externas (também empacotadas no `.blend`) | `textures_pbr/` |

## Continuidade da AC04

- A cena parte de uma **cópia** de `AC04/AC04_CaioMedeiros.blend`; os arquivos da AP1, AP2 e AC04 não foram alterados.
- Composição, câmera `Cam_Main`, luzes (`Luz_Key`, `Luz_Fill`, `Luz_Rim`, `Sol`), posição das cadeiras e a palavra/logo **Ibmec** são os da AC04.
- Os materiais **Lambert, Phong e Blinn-Phong** da AC04 foram substituídos por materiais PBR (abaixo). Eles continuam existindo no arquivo da AC04.
- Todos os materiais foram renomeados com nomes descritivos (`MAT_*`). A placa/logo Ibmec continua com as mesmas cores (branco `(1,1,1)`, amarelo `(0,91; 0,41; 0)` e azul da placa), agora em PBR sem textura nem relevo.

## 1. Objetos autorais e materiais aplicados

Os três objetos autorais são os mesmos da AC04: corpo da Barra, arco da fachada e cadeiras.

| # | Objeto autoral | Objetos no Blender | Material | Aparência |
|---|----------------|--------------------|----------|-----------|
| 1 | **Cadeiras** (assento e encosto) | `Cad_01` … `Cad_04` (antes Lambert, Phong, Blinn-Phong) | `MAT_Madeira_PBR` | Madeira escura, com texturas de imagem |
| 2 | **Arco e pilares da fachada** | `Barra_Arco`, `Barra_Pilar` (antes Phong); pernas das cadeiras usam o mesmo metal | `MAT_Metal_Azul_PBR` e `MAT_Metal_Azul_Arco_PBR` | Metal pintado de azul, com texturas de imagem |
| 3 | **Corpo da Barra** (coberturas das alas + vidro da entrada) | `Barra_Ala` (slot que era Lambert) e `Barra_Vidro` | `MAT_Espelho_PBR` | Espelho, cor sólida |

## 2. Propriedades principais dos materiais

| Material | Base Color | Roughness | Metallic | Outros |
|----------|-----------|-----------|----------|--------|
| `MAT_Madeira_PBR` | mapa `wood_table_001_diff` | mapa `wood_table_001_rough` | 0 (não metal) | Normal Map, força 1,0; escala do Mapping 0,417 (textura de 1,5 m e cadeiras com escala 1,6) |
| `MAT_Metal_Azul_PBR` | mapa `blue_metal_plate_diff` | mapa `blue_metal_plate_rough` | 0,85 constante | Normal Map, força 1,0; escala 0,4 (textura de 2,5 m) |
| `MAT_Metal_Azul_Arco_PBR` | igual ao anterior | igual ao anterior | 0,85 | Escala do Mapping (2,135; 0,352), ver seção 4 |
| `MAT_Espelho_PBR` | (0,92; 0,94; 0,97) | 0,03 | 1,0 | sem textura |
| `MAT_Ibmec_Branco_PBR` | (1,0; 1,0; 1,0) | 0,35 | 0 | sem textura/relevo |
| `MAT_Ibmec_Amarelo_PBR` | (0,91; 0,41; 0,0) | 0,35 | 0 | sem textura/relevo |

A textura Blue Metal Plate não traz mapa Metallic, por isso o Metallic do metal pintado é um valor constante (0,85); a madeira, não metálica, usa 0.

## 3. Mapas utilizados e ligações

Conferido no arquivo salvo (ver `AC05_CaioMedeiros_shader_editor.png`, material da madeira):

| Mapa | Espaço de cor | Ligação |
|------|---------------|---------|
| Base Color (`*_diff_2k.jpg`) | **sRGB** | Color → **Base Color** do Principled BSDF |
| Roughness (`*_rough_2k.jpg`) | **Non-Color** | Color → **Roughness** |
| Normal OpenGL (`*_nor_gl_2k.jpg`) | **Non-Color** | Color → nó **Normal Map** (espaço tangente, UV `UVMap`) → **Normal** do Principled BSDF |

Madeira e metal têm os três mapas (Base Color, Roughness e Normal), ou seja, **dois objetos** recebem texturas de imagem completas. Todas as texturas passam por `Texture Coordinate (UV)` → `Mapping` (repetição ligada). Não usei mapa Metallic (opcional).

## 4. UVs

- **Cadeiras (`Cad_01`…`Cad_04`) e pilares (`Barra_Pilar`):** projeção em caixa (*box projection*) em escala real. Cada face é projetada no plano do eixo dominante da sua normal, com coordenadas em **metros** (1 unidade de UV = 1 m): densidade de textura uniforme e sem distorção nas faces planas. O nó Mapping ajusta a repetição ao tamanho real de cada textura. As malhas têm um mapa `UVMap` cada.
- **Arco (`Barra_Arco`, uma curva Bézier com tubo de raio 0,14):** o Blender gera o UV da curva automaticamente (verificado: a malha avaliada tem `UVMap`), com U ao longo da curva e V ao redor do tubo, de 0 a 1. Como esse UV não está em metros, o arco usa uma cópia do material com a escala do Mapping = (comprimento da curva ÷ 2,5; circunferência ÷ 2,5), para a textura não esticar.
- **Limitação conhecida:** na projeção em caixa, faces opostas (frente/trás) caem no mesmo lugar do UV e **as ilhas se sobrepõem** (visível no UV Editor). Isso não atrapalha texturas repetidas (*tileable*), mas não serviria para *baking*. No arco, o V não é periódico: pode aparecer uma costura de textura ao longo do tubo.
- As pernas das cadeiras usam o mesmo material do pilar (escala 0,4), então a textura fica um pouco maior nelas do que no pilar, já que as cadeiras têm escala 1,6.

## 5. Origem e licença das texturas

Todas vêm do **Poly Haven**, licença **CC0** (domínio público; creditadas aqui mesmo assim). Resolução 2K, JPG.

| Textura | Autoria | Link |
|---------|---------|------|
| Blue Metal Plate (cor, roughness, normal GL) | Rob Tuytel | https://polyhaven.com/a/blue_metal_plate |
| Wood Table 001 (cor, roughness, normal GL) | Dimitrios Savva (fotografia) e Rico Cilliers (processamento) | https://polyhaven.com/a/wood_table_001 |

As demais imagens da cena (fachada, Rio, rua) são as da AP1/AC04 e continuam com os créditos registrados em `AP1/ref/creditos_imagens.txt`.

## 6. Ajustes de cena registrados

- **Ray tracing do EEVEE ligado** (`use_raytracing = True`) para o espelho e o metal terem reflexos reais; estava desligado na AC04. Nenhuma luz, câmera, posição de objeto ou escala foi alterada.
- Imagens empacotadas no `.blend` (`File > External Data > Pack Resources`): sem caminhos locais quebrados (verificado: nenhuma imagem externa sem pacote).

## 7. Como a iluminação influenciou a aparência

Observado nos renders (`AC05_CaioMedeiros_render.png` e `AC05_CaioMedeiros_render_detalhe.png`):

- **Madeira:** o veio e o relevo do normal map aparecem no assento e no encosto; o assento mostra um brilho suave na borda, vindo da rugosidade do mapa. Todas as quatro cadeiras ficam iguais, ao contrário da AC04, onde cada uma tinha uma cor e um modelo diferentes.
- **Metal azul:** com a cor da textura muito escura, arco, pilares e pernas das cadeiras aparecem em azul-marinho quase preto. No render de detalhe, as curvas do arco e as bordas das pernas mostram brilhos claros, e o riscado/desgaste da textura aparece nos pilares.
- **Espelho:** as coberturas das alas e o vidro da entrada aparecem em azul claro, próximo da cor do `World` (0,27; 0,48; 0,81), ou seja, refletem o fundo azul da cena; no render de detalhe também se vê a parte quebrada do vidro, com a pedra e o ônibus atrás. Com `Roughness = 0,03` o reflexo é nítido.
- **Luzes:** a `Luz_Key` (Sun) continua projetando as sombras das cadeiras no piso; os materiais PBR respondem às mesmas luzes da AC04, sem ajuste.
- **Palavra Ibmec:** a placa/logo continua legível, com as mesmas cores da AC04.

## 8. Observações

- O `.blend`, os dois renders e as capturas do Shader Editor e do UV Editor foram gerados e salvos no **Blender 4.5.14 LTS** (EEVEE Next), a mesma versão da AC04. Conferido ao abrir o arquivo no 4.5.14: ligações e espaços de cor dos mapas, UVs e imagens empacotadas (nenhuma externa sem pacote).
- O render entregue é do modo Rendered (EEVEE), pela câmera principal; não fiz capturas separadas do Material Preview.
