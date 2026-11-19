"""Create isolated photo-informed material revisions. No scene mutation."""
import pathlib,json,unreal
wm_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
wm_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');wm_out=wm_root/'SourceAssets/Dining/WallFloorDetail_20261108'
wm_path='/Game/ATS/Dining/WallFloorDetail_20261108/Materials'
assert not unreal.EditorAssetLibrary.does_directory_exist(wm_path),'Inspect existing assets before rerun.'
# Preserve the resolved aggregate formula and its sampled far-distance mean.
wm_floorcode=(wm_work/'create_dining_registered_surface_materials.py').read_text(encoding='utf-8')
wm_floorcode=wm_floorcode.replace('/Game/ATS/Dining/StructuralSurfaces_20261108/Materials',wm_path)
wm_floorcode=wm_floorcode.replace('M_Dining_DryTerrazzo_StableGrain','M_Dining_DryTerrazzo_ContrastedAggregate')
wm_floorcode=wm_floorcode.replace('"AggregateScale_VisualEstimate", 1.0','"AggregateScale_VisualEstimate", 1.20')
wm_floorcode=wm_floorcode.replace('"AggregateContrast", 0.94','"AggregateContrast", 1.0')
wm_floorcode=wm_floorcode.replace('"DryRoughness", 0.55','"DryRoughness", 0.50')
wm_floorcode=wm_floorcode.replace('(202,195,173)','(208,205,193)').replace('(63,63,58)','(47,49,46)').replace('(137,135,123)','(127,130,123)').replace('(222,218,204)','(233,232,221)')
wm_floor_ns={};exec(compile(wm_floorcode,'new_wall_floor_terrazzo','exec'),wm_floor_ns)
wm_floor=wm_floor_ns['create_dining_registered_surface_materials'](save=True,include_wall_studies=False)
wm_wallcode=(wm_work/'create_dining_hall_mosaic.py').read_text(encoding='utf-8')
wm_wallcode=wm_wallcode.replace('/Game/ATS/Dining/StructuralSurfaces_20261108/Materials',wm_path)
wm_wallcode=wm_wallcode.replace('M_Dining_Hall_BasketMosaic','M_Dining_Hall_BasketMosaic_Multiscale').replace('M_Dining_Hall_CharcoalCap','M_Dining_Hall_CharcoalCap_FineJoint').replace('M_Dining_Hall_DarkTerrazzoSkirting','M_Dining_Hall_DarkTerrazzoSkirting_Contrasted')
wm_wallcode=wm_wallcode.replace('(226,225,222)','(232,232,229)').replace('(229,217,217)','(223,209,211)').replace('(230,227,216)','(230,229,218)').replace('(184,182,178)','(162,162,158)')
wm_wallcode=wm_wallcode.replace("'GrainPitchCM_VisualEstimate',.7","'GrainPitchCM_VisualEstimate',.9")
wm_wallcode=wm_wallcode.replace('(111,113,111)','(128,130,126)').replace('(210,210,204)','(224,224,216)')
wm_old='float3 colour = lerp(average,resolved,visibility);'
wm_new=r'''// Keep the larger block's average colour after narrow strips become
// subpixel. Only then fade the entire block toward the global mean.
float3 blockMean=0;
[unroll] for(int k=0;k<4;++k){
 if(k<strips){
  float3 hh=frac(float3(block.x,block.y,k)*float3(.1031,.1030,.0973));
  hh+=dot(hh,hh.yxz+33.33);hh=frac((hh.xxy+hh.yzz)*hh.zyx);
  float3 cc=(hh.x<.20)?(float3)PalePinkTile:((hh.x<.35)?(float3)PaleCreamTile:(float3)PaleGreyTile);
  blockMean+=cc*lerp(.965,1.025,hh.y);
 }
}
blockMean=lerp(blockMean/strips,(float3)GroutColour,meanJoint);
float blockVisibility=saturate((1.5-footprint/blockSize)/1.1);
float3 colour=lerp(average,lerp(blockMean,resolved,visibility),blockVisibility);'''
assert wm_old in wm_wallcode;wm_wallcode=wm_wallcode.replace(wm_old,wm_new)
wm_wall_ns={};exec(compile(wm_wallcode,'new_wall_floor_mosaic','exec'),wm_wall_ns)
wm_wall=wm_wall_ns['create_dining_hall_mosaic'](save=False)
wm_mat=wm_wall['materials']['mosaic'];wm_ml=unreal.MaterialEditingLibrary
# Fine recessed joints affect highlights without changing geometry/collision.
wm_mat.set_editor_property('tangent_space_normal',False)
wm_normalcode=r'''
float3 n=normalize((float3)SurfaceNormal);
if(abs(n.z)>.5)return n;
float2 t=normalize(float2(-n.y,n.x));
float2 p=float2(dot((float2)WorldPos.xy,t),WorldPos.z+2455.0);
float blockSize=3.6,width=1.2,halfJoint=.04;
float2 block=floor(p/blockSize),q=frac(p/blockSize)*blockSize;
bool rotated=fmod(abs(block.x+block.y),2.0)>.5;
if(rotated)q=q.yx;
float2 local=float2(q.x,frac(q.y/width)*width);
float4 edges=float4(local.x,blockSize-local.x,local.y,width-local.y);
float d=min(min(edges.x,edges.y),min(edges.z,edges.w));
float2 gradient=(d==edges.x)?float2(1,0):((d==edges.y)?float2(-1,0):((d==edges.z)?float2(0,1):float2(0,-1)));
float footprint=max(length(ddx(p)),length(ddy(p)));
float strength=.12*exp(-max(d-halfJoint,0)/.065)*step(halfJoint,d)*saturate((.9-footprint/width)/.7);
if(rotated)gradient=gradient.yx;
float3 slope=float3(t*gradient.x,gradient.y)*strength;
return normalize(n-slope);
'''
wm_custom=wm_ml.create_material_expression(wm_mat,unreal.MaterialExpressionCustom,-50,650);wm_custom.set_editor_property('code',wm_normalcode);wm_custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
wm_bind={'WorldPos':unreal.MaterialExpressionWorldPosition,'SurfaceNormal':unreal.MaterialExpressionVertexNormalWS};wm_inputs=[]
for wm_n in wm_bind:
 wm_i=unreal.CustomInput();wm_i.set_editor_property('input_name',wm_n);wm_inputs.append(wm_i)
