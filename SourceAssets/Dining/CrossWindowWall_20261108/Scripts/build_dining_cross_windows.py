import bpy,pathlib,json,math,hashlib
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/CrossWindowWall_20261108';out.mkdir(parents=True,exist_ok=True)
anchor=json.loads((out/'anchor_confirmation.json').read_text(encoding='utf-8'))
cross_v=anchor['confirmed_horizontal_v'];cross_h=2.62
centres=[cross_v-1.10,cross_v+2.35];width=1.5;bottom=.9;top=3.15
openings=[(v-width/2,v+width/2,bottom,top) for v in centres]
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(p):u,v,h=p;return (-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
def local(p):x=p.x+8;y=p.y+24;return (c*x+s*y,-s*x+c*y,p.z+24.55)
facebox=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
materials={};records=[];objects=[];source_hashes=[]
def material(name,colour=(.7,.7,.7,1)):
 if name not in materials:
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=colour;materials[name]=m
 return materials[name]
def dataset():return {'v':[],'f':[],'m':[],'uv':[]}
def add(data,vs,fs,mat,uvs=None):
 n=len(data['v']);data['v'].extend(vs);data['f'].extend([tuple(n+i for i in f) for f in fs]);data['m'].extend([mat]*len(fs));data['uv'].extend(uvs if uvs is not None else [None]*len(fs))
def box(data,p,sz,mat):
 x,y,z=p;dx,dy,dz=[v/2 for v in sz]
 add(data,[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)],facebox,mat)
def rect_cut(data,fixed,depth,vlo,vhi,zlo,zhi,mat):
 xs=sorted(set([vlo,vhi]+[max(vlo,min(vhi,x)) for o in openings for x in o[:2]]))
 zs=sorted(set([zlo,zhi]+[max(zlo,min(zhi,x)) for o in openings for x in o[2:]]))
 for va,vb in zip(xs,xs[1:]):
  for za,zb in zip(zs,zs[1:]):
   if vb-va<.0001 or zb-za<.0001:continue
   if any(a<(va+vb)/2<b and lo<(za+zb)/2<hi for a,b,lo,hi in openings):continue
   box(data,(fixed,(va+vb)/2,(za+zb)/2),(depth,vb-va,zb-za),mat)
def read_source(rel,name):
 path=root/rel;sha=hashlib.sha256(path.read_bytes()).hexdigest()
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):
  assert name in src.objects,name;dst.objects=[name]
 ob=dst.objects[0];vs=[local(ob.matrix_world@v.co) for v in ob.data.vertices]
 uvl=ob.data.uv_layers.active
 rows=[{'verts':list(p.vertices),'material':ob.data.materials[p.material_index].name,'uv':[tuple(uvl.data[li].uv) for li in p.loop_indices] if uvl else None} for p in ob.data.polygons]
 source_hashes.append({'path':str(path),'before':sha});bpy.data.objects.remove(ob,do_unlink=True)
 return vs,rows
def output_mesh(name,data,role,bevel=False):
 used=list(dict.fromkeys(data['m']));me=bpy.data.meshes.new(name);me.from_pydata([site(p) for p in data['v']],[],data['f']);me.update()
 for n in used:me.materials.append(material(n))
 uv=me.uv_layers.new(name='UVMap')
 for p,n,old_uv in zip(me.polygons,data['m'],data['uv']):
  p.material_index=used.index(n)
  for j,li in enumerate(p.loop_indices):
   if old_uv is not None:uv.data[li].uv=old_uv[j]
   else:
    # Project each new box face on its two varying local axes. Reveals and
    # horizontal sills must not collapse to a one-dimensional wall projection.
    pts=[data['v'][i] for i in data['f'][p.index]]
    ext=[max(q[k] for q in pts)-min(q[k] for q in pts) for k in range(3)]
    axes=sorted(range(3),key=lambda k:ext[k],reverse=True)[:2];axes.sort()
    q=data['v'][me.loops[li].vertex_index];uv.data[li].uv=(q[axes[0]]/2,q[axes[1]]/2)
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);objects.append(ob)
 if bevel:
  bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Small edge radius','BEVEL');mod.width=.003;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 records.append({'name':name,'role':role,'materials':used,'faces':len(ob.data.polygons)})
 return ob
# Replace only each known west-wall box. Preserve every other source face and UV.
patches=[]
for rel,name,role,expected in [
 ('SourceAssets/Walkthrough/ATS_Walkthrough.blend','SM_Walk_HistoricWestWing_ShanghaiRender','Shell',[[-.03,.23],[0,30.4],[0,12.8]]),
 ('SourceAssets/Dining/FullGroundFloor_20261108/ATS_Dining_Built.blend','SM_DiningBuilt_Walls','Walls',[[.23,.24],[3.67,30.4],[0,3.96]])]:
 vs,rows=read_source(rel,name)
 for axis in range(3):assert abs(min(v[axis] for v in vs[:8])-expected[axis][0])<.002 and abs(max(v[axis] for v in vs[:8])-expected[axis][1])<.002,(name,axis)
 data=dataset();kept=0
 for row in rows:
  if any(i<8 for i in row['verts']):continue
  pts=[vs[i] for i in row['verts']];add(data,pts,[tuple(range(len(pts)))],row['material'],[row['uv']]);kept+=1
 mat=rows[0]['material'];rect_cut(data,sum(expected[0])/2,expected[0][1]-expected[0][0],*expected[1],*expected[2],mat)
 output_mesh('SM_DiningCross_'+role,data,role)
 patches.append({'role':role,'original_faces':len(rows),'untouched_original_faces':kept,'original_wall_faces_replaced':len(rows)-kept,'preserved_uvs':True,'apertures_campus_v_h':openings})
