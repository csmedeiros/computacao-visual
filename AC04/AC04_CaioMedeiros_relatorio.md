# AC04 — Evolução da Cena: Modelos de Iluminação — Caio Medeiros

Cena da AP1 (Ibmec Barra) copiada para `AC04_CaioMedeiros.blend` (o arquivo original da AP1 não foi alterado). A palavra/logo Ibmec, a composição e a câmera `Cam_Main` foram preservadas. O .blend é gerado por `build_ac04.py` (Python/bpy). O `.blend` e os renders foram gerados e salvos no **Blender 4.5.14 LTS** (engine EEVEE Next); a AP1 original foi salva no 5.x, e o script ajusta o nome do engine ao abrir no 4.5.

## Arquivos
- `AC04_CaioMedeiros.blend` — cena evoluída (colecões `AC04_Materiais` e `AC04_Luzes`).
- `AC04_CaioMedeiros_final.png` — render final (`Cam_Main`, palavra "ibmec" legível, três objetos visíveis).
- `AC04_CaioMedeiros_comparacao.png` — close dos três objetos sob a mesma luz (`Cam_Comparacao`).
- `AC04_CaioMedeiros_teste_angulo.png` — teste temporário com a luz principal girada (configuração depois restaurada; não está salva no .blend).

## Objetos e materiais
| Objeto (AP1) | Material | Cor-base |
|---|---|---|
| `Barra_Ala` (corpo da unidade Barra, slot "Parede") | `MAT_Lambert` | vermelho (0.85, 0.10, 0.10) |
| `Barra_Arco` + `Barra_Pilar` (arco azul da fachada) | `MAT_Phong` | verde (0.10, 0.65, 0.15) |
| `Cad_01` (cadeira) | `MAT_Lambert` | vermelho (0.85, 0.10, 0.10) |
| `Cad_02` (cadeira) | `MAT_Phong` | verde |
| `Cad_03` e `Cad_04` (cadeiras) | `MAT_BlinnPhong` | laranja (0.60, 0.12, 0.01) |

Os três objetos autorais foram escolhidos fora da palavra Ibmec, que não foi alterada.

| Material | Roughness | Specular (IOR Level) | Metallic |
|---|---|---|---|
| MAT_Lambert | 1.0 | 0.05 | 0 |
| MAT_Phong | 0.2 | 0.5 | 0 |
| MAT_BlinnPhong | 0.1 | 1.0 | 0 |

## Iluminação (igual em todas as imagens comparativas)
- **Principal — `Luz_Key`**: Sun, energia 3.2, cor (1.0, 0.97, 0.92), rotação (48°, 0°, −35°).
- **Preenchimento — `Luz_Fill`**: Area, 400 W, cor azulada (0.52, 0.67, 0.82), rotação (67.5°, 0°, 68.7°).
- Há também `Luz_Rim` (Area, 250 W, rotação 66°, 0°, 180°) e `Sol` (Sun, 3.0), herdadas da AP1 e sem alteração.
- O render final e o de comparação não mudam luz nem câmera principal. A `Cam_Comparacao` (35 mm, mais próxima das cadeiras) é só um enquadramento mais próximo.

## Comparação observada
As cadeiras foram movidas (`Cadeiras`: y = −6, escala 1.6) para a frente da fachada, fora do vidro, para ficarem visíveis. A imagem `comparacao.png` (`Cam_Comparacao`) mostra as quatro cadeiras (mesma forma, mesma luz); `Cam_Main` e as luzes seguem como na AP1.
- **Lambert (cadeira vermelha, rough 1.0):** cor uniforme, sem brilho; a luz só muda o tom das faces (difusa).
- **Phong (verde, rough 0.2):** o assento tem uma borda mais clara e um reflexo suave; o brilho é discreto e de área maior que o do Blinn-Phong.
- **Blinn-Phong (laranja, rough 0.1, especular 1.0):** o brilho é o mais nítido e concentrado — uma faixa clara bem definida no assento da `Cad_04` — enquanto o encosto mantém a cor saturada. A diferença para o Phong aqui vem da rugosidade e do especular, não do vetor médio.
- **Ângulo da luz:** em `teste_angulo.png` (luz principal girada, depois restaurada) as regiões claras mudam de lugar e as sombras mudam de direção; o Lambert só muda de tom.
- No render final os três objetos autorais aparecem claramente: corpo da Barra (Lambert, vermelho), arco (Phong, verde) e cadeiras (vermelha, verde, laranja). Nesse enquadramento mais afastado os highlights são pequenos e quase só se percebe a diferença de cor/fosco; a evidência da comparação está em `comparacao.png` e `teste_angulo.png`.

## Limitação
O Principled BSDF do Blender é um shader fisicamente baseado (GGX). Os valores de rugosidade e especular de Phong e Blinn-Phong são **aproximações visuais** e não implementam literalmente as equações clássicas de Phong (`(R·V)^n`) e Blinn-Phong (`(N·H)^n`, vetor médio H). O Lambert (`N·L`) é uma aproximação direta, já que a componente difusa é equivalente.
