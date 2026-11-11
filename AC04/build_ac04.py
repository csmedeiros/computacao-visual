"""AC04 - gera AC04_CaioMedeiros.blend a partir da AP1 (nao altera o original)."""
import bpy, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "..", "AP1", "ap1_ibmec.blend"))
sc = bpy.context.scene
O = bpy.data.objects
if bpy.app.version < (5, 0, 0):   # AP1 foi salva no 5.x; no 4.5 o EEVEE chama-se EEVEE_NEXT
    sc.render.engine = 'BLENDER_EEVEE_NEXT'

# --- colecoes de organizacao ---
def col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in sc.collection.children: sc.collection.children.link(c)
    return c
c_mat, c_luz = col("AC04_Materiais"), col("AC04_Luzes")
for n in ("Luz_Key", "Luz_Fill", "Luz_Rim", "Sol"):
    for c in O[n].users_collection: c.objects.unlink(O[n])
    c_luz.objects.link(O[n])

# --- materiais (Principled BSDF; valores = pontos de partida da atividade) ---
def mat(name, color, rough, spec):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    k = "Specular IOR Level" if "Specular IOR Level" in b.inputs else "Specular"
    b.inputs[k].default_value = spec
    m.diffuse_color = color
    return m
M_L = mat("MAT_Lambert",     (0.85, 0.10, 0.10, 1), 1.0, 0.05)  # vermelho fosco
M_P = mat("MAT_Phong",       (0.10, 0.65, 0.15, 1), 0.2, 0.5)   # verde polido
M_B = mat("MAT_BlinnPhong",  (0.60, 0.12, 0.01, 1), 0.1, 1.0)   # laranja muito polido

def assign(obj, m, only=None):
    for i, s in enumerate(obj.material_slots):
        if only is None or s.material.name in only:
            obj.material_slots[i].material = m

assign(O["Barra_Ala"], M_L, only=("Parede",))             # Lambert -> corpo da Barra
assign(O["Barra_Arco"], M_P); assign(O["Barra_Pilar"], M_P)  # Phong -> arco/pilares
# cadeiras: mesma forma, um material cada -> comparacao direta (Cad_03 e Cad_04 = Blinn-Phong)
for n in ("Cad_01", "Cad_02", "Cad_03", "Cad_04"):
    O[n].data = O[n].data.copy()   # malha compartilhada -> 1 material por cadeira
for n, m in (("Cad_01", M_L), ("Cad_02", M_P), ("Cad_03", M_B), ("Cad_04", M_B)):
    assign(O[n], m, only=("Azul",))

# cadeiras movidas para a frente da fachada (fora do vidro) para ficarem visiveis na imagem final
O["Cadeiras"].location = (20, -6.0, 0.0)
O["Cadeiras"].scale = (1.6, 1.6, 1.6)

# --- camera de comparacao (luzes e Cam_Main intactas) ---
cam = bpy.data.objects.new("Cam_Comparacao", bpy.data.cameras.new("Cam_Comparacao"))
sc.collection.objects.link(cam)
cam.location = (20, -13.5, 1.6); cam.rotation_euler = (math.radians(90), 0, 0)
cam.data.lens = 35

bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "AC04_CaioMedeiros.blend"))
