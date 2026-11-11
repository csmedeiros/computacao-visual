"""AC05 - Evolução da Cena: Materiais PBR e Texturas (Blender 4.5 LTS).

Parte da cena da AC04 (AC04/AC04_CaioMedeiros.blend), sem alterar o original.

Como reproduzir (a partir de uma cópia da AC04):
    cd AC05
    cp ../AC04/AC04_CaioMedeiros.blend AC05_CaioMedeiros.blend
    cp -r ../AC04/textures textures      # imagens da AP1/AC04 (serão empacotadas)
    blender -b AC05_CaioMedeiros.blend --python ac05_materiais_pbr.py
    rm -r textures                       # as imagens ficam empacotadas no .blend

O script:
  1. troca os materiais Lambert/Phong/Blinn-Phong da AC04 por materiais PBR:
       - Cadeiras (assento/encosto) ....... MAT_Madeira_PBR      (Base Color + Roughness + Normal)
       - Arco e pilares da fachada ........ MAT_Metal_Azul_PBR   (Base Color + Roughness + Normal, Metallic)
         (pernas das cadeiras usam o mesmo metal)
       - Corpo da Barra (coberturas+vidro)  MAT_Espelho_PBR      (cor sólida, Metallic = 1)
  2. renomeia os demais materiais com nomes descritivos (MAT_*), preservando as cores;
  3. gera UVs por projeção em caixa em escala real (1 unidade UV = 1 m) nas malhas texturizadas;
     o arco (curva) usa o UV que o próprio Blender gera (U ao longo da curva, V ao redor do tubo);
  4. empacota as imagens no .blend e salva.
"""
import math
import os

import bmesh
import bpy

