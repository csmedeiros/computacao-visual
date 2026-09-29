# AC03 - Geometric Park | Computação Visual (Ibmec) | Caio Medeiros
# Uso: blender --background --python AC03_CaioMedeiros.py
import bpy, math, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
NAME = "AC03_CaioMedeiros"
F_START, F_END, FPS = 1, 96, 24          # 4 segundos

# ---------- cena limpa ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start, scene.frame_end = F_START, F_END
scene.render.fps = FPS

def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    m.diffuse_color = (*rgb, 1)
    return m

def paint(obj, m):
    obj.data.materials.append(m)

def name_it(obj, n):
    obj.name = n
    obj.data.name = n + "_mesh"
    return obj

# ---------- chão ----------
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = name_it(bpy.context.object, "Chao")
paint(ground, mat("M_Chao", (0.25, 0.55, 0.28)))

# ---------- 2D (formas planas, no plano XY) ----------
# Quadrado = Plane
bpy.ops.mesh.primitive_plane_add(size=2, location=(-4, -3, 0.02))
sq = name_it(bpy.context.object, "Quadrado2D")
sq.scale = (1.2, 1.2, 1)
paint(sq, mat("M_Quad", (0.15, 0.35, 0.85)))

# Triângulo = malha criada a partir de vértices
me = bpy.data.meshes.new("Triangulo2D_mesh")
me.from_pydata([(-1, -0.8, 0), (1, -0.8, 0), (0, 1, 0)], [], [(0, 1, 2)])
me.update()
tri = bpy.data.objects.new("Triangulo2D", me)
scene.collection.objects.link(tri)
tri.location = (-1.5, -3, 0.03)
paint(tri, mat("M_Tri", (0.95, 0.75, 0.1)))

# Círculo = Circle preenchido (N-gon)
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1.1, fill_type='NGON', location=(4, -3, 0.02))
circ = name_it(bpy.context.object, "Circulo2D")
paint(circ, mat("M_Circ", (0.9, 0.2, 0.25)))

# ---------- 3D ----------
bpy.ops.mesh.primitive_cube_add(size=2, location=(-4, 2, 1))
cube = name_it(bpy.context.object, "Cubo")
paint(cube, mat("M_Cubo", (0.6, 0.3, 0.8)))

bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.6, depth=2, location=(0, 2, 1.5))
cyl = name_it(bpy.context.object, "Cilindro")
cyl.scale = (1, 1, 1.5)                       # coluna alta
paint(cyl, mat("M_Cil", (0.9, 0.9, 0.85)))

bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=(4, 2, 1))
sph = name_it(bpy.context.object, "Esfera")
paint(sph, mat("M_Esf", (0.2, 0.75, 0.75)))
bpy.ops.object.shade_smooth()

# Bônus: hierarquia (pai-filho) -> esfera pequena orbita com a rotação do cilindro
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.35, location=(0, 2, 0))
orb = name_it(bpy.context.object, "Orbita")
paint(orb, mat("M_Orb", (1, 0.4, 0.1)))
orb.parent = cyl
orb.location = (1.8, 0, 0.5)                  # espaço LOCAL do cilindro (pai)

# ---------- transformações via Python (graus -> radianos) ----------
tri.rotation_euler = (0, 0, math.radians(0))
cube.rotation_euler = (0, 0, math.radians(15))     # inclinação inicial
sph.rotation_euler = (math.radians(20), 0, 0)
sph.scale = (1, 1, 1.0)

# ---------- animação ----------
prefs = bpy.context.preferences.edit
prefs.keyframe_new_interpolation_type = 'LINEAR'   # rotações/translações constantes

def key(obj, path, frame, index=-1):
    obj.keyframe_insert(data_path=path, frame=frame, index=index)

# 2D: triângulo translada em X e gira 360° em Z
tri.location.x = -1.5;  tri.rotation_euler.z = 0
key(tri, "location", F_START); key(tri, "rotation_euler", F_START)
tri.location.x = 1.5;   tri.rotation_euler.z = math.radians(360)
key(tri, "location", F_END);   key(tri, "rotation_euler", F_END)

# 3D: cubo escala 1 -> 1.6 (com ponto intermediário) e gira 15° -> 195° em Z
prefs.keyframe_new_interpolation_type = 'BEZIER'
cube.scale = (1, 1, 1);        cube.location.z = 1.0
cube.rotation_euler.z = math.radians(15)
key(cube, "scale", F_START); key(cube, "location", F_START); key(cube, "rotation_euler", F_START)
cube.scale = (1.8, 1.8, 1.8);  cube.location.z = 1.8            # pico aos 50%
cube.rotation_euler.z = math.radians(105)
key(cube, "scale", 48); key(cube, "location", 48); key(cube, "rotation_euler", 48)
cube.scale = (1, 1, 1);        cube.location.z = 1.0
cube.rotation_euler.z = math.radians(195)
key(cube, "scale", F_END); key(cube, "location", F_END); key(cube, "rotation_euler", F_END)

# Cilindro gira 360° (arrasta a esfera-filha)
prefs.keyframe_new_interpolation_type = 'LINEAR'
cyl.rotation_euler.z = 0;  key(cyl, "rotation_euler", F_START)
cyl.rotation_euler.z = math.radians(360); key(cyl, "rotation_euler", F_END)

# Esfera "respira" no eixo Z (escala) - variação temporal
prefs.keyframe_new_interpolation_type = 'BEZIER'
sph.scale = (1, 1, 1);   key(sph, "scale", F_START)
sph.scale = (1.2, 1.2, 0.7); key(sph, "scale", 24)
sph.scale = (1, 1, 1);   key(sph, "scale", 48)
sph.scale = (1.2, 1.2, 0.7); key(sph, "scale", 72)
sph.scale = (1, 1, 1);   key(sph, "scale", F_END)

# ---------- luz, câmera, mundo ----------
bpy.ops.object.light_add(type='SUN', location=(6, -6, 12))
sun = bpy.context.object; sun.name = "Sol"
sun.data.energy = 4
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))

bpy.ops.object.camera_add(location=(0, -19, 11))
cam = bpy.context.object; cam.name = "Camera"
cam.data.lens = 32
cam.rotation_euler = (Vector((0, 0, 0.8)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

world = bpy.data.worlds.new("Mundo")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.75, 0.95, 1)
scene.world = world

# ---------- render ----------
for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'):
    try:
        scene.render.engine = eng; break
    except TypeError:
        pass
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.frame_set(36)
scene.render.filepath = os.path.join(OUT, NAME + ".png")
bpy.ops.render.render(write_still=True)
scene.frame_set(F_START)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, NAME + ".blend"))
print("OK", scene.render.engine)
