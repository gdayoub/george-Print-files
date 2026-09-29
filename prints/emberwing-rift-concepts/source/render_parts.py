"""Render a labelled contact sheet directly from the distributed STL geometry."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import trimesh

ROOT = Path(__file__).resolve().parents[1]
parts = [p for p in json.loads((ROOT/'validation/mesh_validation.json').read_text())['parts'] if p['file']]
fig = plt.figure(figsize=(16, 12), facecolor='#141217')
fig.suptitle('EMBERWING + RIFT / BED FOOTPRINTS', color='#fff4f0', fontsize=25, y=.97, weight='bold')
fig.text(.5, .925, 'Top views of actual STL geometry • Rear face down • X × Y × Z in millimetres', ha='center', color='#bcaeb4', fontsize=12)
for index, part in enumerate(parts):
    mesh = trimesh.load(ROOT/part['file'], force='mesh')
    ax = fig.add_subplot(3, 4, index+1, facecolor='#141217')
    # Orthographic painter's order avoids triangulation artifacts in mplot3d.
    order=np.argsort(mesh.triangles_center[:,2])
    brightness=.45+.55*np.clip(mesh.face_normals[:,2],0,1)
    colors=np.array([.86,.13,.24])[None,:]*brightness[:,None]
    ax.add_collection(PolyCollection(mesh.triangles[order,:,:2], facecolors=colors[order], edgecolors='none'))
    size = 230
    center = mesh.bounds.mean(axis=0)
    ax.set_xlim(center[0]-size*.55, center[0]+size*.55)
    ax.set_ylim(center[1]-size*.55, center[1]+size*.55)
    ax.set_aspect('equal'); ax.set_axis_off()
    ax.set_title(part['part'] + ('  ×5' if part['part'].startswith('RIFT') else ''), color='#fff4f0', fontsize=11, pad=-8)
    dims=' × '.join(f'{v:g}' for v in part['dimensions_xyz_mm'])
    ax.text(.5, -.03, dims+' mm', transform=ax.transAxes, color='#bcaeb4', fontsize=9, ha='center')
fig.subplots_adjust(top=.90, bottom=.05, left=.025, right=.975, wspace=.04, hspace=.14)
fig.text(.5, .015, 'Mesh integrity checked. Physical print, assembly and adhesive mounting untested.', ha='center', color='#bcaeb4', fontsize=11)
fig.savefig(ROOT/'images/print-parts.png', dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
