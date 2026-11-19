import pathlib,json,unreal
hm_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work');hm_ns={}
hm_source=hm_work/'create_dining_hall_mosaic.py';exec(compile(hm_source.read_text(encoding='utf-8'),str(hm_source),'exec'),hm_ns)
hm_result=hm_ns['create_dining_hall_mosaic'](save=True)
hm_report={k:v for k,v in hm_result.items() if k!='materials'}
pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/Dining/StructuralSurfaces_20261108/wall_material_creation.json').write_text(json.dumps(hm_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('HALL_MOSAIC_MATERIALS_CREATED',hm_report)
