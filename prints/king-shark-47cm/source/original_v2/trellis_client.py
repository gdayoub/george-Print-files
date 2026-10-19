from pathlib import Path
import sys, json, os, time, traceback, shutil, re, base64
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'gradio_runtime'))
from gradio_client import Client, handle_file

def main():
    print('Connecting to official public Microsoft TRELLIS.2 Gradio API', flush=True)
    client = Client('https://microsoft-trellis-2.hf.space', download_files=str(BASE / 'trellis_downloads'), token=False, analytics_enabled=False)
    api = client.view_api(return_format='dict', print_info='--schema' in sys.argv)
    (BASE / 'trellis_api.json').write_text(json.dumps(api, indent=2), encoding='utf-8')
    print('API connected; schema saved', flush=True)
    if '--schema' in sys.argv:
        return
    status = {'source': 'https://huggingface.co/spaces/microsoft/TRELLIS.2',
              'source_image': str(BASE / 'realistic_concept.png'),
              'resolution': '1024', 'decimation_target': 500000,
              'texture_size': 2048, 'seed': 20261006,
              'started': time.strftime('%Y-%m-%dT%H:%M:%S')}
    def record(stage, **details):
        status.update(stage=stage, updated=time.strftime('%Y-%m-%dT%H:%M:%S'), **details)
        (BASE / 'trellis_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
        print(stage, details, flush=True)
    def predict(stage, **kwargs):
        record(stage)
        job = client.submit(**kwargs)
        previous = None
        while not job.done():
            s = job.status()
            current = str(s)
            if current != previous:
                record(stage, queue_status=current)
                previous = current
            time.sleep(5)
        result = job.result()
        record(stage + '_complete')
        return result
    try:
        predict('start_session', api_name='/start_session')
        preprocessed = predict('preprocessing', input=handle_file(str(BASE / 'realistic_concept.png')), api_name='/preprocess_image')
        record('preprocessing_saved', preprocessed_result=preprocessed)
        if isinstance(preprocessed, dict):
            preprocessed = preprocessed['path']
        if not isinstance(preprocessed, str):
            raise TypeError(f'Unexpected preprocessed image return: {type(preprocessed)}')
        shutil.copy2(preprocessed, BASE / 'trellis_preprocessed.png')
        html = predict('generating_1024', image=handle_file(preprocessed), seed=20261006, resolution='1024',
            ss_guidance_strength=7.5, ss_guidance_rescale=0.7, ss_sampling_steps=12, ss_rescale_t=5.0,
            shape_slat_guidance_strength=7.5, shape_slat_guidance_rescale=0.5, shape_slat_sampling_steps=12, shape_slat_rescale_t=3.0,
            tex_slat_guidance_strength=1.0, tex_slat_guidance_rescale=0.0, tex_slat_sampling_steps=12, tex_slat_rescale_t=3.0,
            api_name='/image_to_3d')
        (BASE / 'trellis_3d_preview.html').write_text(html, encoding='utf-8')
        for mode, idx, data in re.findall(r'id="view-m(\d+)-s(\d+)"\s+class="[^"]*"\s+src="data:image/jpeg;base64,([^"]+)"', html):
            folder = BASE / 'trellis_rendered_views'
            folder.mkdir(exist_ok=True)
            (folder / f'mode_{mode}_view_{idx}.jpg').write_bytes(base64.b64decode(data))
        output = predict('extracting_glb', decimation_target=500000, texture_size=2048, api_name='/extract_glb')
        out_file = output[0] if isinstance(output, (list, tuple)) else output
        if isinstance(out_file, dict):
            out_file = out_file['path']
        dst = BASE / 'King_Shark_realistic_v2_raw.glb'
        shutil.copy2(out_file, dst)
        record('complete', glb=str(dst), size_bytes=dst.stat().st_size, output=output)
    except Exception as e:
        record('error', error=str(e), exception=type(e).__name__)
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
