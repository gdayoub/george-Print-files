from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E,re
import numpy as np
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parent.parent;N={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};P='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
checks=json.loads((R/'Reports/geometry_validation.json').read_text());reports={}
def transform(s):
 a=np.array([float(x) for x in s.split()]);T=np.eye(4);T[:3,:3]=a[:9].reshape(3,3).T;T[:3,3]=a[9:];return T
for path in (R/'Print/P1S').glob('*.3mf'):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  rt=E.fromstring(z.read('3D/3dmodel.model'));cfg=E.fromstring(z.read('Metadata/model_settings.config'));settings=json.loads(z.read('Metadata/project_settings.config'))
  report={'archive_valid':True,'originals':{},'mesh_repairs':{}}
  for it in rt.find('m:build',N):
   T=transform(it.get('transform'));sv=np.linalg.svd(T[:3,:3],compute_uv=False);assert np.max(np.abs(sv-1))<1e-6
  for ob in cfg.findall('object'):
   resource=next(o for o in rt.findall('m:resources/m:object',N) if o.get('id')==ob.get('id'))
   for part in ob.findall('part'):
    md={a.get('key'):a.get('value') for a in part.findall('metadata')};name=md.get('name','');stat=part.find('mesh_stat')
    if stat is not None:report['mesh_repairs'][name]=stat.attrib
    if not name.startswith('ORIGINAL'):continue
    comp=next(c for c in resource.findall('m:components/m:component',N) if c.get('objectid')==part.get('id'))
    sub=E.fromstring(z.read(comp.get(P+'path').lstrip('/')));o=next(o for o in sub.findall('m:resources/m:object',N) if o.get('id')==part.get('id'));me=o.find('m:mesh',N)
    v=np.array([[float(a.get(k)) for k in 'xyz'] for a in me.find('m:vertices',N)]);faces=me.find('m:triangles',N);T=transform(comp.get('transform'));v=v@T[:3,:3].T+T[:3,3]
    role='base' if 'BASE' in name else 'lid';src=np.load(R/'Foundations'/f'{role}_exact.npz');T=np.array(checks[role+'_transform']);expected=src['vertices']@T[:3,:3].T+T[:3,3]
    # Bambu recenters a singleton object before applying its rigid build pose.
    # Remove only that translation; never normalize dimensions or scale.
    recenter=(expected.min(0)+expected.max(0)-v.min(0)-v.max(0))/2
    if len(ob.findall('part'))>1:assert np.max(np.abs(recenter))<.0001
    v=v+recenter
    forward=cKDTree(expected).query(v)[0].max();reverse=cKDTree(v).query(expected)[0].max();err=float(max(forward,reverse))
    assert len(faces)==len(src['faces']);assert err<.0001,(path,name,err)
    report['originals'][name]={'triangles':len(faces),'max_bidirectional_vertex_distance_mm':err,'rigid_build_scale':True}
  assert str(settings['xy_hole_compensation'])=='0' and str(settings['xy_contour_compensation'])=='0'
  report['zero_XY_compensation']=True
  gc=z.read('Metadata/plate_1.gcode').decode(errors='replace');heights=[float(x) for x in re.findall(r'; layer height: ([0-9.]+)',gc)]
  report['layer_height_values_mm']=sorted(set(heights))
  if heights:assert max(heights)<=.20001
  reports[path.name]=report
(R/'Reports/native_verification.json').write_text(json.dumps(reports,indent=2))
print(json.dumps({k:{'originals':v['originals'],'repairs':{n:{a:b for a,b in d.items() if a!='face_count' and b!='0'} for n,d in v['mesh_repairs'].items()}} for k,v in reports.items()},indent=2))