# Cut the CURRENT mosaic-panel revision and cap, preserving all other finishes.
vs,rows=read_source('SourceAssets/Dining/StructuralSurfaces_20261108/ATS_Dining_HallSurfaces.blend','SM_Dining_HallSurfacePanels')
data=dataset();removed={'mosaic':0,'cap':0};kept=0
for row in rows:
 pts=[vs[i] for i in row['verts']];mat=row['material']
 is_west=all(.242<q[0]<.266 and 3.76<q[1]<30.31 for q in pts)
 if is_west and mat=='M_Dining_Hall_BasketMosaic':removed['mosaic']+=1;continue
 if is_west and mat=='M_Dining_Hall_CharcoalCap':removed['cap']+=1;continue
 add(data,pts,[tuple(range(len(pts)))],mat,[row['uv']]);kept+=1
assert removed=={'mosaic':6,'cap':6},removed
rect_cut(data,.254,.002,3.77,30.3,.15,1.8,'M_Dining_Hall_BasketMosaic')
rect_cut(data,.252,.018,3.77,30.3,1.8,1.85,'M_Dining_Hall_CharcoalCap')
output_mesh('SM_DiningCross_Tiles',data,'Tiles')
patches.append({'role':'Tiles','original_faces':len(rows),'untouched_original_faces':kept,'replaced_faces':removed,'skirting_preserved':True})
# The two visible window bays only; no repeated whole-wall window rhythm inferred.
frames=dataset();glass=dataset();ac=dataset();cross=dataset()
frame='M_DiningBuild_Frame';glazing='M_DiningBuild_Glass';paint='M_Dining_OffWhitePaint_Matte';black='M_DiningBuild_Black';wood='M_DiningCross_DarkWood'
for vc in centres:
 va,vb=vc-width/2,vc+width/2
 for vv in [va,vb]:box(frames,(.205,vv,(bottom+top)/2),(.13,.065,top-bottom+.065),frame)
 for zz in [bottom,top]:box(frames,(.205,vc,zz),(.13,width+.065,.065),frame)
 box(frames,(.205,vc,(bottom+top)/2),(.11,.045,top-bottom),frame)
 levels=[bottom,bottom+2.25*.43,bottom+2.25*.70,top]
 for zz in levels[1:-1]:box(frames,(.205,vc,zz),(.11,width,.045),frame)
 # Shallow sill only, rather than inventing a canopy or ornamental surround.
 box(frames,(.12,vc,bottom-.025),(.4,width+.13,.055),frame)
 for ci in range(2):
  for ri in range(3):
   vlo=va+ci*width/2;vhi=vlo+width/2;lo,hi=levels[ri:ri+2]
   if ci==0 and ri==2:continue
   box(glass,(.197,(vlo+vhi)/2,(lo+hi)/2),(.008,vhi-vlo-.04,hi-lo-.04),glazing)
 # The upper-left compartment contains a window air conditioner in both photos.
 acv=va+width/4;acz=(levels[2]+top)/2
 box(ac,(.12,acv,acz),(.42,.65,.58),paint)
 box(ac,(.336,acv-.025,acz+.035),(.018,.56,.30),black)
 for i in range(8):box(ac,(.349,acv-.025,acz-.095+i*.037),(.025,.55,.012),frame)
 box(ac,(.34,acv,acz-.22),(.02,.60,.08),paint)
 # Seal the perimeter with glazing behind the overlapping opaque AC casing.
 box(glass,(.197,acv,acz),(.008,width/2-.04,levels[3]-levels[2]-.04),glazing)
for p,sz in [((.278,cross_v,cross_h),(.045,.046,.60)),((.278,cross_v,cross_h+.15),(.045,.35,.046))]:box(cross,p,sz,wood)
for name,d,role,bevel in [('Frames',frames,'Frames',True),('Glass',glass,'Glass',False),('Aircon',ac,'Aircon',True),('Cross',cross,'Cross',True)]:output_mesh('SM_DiningCross_'+name,d,role,bevel)
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'ATS_Dining_CrossWindows.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_CrossWindows.blend'))
for row in source_hashes:row['after']=hashlib.sha256(pathlib.Path(row['path']).read_bytes()).hexdigest();assert row['before']==row['after']
manifest={'window_count':2,'window_centres_campus_m':[[.205,v,(bottom+top)/2] for v in centres],'window_openings_v_h':openings,'window_width_m':width,'window_height_m':top-bottom,'row_height_ratios_bottom_to_top':[.43,.27,.30],'cross_campus_m':[.278,cross_v,cross_h],'cross_dimensions_m':[.045,.35,.6],'photo_based':['Two tall window bays bracketing the cross','Two columns and three main glazing levels per bay','Upper-left window air conditioners','Dark cross biased toward the left window','Cross is above the dark dado border'],'user_confirmed':['This is the main dining hall','The west blank wall is the cross-window wall','The centre of the archived user view identifies the cross location'],'interpretation_disclosed':'The user view establishes the horizontal position. Its raw ray height is below the dado, conflicting with the photograph. Hanging height follows the photographed above-dado relationship and is explicitly an estimate, not a confirmed measured 3D point.','numeric_dimensions_and_spacing_are_photo_estimates':True,'raw_user_view_ray_h':anchor['raw_view_centre_h'],'meshes':records,'patches':patches,'source_integrity':source_hashes,'not_changed':['Other exterior faces and upper floors','Courtyard shutter opening and rear shutter openings','Dining ceiling and unregistered beam grid','Existing exterior retaining/boundary proxy behind this wall']}
(out/'construction_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('CROSS_WINDOWS_BUILT',len(records),'SOURCE_HASHES_UNCHANGED',len(source_hashes))