AQUI = os.path.dirname(bpy.data.filepath)
TEX = os.path.join(AQUI, "textures_pbr")
UV_NOME = "UVMap"
O = bpy.data.objects
M = bpy.data.materials


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def novo_material(nome):
    """Cria (ou recria) um material com nós: Principled BSDF -> Material Output."""
    if nome in M:
        M.remove(M[nome])
    mat = M.new(nome)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (560, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt, bsdf


def imagem(arquivo, espaco):
    """Carrega a imagem e define o espaço de cor (sRGB para cor, Non-Color para dados)."""
    caminho = os.path.join(TEX, arquivo)
    img = bpy.data.images.load(caminho, check_existing=True)
    img.colorspace_settings.name = espaco
    img.filepath = bpy.path.relpath(caminho)
    return img


def no_imagem(nt, arquivo, espaco, x, y, rotulo):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = imagem(arquivo, espaco)
    n.label = rotulo
    n.location = (x, y)
    n.interpolation = "Cubic"
    n.extension = "REPEAT"
    return n


def material_texturizado(nome, escala_uv, mapas, metallic=0.0, normal_forca=1.0):
    """Principled BSDF com mapas de imagem.

    mapas: 'cor' (sRGB), 'rough' e 'normal' (Non-Color), 'metal' opcional (Non-Color).
    escala_uv: repetições por unidade de UV (UV em metros; textura de N m => 1/N).
    escala_uv pode ser um número ou (u, v).
    """
    mat, nt, bsdf = novo_material(nome)
    su, sv = escala_uv if isinstance(escala_uv, tuple) else (escala_uv, escala_uv)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-900, 0)
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.location = (-700, 0)
    mapa.inputs["Scale"].default_value = (su, sv, 1.0)
    nt.links.new(coord.outputs["UV"], mapa.inputs["Vector"])

    def liga(chave, espaco, entrada, y, rotulo):
        n = no_imagem(nt, mapas[chave], espaco, -400, y, rotulo)
        nt.links.new(mapa.outputs["Vector"], n.inputs["Vector"])
        nt.links.new(n.outputs["Color"], bsdf.inputs[entrada])

    liga("cor", "sRGB", "Base Color", 300, "Base Color (sRGB)")
    liga("rough", "Non-Color", "Roughness", 0, "Roughness (Non-Color)")
    if "metal" in mapas:
        liga("metal", "Non-Color", "Metallic", -300, "Metallic (Non-Color)")
    else:
        bsdf.inputs["Metallic"].default_value = metallic
    # Normal: imagem Non-Color -> nó Normal Map (espaço tangente) -> Normal do BSDF
    n_img = no_imagem(nt, mapas["normal"], "Non-Color", -400, -600, "Normal OpenGL (Non-Color)")
    nt.links.new(mapa.outputs["Vector"], n_img.inputs["Vector"])
    n_map = nt.nodes.new("ShaderNodeNormalMap")
    n_map.space = "TANGENT"
    n_map.uv_map = UV_NOME
    n_map.inputs["Strength"].default_value = normal_forca
    n_map.location = (200, -600)
    nt.links.new(n_img.outputs["Color"], n_map.inputs["Color"])
    nt.links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def material_solido(nome, cor, rough, metal=0.0):
    mat, nt, bsdf = novo_material(nome)
    bsdf.inputs["Base Color"].default_value = (*cor, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def trocar(obj, antigos, novo):
    """Troca, nos slots do objeto, qualquer material cujo nome esteja em `antigos`."""
    n = 0
    for s in obj.material_slots:
        if s.material and s.material.name in antigos:
            s.material = novo
            n += 1
    if not n:
        raise RuntimeError(f"{obj.name}: nenhum slot em {antigos}")


def uv_caixa_escala_real(malha, nome=UV_NOME):
    """UV por projeção em caixa: cada face é projetada no plano do eixo dominante da normal,
    com coordenadas em metros (espaço do objeto) => densidade de textura uniforme e sem
    distorção nas faces planas (as texturas se repetem pelo nó Mapping)."""
    if nome in malha.uv_layers:
        malha.uv_layers.remove(malha.uv_layers[nome])
    bm = bmesh.new()
    bm.from_mesh(malha)
    uv = bm.loops.layers.uv.new(nome)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        u, v = [i for i in range(3) if i != ax]
        su = -1.0 if n[ax] < 0 and ax != 2 else 1.0   # não espelhar faces voltadas para -eixo
        for l in f.loops:
            p = l.vert.co
            l[uv].uv = (su * p[u], p[v])
    bm.to_mesh(malha)
    bm.free()
    malha.uv_layers.active = malha.uv_layers[nome]


# ----------------------------------------------------------------------------
# 1) Renomear materiais da AC04 que seguem (cores preservadas), nomes descritivos
# ----------------------------------------------------------------------------
RENOMEAR = {
    "Branco": "MAT_Ibmec_Branco_PBR",
    "Amarelo": "MAT_Ibmec_Amarelo_PBR",
    "Placa": "MAT_Placa_Azul_PBR",
    "Azul": "MAT_Fundo_Azul_PBR",
    "Cinza": "MAT_Cinza_Pernas_Cadeira_AC04",   # será substituído pelo metal (abaixo)
    "Parede": "MAT_Laje_Branca_PBR",
    "Parede_Textura": "MAT_Fachada_Janelas_PBR",
    "Vidro": "MAT_Vidro_Escuro_PBR",
    "Asfalto": "MAT_Asfalto_PBR",
    "Calcada": "MAT_Calcada_PBR",
    "Chao": "MAT_Gramado_PBR",
    "Trajetoria": "MAT_Trajetoria_Foguete",
}
for velho, novo in RENOMEAR.items():
    if velho in M:
        M[velho].name = novo

# Palavra/logo "Ibmec": mesmas cores (branco e amarelo), só PBR (sem textura nem relevo)
for nome in ("MAT_Ibmec_Branco_PBR", "MAT_Ibmec_Amarelo_PBR"):
    b = principled(M[nome])
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Metallic"].default_value = 0.0

# ----------------------------------------------------------------------------
# 2) Materiais PBR dos três objetos autorais (substituem Lambert, Phong e Blinn-Phong)
# ----------------------------------------------------------------------------
LAMBERT_PHONG_BLINN = ("MAT_Lambert", "MAT_Phong", "MAT_BlinnPhong")

# (a) Cadeiras -> madeira (Poly Haven "Wood Table 001", CC0). Textura de 1,5 m;
#     as cadeiras estão com escala 1,6 (empty `Cadeiras`), logo 1 / (1,5 * 1,6).
mat_madeira = material_texturizado(
    "MAT_Madeira_PBR",
    escala_uv=1.0 / (1.5 * 1.6),
    mapas={
        "cor": "wood_table_001_diff_2k.jpg",
        "rough": "wood_table_001_rough_2k.jpg",
        "normal": "wood_table_001_nor_gl_2k.jpg",
    },
)
# (b) Arco e pilares da fachada -> metal pintado de azul (Poly Haven "Blue Metal Plate", CC0).
#     Textura de 2,5 m. Essa textura não traz mapa Metallic: Metallic constante = 0,85 (metal pintado).
MAPAS_METAL = {
    "cor": "blue_metal_plate_diff_2k.jpg",
    "rough": "blue_metal_plate_rough_2k.jpg",
    "normal": "blue_metal_plate_nor_gl_2k.jpg",
}
mat_metal = material_texturizado("MAT_Metal_Azul_PBR", escala_uv=1.0 / 2.5, mapas=MAPAS_METAL, metallic=0.85)

# O arco é uma curva: seu UV vai de 0 a 1 (U ao longo, V ao redor do tubo), não em metros.
# Escala do Mapping = (comprimento / 2,5 ; circunferência / 2,5) para a textura não esticar.
arco = O["Barra_Arco"]
comprimento = sum(s.calc_length() for s in arco.data.splines)
circunferencia = 2 * math.pi * arco.data.bevel_depth
mat_metal_arco = material_texturizado(
    "MAT_Metal_Azul_Arco_PBR",
    escala_uv=(comprimento / 2.5, circunferencia / 2.5),
    mapas=MAPAS_METAL,
    metallic=0.85,
)
# (c) Corpo da Barra (coberturas das alas + vidro da entrada) -> espelho (cor sólida, Metallic = 1)
mat_espelho = material_solido("MAT_Espelho_PBR", (0.92, 0.94, 0.97), rough=0.03, metal=1.0)

# Assento/encosto das cadeiras (antes Lambert/Phong/Blinn-Phong) -> madeira; pernas -> metal
for n in ("Cad_01", "Cad_02", "Cad_03", "Cad_04"):
    trocar(O[n], LAMBERT_PHONG_BLINN, mat_madeira)
    trocar(O[n], ("MAT_Cinza_Pernas_Cadeira_AC04",), mat_metal)
# Arco (curva) e pilares
trocar(O["Barra_Arco"], LAMBERT_PHONG_BLINN, mat_metal_arco)
trocar(O["Barra_Pilar"], LAMBERT_PHONG_BLINN, mat_metal)
# Corpo da Barra: coberturas (antes Lambert) e vidro da entrada
trocar(O["Barra_Ala"], LAMBERT_PHONG_BLINN, mat_espelho)
trocar(O["Barra_Vidro"], ("MAT_Vidro_Escuro_PBR",), mat_espelho)

# Materiais da AC04 que ficaram sem uso (continuam no arquivo da AC04)
for nome in LAMBERT_PHONG_BLINN + ("MAT_Cinza_Pernas_Cadeira_AC04",):
    if nome in M and M[nome].users == 0:
        M.remove(M[nome])

# ----------------------------------------------------------------------------
# 3) UVs
# ----------------------------------------------------------------------------
for nome in ("Cad_01", "Cad_02", "Cad_03", "Cad_04", "Barra_Pilar"):
    uv_caixa_escala_real(O[nome].data)
# Barra_Arco: o UV é gerado pelo Blender para a curva (verificado: malha avaliada tem "UVMap")

# ----------------------------------------------------------------------------
# 4) Ajuste de render registrado no relatório e salvar
# ----------------------------------------------------------------------------
bpy.context.scene.eevee.use_raytracing = True   # reflexos reais para o espelho e o metal

bpy.ops.file.pack_all()
bpy.ops.wm.save_mainfile()
print("AC05 OK:", sorted(m.name for m in M if m.users))
