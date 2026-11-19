import unreal,pathlib,json,hashlib,datetime
lw_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
lw_out=lw_root/'SourceAssets/LibraryWorkshop_20261108'
lw_stage='/Game/ATS/LibraryWorkshop_20261108'
lw_lib=unreal.EditorAssetLibrary;lw_tools=unreal.AssetToolsHelpers.get_asset_tools();lw_ml=unreal.MaterialEditingLibrary
lw_tm=json.loads((lw_out/'Textures/texture_manifest.json').read_text(encoding='utf-8'))
lw_textures={};lw_texture_report=[];lw_mats={}
for asset in lw_tm['assets']:
 for role,item in asset['maps'].items():
  src=pathlib.Path(item['path']);assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256']
  name='T_LW_'+asset['asset_key']+'_'+role
  path=lw_stage+'/Textures/'+name
  tex=lw_lib.load_asset(path) if lw_lib.does_asset_exist(path) else None
  if not tex:
   task=unreal.AssetImportTask();task.filename=str(src);task.destination_path=lw_stage+'/Textures';task.destination_name=name;task.automated=True;task.save=False;task.replace_existing=False
   lw_tools.import_asset_tasks([task]);tex=next(t for t in task.get_objects() if isinstance(t,unreal.Texture2D))
  normal=role=='normal_gl';tex.set_editor_property('srgb',role=='base_color');tex.set_editor_property('max_texture_size',4096);tex.set_editor_property('lod_bias',0)
  tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if normal else unreal.TextureCompressionSettings.TC_DEFAULT)
  tex.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_WORLD_NORMAL_MAP if normal else unreal.TextureGroup.TEXTUREGROUP_WORLD)
  if normal:tex.set_editor_property('flip_green_channel',True)
  assert lw_lib.save_loaded_asset(tex,only_if_is_dirty=False)
  assert tex.blueprint_get_size_x()==4096 and tex.blueprint_get_size_y()==4096,(name,tex.blueprint_get_size_x(),tex.blueprint_get_size_y())
  lw_textures[(asset['asset_key'],role)]=tex
  lw_texture_report.append({'asset':tex.get_path_name(),'source':str(src),'role':role,'width':4096,'height':4096,'srgb':role=='base_color','normal_green_flipped':normal,'max_texture_size':4096,'source_sha256':item['sha256']})
  (lw_out/'texture_import_progress.json').write_text(json.dumps(lw_texture_report,ensure_ascii=False,indent=2),encoding='utf-8')

def lw_node(m,cls,x=0,y=0):return lw_ml.create_material_expression(m,cls,x,y)
def lw_const(m,value,prop=None):
 n=lw_node(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',float(value))
 if prop is not None:assert lw_ml.connect_material_property(n,'',prop)
 return n
def lw_vec(m,value,prop=None):
 n=lw_node(m,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*value,1))
 if prop is not None:assert lw_ml.connect_material_property(n,'',prop)
 return n
def lw_newmat(key):
 name='M_'+key;path=lw_stage+'/Materials/'+name
 m=lw_lib.load_asset(path) if lw_lib.does_asset_exist(path) else lw_tools.create_asset(name,lw_stage+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 assert m;lw_ml.delete_all_material_expressions(m);lw_mats[key]=m;return m
def lw_link(a,out,b,pin):assert lw_ml.connect_material_expressions(a,out,b,pin)
def lw_finish(m):lw_ml.recompile_material(m)
def lw_pbr(key,asset,uvscale,tint=(1,1,1),lift=0,normal_strength=.55):
 m=lw_newmat(key);uv=lw_node(m,unreal.MaterialExpressionTextureCoordinate,-900,200);uv.set_editor_property('u_tiling',uvscale);uv.set_editor_property('v_tiling',uvscale)
 for role,prop in [('base_color',unreal.MaterialProperty.MP_BASE_COLOR),('normal_gl',unreal.MaterialProperty.MP_NORMAL),('roughness',unreal.MaterialProperty.MP_ROUGHNESS),('ambient_occlusion',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)]:
  tex=lw_textures.get((asset,role))
  if not tex:continue
  sample=lw_node(m,unreal.MaterialExpressionTextureSample,-600,100);sample.set_editor_property('texture',tex)
  sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if role=='normal_gl' else (unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if role=='base_color' else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR));lw_link(uv,'',sample,'UVs');result=sample;output='RGB'
  if role=='base_color':
   mul=lw_node(m,unreal.MaterialExpressionMultiply,-300,0);lw_link(sample,'RGB',mul,'A');lw_link(lw_vec(m,tint),'',mul,'B');result=mul;output=''
   if lift:
    add=lw_node(m,unreal.MaterialExpressionAdd,-100,0);add.set_editor_property('const_b',lift);lw_link(result,'',add,'A');result=add
  elif role=='normal_gl':
   mul=lw_node(m,unreal.MaterialExpressionMultiply,-300,200);lw_link(sample,'RGB',mul,'A');lw_link(lw_vec(m,(normal_strength,normal_strength,1)),'',mul,'B');norm=lw_node(m,unreal.MaterialExpressionNormalize,-100,200);lw_link(mul,'',norm,str(lw_ml.get_material_expression_input_names(norm)[0]));result=norm;output=''
  elif role=='roughness':
   clamp=lw_node(m,unreal.MaterialExpressionClamp,-300,400);clamp.set_editor_property('min_default',.28);clamp.set_editor_property('max_default',.92);lw_link(sample,'R',clamp,str(lw_ml.get_material_expression_input_names(clamp)[0]));result=clamp;output=''
  assert lw_ml.connect_material_property(result,output,prop)
 lw_const(m,0,unreal.MaterialProperty.MP_METALLIC);lw_finish(m);return m

