from pathlib import Path
import zipfile,xml.etree.ElementTree as E,numpy as np,json,shutil
src=Path(r'C:\Users\Panduh\Downloads\black+venom+marvelrivals.3mf');out=Path('outputs/Venom_480');out.mkdir(exist_ok=True);shutil.copy2(src,out/'Venom_original.3mf');z=zipfile.ZipFile(src);ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};r=E.fromstring(z.read('3D/3dmodel.model'));item=r.find('m:build/m:item',ns);a=np.fromstring(item.get('transform'),sep=' ').reshape(4,3);M=np.eye(4);M[:3,:]=a.T
V=[];F=[];attrs={}
with z.open('3D/Objects/object_1.model') as f:
 for _,e in E.iterparse(f,events=['end']):
  tag=e.tag.rsplit('}',1)[-1]
  if tag=='vertex':V.append((float(e.get('x')),float(e.get('y')),float(e.get('z'))));e.clear()
  elif tag=='triangle':
   F.append((int(e.get('v1')),int(e.get('v2')),int(e.get('v3'))))
   for k,v in e.attrib.items():
    if k not in ['v1','v2','v3']:attrs.setdefault(k,{});attrs[k][v]=attrs[k].get(v,0)+1
   e.clear()
V=np.asarray(V);F=np.asarray(F,dtype=np.int32);w=V@M[:3,:3].T+M[:3,3];print('VERTICES',len(V),'TRIANGLES',len(F),'SOURCE DIMENSIONS',np.ptp(w,axis=0).tolist(),'ATTRS',str(attrs)[:3000],flush=True)
# Restore native upright orientation, center XY, and put feet on Z=0, uniformly scale to 480mm.
scale=480/np.ptp(V[:,2]);V*=scale;V[:,:2]-=(V[:,:2].min(0)+V[:,:2].max(0))/2;V[:,2]-=V[:,2].min();np.savez_compressed('work/venom/source_480.npz',vertices=V,faces=F)
summary=dict(vertices=len(V),triangles=len(F),original_print_dimensions_mm=np.ptp(w,axis=0).tolist(),target_dimensions_mm=np.ptp(V,axis=0).tolist(),mesh_to_480_scale=scale,triangle_attribute_counts=attrs)
Path('work/venom/summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
