"""AC05 - Evolução da cena: Materiais PBR e Texturas (Blender 5.x / 4.5 LTS).

Como reproduzir (a partir de uma cópia da cena AP2/AC04, sem sobrescrever os originais):
    cp ../AP2/ap2_ibmec.blend AC05_CaioMedeiros.blend   # (e copie AP2/textures para AC05/textures)
    blender -b AC05_CaioMedeiros.blend --python ac05_materiais_pbr.py

O script:
  1. renomeia os materiais da cena com nomes descritivos (MAT_*);
  2. cria os 3 materiais PBR dos objetos autorais:
       - Cadeiras .......... MAT_Metal_Escovado_PBR  (Base Color + Roughness + Metallic + Normal)
       - Carteiras e mesa .. MAT_Madeira_PBR         (Base Color + Roughness + Normal)
       - Fachada da Barra .. MAT_Espelho_PBR         (cor sólida, Metallic = 1)
  3. gera UVs por projeção em caixa (box) em escala real (1 unidade UV = 1 metro);
  4. empacota as imagens no .blend e salva.
"""
import os

import bmesh
import bpy

AQUI = os.path.dirname(bpy.data.filepath)
TEX = os.path.join(AQUI, "textures_pbr")
UV_NOME = "UVMap"


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def novo_material(nome):
    """Cria (ou recria) um material com nós, limpo, com Principled BSDF -> Material Output."""
    antigo = bpy.data.materials.get(nome)
    if antigo:
        bpy.data.materials.remove(antigo)
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (560, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt, bsdf


def imagem(nome_arquivo, espaco):
    """Carrega a imagem e define o espaço de cor (sRGB para cor, Non-Color para dados)."""
    caminho = os.path.join(TEX, nome_arquivo)
    img = bpy.data.images.load(caminho, check_existing=True)
    img.colorspace_settings.name = espaco
    img.filepath = bpy.path.relpath(caminho)
    return img


def no_imagem(nt, img, x, y, rotulo):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    n.label = rotulo
    n.location = (x, y)
    n.interpolation = "Cubic"
    n.extension = "REPEAT"
    return n


def material_texturizado(nome, prefixo, escala_uv, mapas, normal_forca=1.0, extra=None):
    """Material Principled com mapas de imagem.

    mapas: dict com chaves 'cor', 'rough', 'normal' e (opcional) 'metal' -> arquivo.
    escala_uv: repetições por UV (UV está em metros; textura de N m => escala 1/N).
    """
    mat, nt, bsdf = novo_material(nome)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-900, 0)
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.location = (-700, 0)
    mapa.inputs["Scale"].default_value = (escala_uv, escala_uv, escala_uv)
    # Mapping/UV: coordenada UV como entrada
    nt.links.new(coord.outputs["UV"], mapa.inputs["Vector"])

    def liga(chave, espaco, entrada_bsdf, y):
        n = no_imagem(nt, imagem(mapas[chave], espaco), -400, y, chave)
        nt.links.new(mapa.outputs["Vector"], n.inputs["Vector"])
        nt.links.new(n.outputs["Color"], bsdf.inputs[entrada_bsdf])
        return n

    liga("cor", "sRGB", "Base Color", 300)                 # cor: sRGB
    liga("rough", "Non-Color", "Roughness", 0)             # dado: Non-Color
    if "metal" in mapas:
        liga("metal", "Non-Color", "Metallic", -300)       # dado: Non-Color
    else:
        bsdf.inputs["Metallic"].default_value = 0.0         # não metal
    # Normal: imagem Non-Color -> nó Normal Map (espaço tangente) -> Normal do BSDF
    n_img = no_imagem(nt, imagem(mapas["normal"], "Non-Color"), -400, -600, "normal (OpenGL)")
    nt.links.new(mapa.outputs["Vector"], n_img.inputs["Vector"])
    n_map = nt.nodes.new("ShaderNodeNormalMap")
    n_map.space = "TANGENT"
    n_map.uv_map = UV_NOME
    n_map.inputs["Strength"].default_value = normal_forca
    n_map.location = (200, -600)
    nt.links.new(n_img.outputs["Color"], n_map.inputs["Color"])
    nt.links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])
    for k, v in (extra or {}).items():
        bsdf.inputs[k].default_value = v
    return mat


