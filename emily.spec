# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py',
              'scripts/training/training_streamlined.py',
              'scripts/training/training_not_streamlined.py',
              'scripts/training/shared_model_functions.py',
              'scripts/processing/shared_processing_functions.py',
              'scripts/processing/processing_streamlined.py',
              'scripts/processing/processing_not_streamlined.py',
              'scripts/dataset/dataset_generator.py',
              'scripts/dataset/dataset_functions.py',
              'scripts/arduino/arduino.py',
              'imports.py'],
             pathex=['C:\Bharat\Imperial College London\Year 3\GP\Shared\Project-EMILY'],
             binaries=[],
             datas=[('scripts','scripts'),
                    ('Images','Images'),
                    ('arduino_inference_script','arduino_inference_script'),
                    ('arduino_record_script','arduino_record_script'),
                    ('C:\\Users\\bhara\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\librosa\\util\\example_data','librosa/util/example_data/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='emily',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          icon='Images/emily.ico')