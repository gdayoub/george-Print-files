from pathlib import Path
import ctypes,os,sys
folder=r'C:\Users\Panduh\AppData\Local\Programs\BambuStudioPortable-02.08.02.61';os.add_dll_directory(folder);os.chdir(folder);lib=ctypes.WinDLL(folder+r'\BambuStudio.dll');f=lib.bambustu_main;f.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_wchar_p)];f.restype=ctypes.c_int
args=[folder+r'\bambu-studio.exe']+sys.argv[1:];print('RETURN',f(len(args),(ctypes.c_wchar_p*(len(args)+1))(*args,None)),flush=True)
