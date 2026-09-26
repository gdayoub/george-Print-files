from pathlib import Path
import json,numpy as np,trimesh,bpy
from mathutils import Vector
from manifold3d import Manifold as M,Mesh64,OpType
R=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(R/'CAD/Gengar_Compact_EDITABLE.blend'))
for e in json.loads((R/'CAD/outputs/manifest.json').read_text()):
 ob=bpy.data.objects[e['name']];a=np.load(R/'CAD/outputs'/e['file']);t=trimesh.Trimesh(a['vertices'],a['faces'],process=True)
 solid=M(Mesh64(np.asarray(t.vertices),np.asarray(t.faces,dtype=np.uint64)))
 solid=M.batch_boolean([c for c in solid.decompose() if c.volume()>1e-5],OpType.Add)
 cut=solid ^ M.cube((240,160,220)).translate((-120,0,-20))
 if cut.volume()<1e-6:ob.hide_render=True;continue
 mesh=cut.to_mesh64();me=bpy.data.meshes.new(e['name']+'_section');me.from_pydata(np.asarray(mesh.vert_properties)[:,:3].tolist(),[],np.asarray(mesh.tri_verts).tolist());me.update();mat=ob.data.materials[0];ob.data=me;me.materials.append(mat)
 if e['name'].startswith('ORIGINAL'):
  mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.06,.45,.34,1)
s=bpy.context.scene;cam=s.camera;cam.location=(110,-320,151);cam.rotation_euler=(Vector((0,5,61))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=200
s.render.filepath=str(R/'Previews/05_section_foundation_highlighted.png');bpy.ops.render.render(write_still=True)