wm_custom.set_editor_property('inputs',wm_inputs)
for wm_n,wm_cls in wm_bind.items():
 wm_node=wm_ml.create_material_expression(wm_mat,wm_cls,-450,650);assert wm_ml.connect_material_expressions(wm_node,'',wm_custom,wm_n)
assert wm_ml.connect_material_property(wm_custom,'',unreal.MaterialProperty.MP_NORMAL)
wm_ml.recompile_material(wm_mat)
assert unreal.EditorAssetLibrary.save_directory(wm_path,only_if_is_dirty=True,recursive=True)
wm_report={'status':'created_pending_live_visual_check','materials':{k:m.get_path_name() for k,m in dict(wm_wall['materials'],floor=wm_floor['materials']['floor']).items()},'geometry_unchanged':True,'mosaic_module_model_cm':3.6,'mosaic_strip_count_model':3,'mosaic_change':'Preserve block mean colour before global distant averaging; modest grout contrast and shallow joint highlight response. Module size unchanged.','floor_change':'Neutral pale warm matrix with more distinct dark/grey/ivory aggregate; aggregate scale 1.20 visual estimate, dry roughness .50; same stable sampled mean; no bump or displacement.','skirting_change':'More visible grey and light aggregate in the dark base strip','all_numeric_surface_settings_are_visual_estimates':True,'not_added':['Floor-band geometry','Floor slab-joint grid','Unregistered reflective wall panels','Unknown partitions']}
(wm_out/'material_creation.json').write_text(json.dumps(wm_report,ensure_ascii=False,indent=2),encoding='utf-8')
(wm_out/'floor_material_builder.py').write_text(wm_floorcode,encoding='utf-8');(wm_out/'mosaic_material_builder.py').write_text(wm_wallcode,encoding='utf-8')
print('WALL_FLOOR_MATERIALS_CREATED',wm_report['materials'])
