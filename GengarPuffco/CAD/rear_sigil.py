"""Printable red George wordmark with mirrored thorn ornament, viewed from +Y."""
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from manifold3d import Manifold, CrossSection, FillRule
from shapely.geometry import LineString

class OutlinePen(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs); self.contours=[]; self.points=[]
    def _moveTo(self,p): self.points=[p]
    def _lineTo(self,p): self.points.append(p)
    def _curveToOne(self,p1,p2,p3):
        p0=np.array(self.points[-1])
        for t in np.linspace(0,1,17)[1:]:
            self.points.append(((1-t)**3*p0+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)).tolist())
    def _qCurveToOne(self,p1,p2):
        p0=np.array(self.points[-1])
        for t in np.linspace(0,1,13)[1:]:
            self.points.append(((1-t)**2*p0+2*(1-t)*t*np.array(p1)+t*t*np.array(p2)).tolist())
    def _closePath(self): self.contours.append(self.points); self.points=[]
    def _endPath(self): self._closePath()

def rear_mask():
    font=TTFont(Path(__file__).parent/'Fonts/MetalMania-Regular.ttf')
    glyphs=font.getGlyphSet(); cmap=font.getBestCmap(); contours=[]; cursor=0
    for char in 'George':
        name=cmap[ord(char)]; pen=OutlinePen(glyphs); glyphs[name].draw(pen)
        contours.extend([[(x+cursor,y) for x,y in c] for c in pen.contours])
        cursor+=font['hmtx'][name][0]+35
    pts=np.concatenate(contours); lo=pts.min(axis=0); hi=pts.max(axis=0)
    # Broad readable name; slight arch follows the round back of the head.
    scale=65/(hi[0]-lo[0]); cx=(hi[0]+lo[0])/2
    outlines=[]
    for contour in contours:
        outlines.append([((x-cx)*scale,87+(y-lo[1])*scale+2*(1-((x-cx)*scale/33)**2)) for x,y in contour])
    design=CrossSection(outlines, FillRule.EvenOdd)
    # Custom pointed sigils with substantial roots rather than fragile hairlines.
    for side in [-1,1]:
        paths=[[(4,82),(14,79),(24,80),(35,86),(43,99)],
               [(15,80),(20,74),(27,71)],
               [(28,82),(37,80),(43,84)],
               [(35,87),(43,91),(46,98)],
               [(9,108),(19,110),(29,108),(37,103)]]
        for points in paths:
            points=[(side*x,z) for x,z in points]
            poly=LineString(points).buffer(.65,join_style=1)
            design=design+CrossSection([list(poly.exterior.coords)], FillRule.EvenOdd)
            end=np.array(points[-1]); prev=np.array(points[-2]); d=(end-prev)/np.linalg.norm(end-prev); n=np.array([-d[1],d[0]])
            design=design+CrossSection([[end-n*.65,end+d*3.5,end+n*.65]], FillRule.EvenOdd)
    # Local text x points toward screen-right when looking at the rear.
    return Manifold.extrude(design,55).transform([[-1,0,0,0],[0,0,1,25],[0,1,0,0]])