lw_pbr('LW_PaleOak','oak_veneer_02',1,(.88,.88,.88),.045,.28)
lw_pbr('LW_DarkOak','oak_veneer_02',1,(.34,.23,.14),.012,.35)
lw_pbr('LW_FloorOak','WoodFloor051',2/1.8,(.93,.93,.93),.025,.3)
lw_pbr('LW_Plaster','white_plaster_02',2,(.07,.07,.07),.78,.05)
lw_pbr('LW_Wicker','oak_veneer_02',1,(.63,.43,.22),.015,.5)
def lw_simple(key,rgb,rough=.5,metal=0):
 m=lw_newmat(key);colour=lw_vec(m,rgb,unreal.MaterialProperty.MP_BASE_COLOR);lw_const(m,rough,unreal.MaterialProperty.MP_ROUGHNESS);lw_const(m,metal,unreal.MaterialProperty.MP_METALLIC);lw_finish(m);return m,colour
for key,rgb,rough,metal in [('LW_BlackMetal',(.018,.022,.025),.3,.65),('LW_WhiteMetal',(.75,.76,.74),.38,.12),('LW_Rubber',(.012,.014,.016),.84,0),('LW_Orange',(.65,.18,.026),.5,0),('LW_Fabric',(.11,.085,.060),.94,0),('LW_Paper',(.76,.72,.61),.88,0),('LW_BookRed',(.30,.035,.025),.62,0),('LW_BookBlue',(.035,.10,.20),.56,0),('LW_BookGreen',(.055,.15,.09),.62,0),('LW_BookTan',(.50,.32,.14),.64,0),('LW_BookGrey',(.24,.26,.25),.64,0),('LW_Plant',(.065,.19,.035),.66,0),('LW_DisplayBase',(.12,.145,.16),.8,0)]:lw_simple(key,rgb,rough,metal)
lw_glass,lw_gc=lw_simple('LW_Glass',(.80,.92,.94),.075,0);lw_glass.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);lw_glass.set_editor_property('two_sided',True);lw_const(lw_glass,.12,unreal.MaterialProperty.MP_OPACITY);lw_finish(lw_glass)
lw_simple('LW_ExitGreen',(.015,.30,.16),.5,0)
lw_simple('LW_ScreenWhite',(.83,.83,.80),.9,0)
lw_light,lw_lc=lw_simple('LW_Light',(1,.91,.77),.3,0);lw_mul=lw_node(lw_light,unreal.MaterialExpressionMultiply);lw_mul.set_editor_property('const_b',5);lw_link(lw_lc,'',lw_mul,'A');lw_ml.connect_material_property(lw_mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);lw_finish(lw_light)
assert lw_lib.save_directory(lw_stage,only_if_is_dirty=True,recursive=True)
lw_report={'time':datetime.datetime.now().isoformat(),'texture_count':len(lw_texture_report),'textures':lw_texture_report,'materials':{k:v.get_path_name() for k,v in lw_mats.items()},'resolution':'Original 4096x4096 source files; max texture size4096 and LOD bias0','limit':'Photographic appearance matching, not certified original school material manufacturer.'}
(lw_out/'materials_import_report.json').write_text(json.dumps(lw_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIBRARY_WORKSHOP_MATERIALS',len(lw_texture_report),len(lw_mats))
