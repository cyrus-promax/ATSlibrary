import bpy,pathlib,json,math
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/StructuralSurfaces_20261108';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'SourceAssets/Dining/FullGroundFloor_20261108/ATS_Dining_Built.blend'))
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(p):u,v,h=p;return (-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
def campus(p):x=p.x+8;y=p.y+24;return (c*x+s*y,-s*x+c*y,p.z+24.55)
old=bpy.data.objects['SM_DiningBuilt_Tiles'];ov=[campus(old.matrix_world@v.co) for v in old.data.vertices]
vs=[];fs=[];mi=[]
def geom(vertices,faces,mat):
 base=len(vs);vs.extend(vertices);fs.extend([tuple(base+i for i in f) for f in faces]);mi.extend([mat]*len(faces))
preserved=0;removed=0
for p in old.data.polygons:
 if old.data.materials[p.material_index].name!='M_DiningBuild_DarkBorder':removed+=1;continue
 points=[ov[i] for i in p.vertices];mat=1 if sum(x[2] for x in points)/len(points)>1 else 2
 geom(points,[tuple(range(len(points)))],mat);preserved+=1
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
def box(p,sz,mat):
 x,y,z=p;dx,dy,dz=[v/2 for v in sz]
 geom([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
panels=[]
def surface(axis,fixed,a,b,inside_sign,openings):
 z0,z1=.15,1.8
 xs=sorted(set([a,b]+[max(a,min(b,x)) for o in openings for x in o[:2]]))
 zs=sorted(set([z0,z1]+[max(z0,min(z1,z)) for o in openings for z in o[2:]]))
 for x0,x1 in zip(xs,xs[1:]):
  for za,zb in zip(zs,zs[1:]):
   if x1-x0<.001 or zb-za<.001:continue
   if any(lo<(x0+x1)/2<hi and bot<(za+zb)/2<top for lo,hi,bot,top in openings):continue
   p=[fixed+inside_sign*.010,(x0+x1)/2,(za+zb)/2] if axis=='u' else [(x0+x1)/2,fixed+inside_sign*.010,(za+zb)/2]
   sz=[.002,x1-x0,zb-za] if axis=='u' else [x1-x0,.002,zb-za]
   box(p,sz,0);panels.append({'axis':axis,'fixed':fixed+inside_sign*.010,'extent':[x0,x1,za,zb]})
u0,u1,v0,v1=.23,19.68,3.67,30.4;dv0,dv1=12.54613555,14.74613555
back=[(2.675,4.875,0,2.8),(10.705,12.905,0,2.8)]+[(max(u0,a),min(u1,b),1.03,3.23) for a,b in [(.2,3.8),(4.2,7.8),(8.2,11.8),(12.2,15.8),(16.2,19.8)]]
windows=[(u-1.25,u+1.25,1,3) for u in [5.5,8.7,11.9,15.1,18.3]]
surface('v',v1-.091,u0+.1,u1-.01,-1,back)
surface('u',u1-.004,v0+.1,v1-.1,-1,[(dv0,dv1,0,2.8)])
surface('v',v0+.004,u0+.1,u1-.01,1,windows)
surface('u',u0+.013,v0+.1,v1-.1,1,[])
me=bpy.data.meshes.new('Dining_HallSurfacePanels');me.from_pydata([site(p) for p in vs],[],fs);me.update()
for n,col in [('M_Dining_Hall_BasketMosaic',(.72,.7,.69,1)),('M_Dining_Hall_CharcoalCap',(.025,.025,.025,1)),('M_Dining_Hall_DarkTerrazzoSkirting',(.035,.035,.035,1))]:
 mat=bpy.data.materials.new(n);mat.diffuse_color=col;me.materials.append(mat)
for p,m in zip(me.polygons,mi):p.material_index=m
ob=bpy.data.objects.new('SM_Dining_HallSurfacePanels',me);bpy.context.collection.objects.link(ob);ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Dining_HallSurfacePanels.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_HallSurfaces.blend'))
result={'source':'FullGroundFloor_20261108/ATS_Dining_Built.blend; SM_DiningBuilt_Tiles','removed_generic_square_tile_faces':removed,'preserved_existing_border_faces':preserved,'new_panels':panels,'meshes':1,'collision':False,'basis':'User identified the pictured main hall as the whole modelled dining hall. Replace generic square tiles with the visible pale interwoven rectangular mosaic appearance, preserving known openings and existing border geometry.','limits':['Surface pattern type is photo-supported. Exact tile dimensions and wall-dado heights remain modelling estimates.','Reflective wall panels and separate pink washing-zone surfaces are not mapped and are not newly built.','No guessed column grid, beam grid or floor band grid.']}
(out/'wall_panel_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('HALL_SURFACE_PANELS',len(panels),'REMOVED_GENERIC_FACES',removed,'BORDER_FACES_PRESERVED',preserved)
