import bpy, pathlib, json, math, hashlib
from mathutils import Vector

out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
font_path=next((p for p in [pathlib.Path('C:/Windows/Fonts/msjh.ttc'),pathlib.Path('C:/Windows/Fonts/simhei.ttf'),pathlib.Path('C:/Windows/Fonts/simsun.ttc')] if p.is_file()),None)
assert font_path is not None,'CJK font unavailable'
font=bpy.data.fonts.load(str(font_path))
text_body='中華文化閣'
glyphs=[]
for char in text_body:
 curve=bpy.data.curves.new('GlyphCheck','FONT');curve.body=char;curve.font=font;curve.size=1;curve.extrude=.001
 ob=bpy.data.objects.new('GlyphCheck',curve);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 bpy.ops.object.convert(target='MESH');coords=[tuple(round(v,5) for v in p.co) for p in ob.data.vertices]
 assert len(coords)>15,(char,'blank glyph')
 signature=hashlib.sha256(repr(coords).encode()).hexdigest()
 glyphs.append({'character':char,'codepoint':hex(ord(char)),'vertices':len(coords),'shape_sha256':signature})
 bpy.data.objects.remove(ob,do_unlink=True)
assert len({g['shape_sha256'] for g in glyphs})==len(text_body),'Missing-glyph substitution suspected'
specs={'LW_DarkOak':{'color':[.21,.105,.045],'roughness':.48,'metallic':0},
       'LW_SignGold':{'color':[.72,.49,.14],'roughness':.35,'metallic':.35}}
mats={}
for name,s in specs.items():
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*s['color'],1);mats[name]=mat

bpy.ops.mesh.primitive_cube_add(size=1,location=(23.2,20.79,2.68));board=bpy.context.object
board.name='SM_LW_Add_Culture_Plaque_DarkOak';board.dimensions=(1.65,.05,.38)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bev=board.modifiers.new('RoundedWoodEdge','BEVEL');bev.width=.006;bev.segments=3
bpy.ops.object.modifier_apply(modifier=bev.name);board.data.materials.append(mats['LW_DarkOak'])
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);board.select_set(False)

curve=bpy.data.curves.new('CulturePlaqueText','FONT');curve.body=text_body;curve.font=font;curve.size=.255
curve.align_x='CENTER';curve.extrude=.0014;curve.bevel_depth=.00025;curve.bevel_resolution=1;curve.resolution_u=12
letters=bpy.data.objects.new('SM_LW_Add_Culture_PlaqueLettering_SignGold',curve);bpy.context.collection.objects.link(letters)
letters.location=(23.2,20.762,2.58);letters.rotation_euler=(math.pi/2,0,0)
bpy.context.view_layer.objects.active=letters;letters.select_set(True);bpy.ops.object.convert(target='MESH')
letters.data.materials.append(mats['LW_SignGold']);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
manifest=[]
for ob,mat,part in [(board,'LW_DarkOak','CulturePlaque'),(letters,'LW_SignGold','CulturePlaqueLettering')]:
 uv=ob.data.uv_layers.new(name='UVMap')
 for face in ob.data.polygons:
  axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
  for li in face.loop_indices:
   co=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 mn=[min(v.co[a] for v in ob.data.vertices) for a in range(3)];mx=[max(v.co[a] for v in ob.data.vertices) for a in range(3)]
 manifest.append({'name':ob.name,'module':'Culture','part':part,'material':mat,'collision':False,
                  'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'bounds_m':{'min':mn,'max':mx},
                  'source_photos':['20240831_100320.jpg'],'dimensions_status':'provisional_display_dimensions'})
assert manifest[1]['bounds_m']['min'][0]>22.375 and manifest[1]['bounds_m']['max'][0]<24.025,'Text extends beyond plaque'
assert manifest[1]['bounds_m']['min'][2]>2.49 and manifest[1]['bounds_m']['max'][2]<2.87,'Text outside plaque height'
assert max(v.co.y for v in letters.data.vertices)<20.765,'Text must be in front of board (-Y)'
assert any(p.normal.y<-.9 for p in letters.data.polygons),'Missing forward-facing glyph caps'
for ob in [board,letters]:
 assert ob.location.length<1e-6 and all(abs(s-1)<1e-6 for s in ob.scale)
 ob.select_set(True)
bpy.context.view_layer.objects.active=board
bpy.ops.export_scene.fbx(filepath=str(out/'Addons.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Addons.blend'))
data={'version':1,'kind':'photo_visible_culture_plaque','not_as_built':True,'materials':specs,'meshes':manifest,
      'validation':{'font':str(font_path),'text':text_body,'glyphs':glyphs,'orientation':'front normal -Y, reading direction +X, upright +Z',
                    'world_baked_identity':True,'text_fits_board':True,'text_in_front_of_board':True,'no_render_required':True},
      'source':'https://hkla.org/wp-content/uploads/gallery/2024-aberdeen-technical-school-visit/20240831_100320.jpg',
      'notes':['Plaque wording and visual design are photo supported. Display position and dimensions remain provisional.']}
(out/'addons_manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIBRARY_ADDONS_COMPLETE',json.dumps({'meshes':len(manifest),'glyphs':len(glyphs),'vertices':sum(m['vertices'] for m in manifest)},ensure_ascii=False))