def material_solido(nome, cor, rough, metal=0.0, extra=None):
    mat, nt, bsdf = novo_material(nome)
    bsdf.inputs["Base Color"].default_value = (*cor, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    for k, v in (extra or {}).items():
        bsdf.inputs[k].default_value = v
    return mat


def trocar_slot(obj_ou_malha, nome_antigo, mat_novo):
    """Troca o material de um slot na malha (vale para todos os objetos que a compartilham)."""
    malha = obj_ou_malha.data if hasattr(obj_ou_malha, "data") else obj_ou_malha
    for i, m in enumerate(malha.materials):
        if m and m.name == nome_antigo:
            malha.materials[i] = mat_novo
            return
    raise RuntimeError(f"slot {nome_antigo} não encontrado em {malha.name}")


def uv_caixa_escala_real(malha, nome=UV_NOME):
    """UV por projeção em caixa: cada face é projetada no plano do eixo dominante da normal.

    Coordenadas em metros (espaço do objeto) => densidade de textura uniforme e sem distorção
    nas faces planas. Os mapas se repetem via nó Mapping (REPEAT)."""
    if nome in malha.uv_layers:
        malha.uv_layers.remove(malha.uv_layers[nome])
    bm = bmesh.new()
    bm.from_mesh(malha)
    uv = bm.loops.layers.uv.new(nome)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        u, v = [i for i in range(3) if i != ax]
        # sinal para não espelhar a imagem nas faces voltadas para -eixo
        su = -1.0 if n[ax] < 0 and ax != 2 else 1.0
        for l in f.loops:
            p = l.vert.co
            l[uv].uv = (su * p[u], p[v])
    bm.to_mesh(malha)
    bm.free()
    malha.uv_layers.active = malha.uv_layers[nome]


# ----------------------------------------------------------------------------
# 1) Renomear materiais existentes (nomes descritivos) e convertê-los a PBR coerente
# ----------------------------------------------------------------------------
RENOMEAR = {
    "Branco": "MAT_Ibmec_Branco_PBR",
    "Amarelo": "MAT_Ibmec_Amarelo_PBR",
    "AzulEst": "MAT_Azul_Painel_PBR",
    "Azul": "MAT_Assento_Azul_PBR",
    "Cinza": "MAT_Cinza_Piso_PBR",
    "Madeira": "MAT_Madeira_Original",
    "Parede": "MAT_Parede_PBR",
    "Placa": "MAT_Placa_Azul_PBR",
    "Vidro": "MAT_Vidro_PBR",
    "Asfalto": "MAT_Asfalto_PBR",
    "Calcada": "MAT_Calcada_PBR",
    "Chao": "MAT_Gramado_PBR",
    "Parede_Textura": "MAT_Fachada_Textura_PBR",
    "Trajetoria": "MAT_Trajetoria_Foguete",
}
for velho, novo in RENOMEAR.items():
    if velho in bpy.data.materials:
        bpy.data.materials[velho].name = novo

# Palavra "Ibmec": mantém exatamente as cores (branco e amarelo), só ajusta o PBR (sem textura/relevo)
for nome, rough in (("MAT_Ibmec_Branco_PBR", 0.35), ("MAT_Ibmec_Amarelo_PBR", 0.35)):
    b = principled(bpy.data.materials[nome])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0

# Assento da cadeira: plástico azul-escuro (dielétrico), mesma cor da AP2
b = principled(bpy.data.materials["MAT_Assento_Azul_PBR"])
b.inputs["Roughness"].default_value = 0.45
b.inputs["Metallic"].default_value = 0.0

# ----------------------------------------------------------------------------
# 2) Materiais PBR dos três objetos autorais
# ----------------------------------------------------------------------------
# (a) Cadeiras -> metal escovado/pintado (Poly Haven "Metal Plate", CC0). Textura de 0,5 m.
mat_metal = material_texturizado(
    "MAT_Metal_Escovado_PBR",
    "metal",
    escala_uv=2.0,
    mapas={
        "cor": "metal_plate_diff_2k.jpg",
        "rough": "metal_plate_rough_2k.jpg",
        "metal": "metal_plate_metal_2k.jpg",
        "normal": "metal_plate_nor_gl_2k.jpg",
    },
    normal_forca=1.0,
)
# (b) Carteiras e mesa -> madeira (Poly Haven "Wood Table 001", CC0). Textura de 1,5 m.
mat_madeira = material_texturizado(
    "MAT_Madeira_PBR",
    "madeira",
    escala_uv=1.0 / 1.5,
    mapas={
        "cor": "wood_table_001_diff_2k.jpg",
        "rough": "wood_table_001_rough_2k.jpg",
        "normal": "wood_table_001_nor_gl_2k.jpg",
    },
    normal_forca=1.0,
)
# (c) Fachada da Barra -> espelho (cor sólida, Metallic = 1, rugosidade mínima)
mat_espelho = material_solido("MAT_Espelho_PBR", (0.92, 0.94, 0.97), rough=0.03, metal=1.0)

cad = bpy.data.objects["Cad_01"]               # malha "Cad" compartilhada por 10 objetos
trocar_slot(cad, "MAT_Cinza_Piso_PBR", mat_metal)          # slot "Cinza" da cadeira (estrutura)
# o piso da sala usa o mesmo material "Cinza": agora com nome próprio (continua como estava)
for nome_malha in ("Sala_Cart", "Sala_Mesa"):
    trocar_slot(bpy.data.objects[nome_malha], "MAT_Madeira_Original", mat_madeira)
trocar_slot(bpy.data.objects["Barra_Vidro"], "MAT_Vidro_PBR", mat_espelho)

# ----------------------------------------------------------------------------
# 3) UVs (projeção em caixa, escala real)
# ----------------------------------------------------------------------------
for obj_nome in ("Cad_01", "Sala_Cart", "Sala_Mesa"):
    uv_caixa_escala_real(bpy.data.objects[obj_nome].data)

# ----------------------------------------------------------------------------
# 4) Coleção auxiliar (documenta/agrupa os materiais da atividade) e Render
# ----------------------------------------------------------------------------
col = bpy.data.collections.get("AC05_Materiais_Texturas") or bpy.data.collections.new("AC05_Materiais_Texturas")
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
for m in (mat_metal, mat_madeira, mat_espelho):
    m.use_fake_user = True

# Espelho auxiliar na sala (a fachada da Barra quase não aparece na câmera principal):
# painel fino pendurado à frente do quadro azul, à direita das letras.
if "Espelho_Sala" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Espelho_Sala"])
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(66.0, 4.80, 2.7))
esp = bpy.context.active_object
esp.name = "Espelho_Sala"
esp.dimensions = (2.6, 0.05, 2.8)
esp.rotation_euler = (0.0, 0.0, -0.45)  # girado ~26° para refletir carteiras/cadeiras, não só o céu
esp.data.materials.append(mat_espelho)
for c in list(esp.users_collection):
    c.objects.unlink(esp)
col.objects.link(esp)

# Ajuste de render registrado no relatório: reflexos por ray tracing (EEVEE) para o espelho e o metal
bpy.context.scene.eevee.use_raytracing = True

# ----------------------------------------------------------------------------
# 5) Empacotar imagens e salvar
# ----------------------------------------------------------------------------
bpy.ops.file.pack_all()
bpy.ops.wm.save_mainfile()
print("AC05 OK:", [m.name for m in bpy.data.materials])
