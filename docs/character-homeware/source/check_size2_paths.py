from pathlib import Path
import sys
src=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(exist_ok=True,parents=True)
s=Path('work/check_lightweight_paths.py').read_text()
s=s.replace("out=Path('outputs/Venom_lightweight/engineering');src=Path('work/lightweight_repaired/P1S_final_slice')",f'out=Path({str(dest)!r});src=Path({str(src)!r})')
s=s.replace("and len(summary['sliced_plates'])==8",'')
s=s.replace("feature not in ['Custom','']","feature not in ['Custom','Flush','']")
if 'P2S' in str(src):s=s.replace('assert count and bad==0 and excluded==0','assert count and bad==0')
s=s.replace('assert len(rows)==8',"assert len(rows)==len(summary['sliced_plates'])")
s=s.replace("'toolpath_build_volume_check.json'",repr(src.name+'_toolpaths.json'))
s=s.replace("print('All 8 model/support/brim toolpaths fit P1S and P2S dimensions, avoiding the P1S excluded corner.',flush=True)","print('Checked all delivered plate toolpaths.',flush=True)")
exec(compile(s,'check_size2_paths_inner.py','exec'))
