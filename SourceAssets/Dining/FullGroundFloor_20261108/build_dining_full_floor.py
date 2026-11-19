import bpy,math,json,pathlib,random
from mathutils import Vector
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
out=root/'SourceAssets/Dining/FullGroundFloor_20261108';out.mkdir(parents=True,exist_ok=True)
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(p):u,v,h=p;return (-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
def local(p):x=p.x+8;y=p.y+24;return (c*x+s*y,-s*x+c*y,p.z+24.55)
u0,u1,v0,v1=.23,19.68,3.67,30.4
ceil=3.96;doorh=2.80;doorw=2.20
doors=[{'id':'RightUpper','center':[3.775,v1,0.02],'axis':'u','width':doorw,'height':doorh,'hinge':[3.775-doorw/2,v1,0.02],'yaw':-20,'open_angle':100},
       {'id':'RightLower','center':[11.805,v1,0.02],'axis':'u','width':doorw,'height':doorh,'hinge':[11.805-doorw/2,v1,0.02],'yaw':-20,'open_angle':100},
       {'id':'CourtyardSide','center':[19.8,13.64613555,0.02],'axis':'v','width':doorw,'height':doorh,'hinge':[19.8,13.64613555-doorw/2,0.02],'yaw':-110,'open_angle':-100}]
dv0,dv1=doors[2]['center'][1]-doorw/2,doors[2]['center'][1]+doorw/2

# Rebuild the courtyard aperture for a wider roller shutter, preserving upper walls.
# Build in an isolated scene, leaving the original campus source unchanged.
bpy.ops.wm.open_mainfile(filepath=str(root/'SourceAssets/Walkthrough/ATS_Walkthrough.blend'))
patched=[];patch_info=[]
facebox=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def append_box(vs,fs,center,size):
    base=len(vs);x,y,z=center;dx,dy,dz=[t/2 for t in size]
    vs.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
    fs.extend([tuple(base+i for i in f) for f in facebox])
for name,start,expected,newboxes in [
 ('SM_Walk_HistoricWestWing_FacadeWhite',0,[[19.68,19.92],[3.6,30.4],[0,12.8]],[
  ((19.8,(3.6+dv0)/2,6.4),(.24,dv0-3.6,12.8)),((19.8,(dv1+30.4)/2,6.4),(.24,30.4-dv1,12.8)),((19.8,(dv0+dv1)/2,(doorh+12.8)/2),(.24,doorw,12.8-doorh))])]:
    old=bpy.data.objects[name];points=[local(old.matrix_world@v.co) for v in old.data.vertices]
    block=points[start:start+8]
    for axis in range(3):assert abs(min(v[axis] for v in block)-expected[axis][0])<.002 and abs(max(v[axis] for v in block)-expected[axis][1])<.002
    keep=[i for i in range(len(points)) if not start<=i<start+8];remap={i:j for j,i in enumerate(keep)}
    vs=[points[i] for i in keep];fs=[tuple(remap[i] for i in f.vertices) for f in old.data.polygons if not any(start<=i<start+8 for i in f.vertices)]
    preserved=len(fs)
    for center,size in newboxes:append_box(vs,fs,center,size)
    mesh=bpy.data.meshes.new(name+'_DiningCut');mesh.from_pydata([site(p) for p in vs],[],fs);mesh.materials.append(old.data.materials[0]);mesh.update()
    obj=bpy.data.objects.new('SM_DiningPatch_'+('OldWall' if start==0 else 'OpenAirRoof'),mesh);bpy.context.collection.objects.link(obj);patched.append(obj)
    patch_info.append({'source_object':name,'new_object':obj.name,'original_faces':len(old.data.polygons),'unaltered_original_faces':preserved,'removed_original_faces':len(old.data.polygons)-preserved,'replacement_boxes':len(newboxes)})
for o in list(bpy.data.objects):
    if o not in patched:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

specs={'Paint':([.74,.75,.70],.86,0),'Ceiling':([.82,.82,.77],.9,0),'PinkTile':([.62,.48,.45],.28,0),'CreamTile':([.64,.62,.53],.3,0),'Grout':([.36,.36,.32],.9,0),'DarkBorder':([.045,.075,.062],.28,0),'Frame':([.57,.60,.57],.34,.55),'Glass':([.10,.18,.16],.12,.20),'Steel':([.54,.57,.56],.25,1),'WoodPaint':([.24,.10,.034],.45,0),'Black':([.014,.018,.019],.65,0),'Terrazzo':([.59,.60,.53],.52,0),'Concrete':([.42,.43,.39],.85,0),'Lamp':([.95,.95,.89],.3,0),'KioskAccent':([.22,.40,.32],.48,0)}
for base in ['PinkTile','CreamTile']:
    col,r,m=specs[base]
    for i,f in enumerate([.94,.98,1.03]):specs[base+str(i)]=([v*f for v in col],r,m)
mats={}
for n,(col,r,m) in specs.items():
    mat=bpy.data.materials.new('M_DiningBuild_'+n);mat.diffuse_color=(*col,1);mats[n]=mat
groups={}
def geom(group,mat,vs,fs):
    data=groups.setdefault(group,{'v':[],'f':[],'m':[]});start=len(data['v']);data['v'].extend(vs);data['f'].extend([tuple(start+i for i in f) for f in fs]);data['m'].extend([mat]*len(fs))
def box(group,mat,p,sz):
    vs=[];fs=[];append_box(vs,fs,p,sz);geom(group,mat,vs,fs)
def rod(group,mat,a,b,r=.015,segments=16):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();e=d.cross(Vector((0,0,1)))
    if e.length<.01:e=d.cross(Vector((0,1,0)))
    e.normalize();f=d.cross(e);vs=[]
    for p in [a,b]:
        for i in range(segments):vs.append(tuple(p+r*(math.cos(i*math.tau/segments)*e+math.sin(i*math.tau/segments)*f)))
    fs=[tuple(range(segments-1,-1,-1)),tuple(range(segments,2*segments))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    geom(group,mat,vs,fs)
def wall_piece(axis,fixed,a,b,z0,z1,thickness=.18,mat='Paint',group='Walls'):
    if b<=a or z1<=z0:return
    p=[fixed,(a+b)/2,(z0+z1)/2] if axis=='u' else [(a+b)/2,fixed,(z0+z1)/2]
    sz=[thickness,b-a,z1-z0] if axis=='u' else [b-a,thickness,z1-z0];box(group,mat,p,sz)
def wall_openings(axis,fixed,a,b,openings,thickness=.18):
    cursor=a
    for low,high,bot,top in sorted(openings):
        wall_piece(axis,fixed,cursor,low,0,ceil,thickness);wall_piece(axis,fixed,low,high,0,bot,thickness);wall_piece(axis,fixed,low,high,top,ceil,thickness);cursor=high
    wall_piece(axis,fixed,cursor,b,0,ceil,thickness)

# The user confirms the restaurant occupies this wing's entire G-floor interior.
wall_piece('u',u0+.005,v0,v1,0,ceil,.01)
right_openings=[(d['center'][0]-doorw/2,d['center'][0]+doorw/2,0,doorh) for d in doors[:2]]
# Preserve the existing rear-wing window openings instead of painting over them.
right_openings += [(max(u0,a),min(u1,b),1.03,3.23) for a,b in [(.2,3.8),(4.2,7.8),(8.2,11.8),(12.2,15.8),(16.2,19.8)]]
right_x=sorted(set([u0,u1]+[x for o in right_openings for x in o[:2]]))
right_z=sorted(set([0,ceil]+[z for o in right_openings for z in o[2:]]))
for a,b in zip(right_x,right_x[1:]):
    for za,zb in zip(right_z,right_z[1:]):
        if not any(lo<(a+b)/2<hi and bottom<(za+zb)/2<top for lo,hi,bottom,top in right_openings):wall_piece('v',v1,a,b,za,zb)
windows=[(u-1.25,u+1.25,1.0,3.0) for u in [5.5,8.7,11.9,15.1,18.3]]
# Recess this backing within the existing window wall to avoid coplanar surfaces.
# The first ~4 m of blank wall is provisional closure of a shell gap, not a new guessed window.
wall_openings('v',3.55,u0,u1,windows,thickness=.20)
box('Floor','Terrazzo',((u0+u1)/2,(v0+v1)/2,.006),(u1-u0,v1-v0,.028))
box('OutdoorFloor','Concrete',((4+19.68)/2,(.2+3.43)/2,.004),(19.68-4,3.43-.2,.024))
box('Ceiling','Ceiling',((u0+u1)/2,(v0+v1)/2,ceil+.10),(u1-u0+.18,v1-v0+.18,.20))

# Photo-supported mosaic appearance with real tile edges, not a blurry enlargement.
rand=random.Random(71)
def tilewall(axis,fixed,a,b,inside_sign,base,openings):
    def blocked(x,z):return any(lo-.012<x<hi+.012 and bottom-.012<z<top+.012 for lo,hi,bottom,top in openings)
    # The concrete wall supplies collision; finishes stay nonblocking.
    pitch=.05
    for i in range(math.ceil((b-a)/pitch)):
        x=a+(i+.5)*pitch
        if x>b-.009:continue
        for j in range(33):
            z=.15+(j+.5)*pitch
            if blocked(x,z):continue
            mat=base+str(rand.randrange(3))
            p=[fixed+inside_sign*.006,x,z] if axis=='u' else [x,fixed+inside_sign*.006,z]
            sz=[.010,.047,.047] if axis=='u' else [.047,.010,.047]
            box('Tiles',mat,p,sz)
    for za,zb in [(.02,.13),(1.80,1.85)]:
        intervals=[];cursor=a
        for lo,hi,bot,top in sorted(openings):
            if bot<zb and top>za:intervals.append((cursor,lo));cursor=hi
        intervals.append((cursor,b))
        for lo,hi in intervals:wall_piece(axis,fixed+inside_sign*.009,lo,hi,za,zb,.018,'DarkBorder','Tiles')
tilewall('v',v1-.091,u0+.10,u1-.01,-1,'PinkTile',right_openings)
tilewall('u',u1-.004,v0+.1,v1-.10,-1,'CreamTile',[(dv0,dv1,0,doorh)])
tilewall('v',v0+.004,u0+.10,u1-.01,1,'CreamTile',windows)
tilewall('u',u0+.013,v0+.1,v1-.1,1,'CreamTile',[])

# Five window bays already belong to the G-floor exterior shell.
# Do not introduce duplicate frames or glass inside the enlarged room.
for d in doors:
    u,v,_=d['center']
    if d['axis']=='u':
        for x in [u-doorw/2-.04,u+doorw/2+.04]:box('DoorFrames','Frame',(x,v,doorh/2),(.08,.22,doorh))
        box('DoorFrames','Frame',(u,v,doorh+.23),(doorw+.22,.48,.46))
        box('DoorFrames','DarkBorder',(u,v-.245,doorh+.02),(doorw+.06,.018,.035))
    else:
        for x in [v-doorw/2-.04,v+doorw/2+.04]:box('DoorFrames','Frame',(u,x,doorh/2),(.22,.08,doorh))
        box('DoorFrames','Frame',(u,v,doorh+.23),(.48,doorw+.22,.46))
        box('DoorFrames','DarkBorder',(u-.245,v,doorh+.02),(.018,doorw+.06,.035))
    box('Thresholds','Terrazzo',(u,v,.014),(.4,doorw,.028) if d['axis']=='v' else (doorw,.4,.028))

# User confirmed a tuck shop with a serving window, without a conjectural kitchen.
ku,kv=13.4,9.6
# Larger tuck-shop enclosure, with its frontage normal +v toward the user's saved camera.
wall_openings('u',ku,v0,kv,[])
window_a,window_b=ku+.48,u1-.48
wall_openings('v',kv,ku,u1,[(window_a,window_b,1.03,2.42)])
box('Kiosk','Steel',((ku+u1)/2,kv+.12,1.04),(u1-ku-.60,.44,.065))
for uu in [window_a,window_b]:box('Kiosk','Frame',(uu,kv+.045,1.73),(.06,.12,1.43))
box('Kiosk','Frame',((ku+u1)/2,kv+.045,2.42),(window_b-window_a,.12,.06))
box('Kiosk','KioskAccent',((ku+u1)/2,kv+.10,2.94),(u1-ku-.42,.04,.58))
font=bpy.data.fonts.load('C:/Windows/Fonts/msjh.ttc')
cu=bpy.data.curves.new('VitaShopName','FONT');cu.body='維他天地';cu.font=font;cu.size=.40;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.002
ob=bpy.data.objects.new('VitaShopName',cu);bpy.context.collection.objects.link(ob);ob.location=((ku+u1)/2,kv+.13,2.94);ob.rotation_euler=(math.pi/2,0,math.pi);ob.data.materials.append(mats['Ceiling'])
bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH')
temp=bpy.context.object;geom('Sign','Ceiling',[tuple(temp.matrix_world@v.co) for v in temp.data.vertices],[tuple(f.vertices) for f in temp.data.polygons]);bpy.data.objects.remove(temp,do_unlink=True)

# Fixed equipment follows the drawn positions. Exact product models are unspecified.
sv0,sv1=25.15,27.97;front,back=18.97,19.57
box('Washbasin','Steel',((front+back)/2,(sv0+sv1)/2,.73),(back-front,sv1-sv0,.045))
for u in [front,back]:box('Washbasin','Steel',(u,(sv0+sv1)/2,.835),(.035,sv1-sv0,.22))
for v in [sv0,sv1]:box('Washbasin','Steel',((front+back)/2,v,.835),(back-front,.035,.22))
for u in [front+.05,back-.05]:
    for v in [sv0+.08,sv1-.08]:box('Washbasin','Steel',(u,v,.38),(.045,.045,.72))
for v in [25.61,26.56,27.51]:
    rod('Washbasin','Steel',(19.50,v,.94),(19.50,v,1.16),.022)
    rod('Washbasin','Steel',(19.50,v,1.16),(19.26,v,1.16),.022)
    rod('Washbasin','Steel',(19.26,v,1.16),(19.26,v,1.10),.022)
    rod('Washbasin','Black',(19.25,v,.752),(19.25,v,.757),.035,24)
fu,fv=19.19,29.69
box('Fountain','Steel',(fu,fv,.49),(.57,.57,.92))
box('Fountain','Black',(fu,fv,.055),(.52,.52,.07))
profiles=[(.24,1.02),(.23,1.03),(.205,1.00),(.17,.96),(.11,.93),(.035,.92)]
verts=[];faces=[];n=40
for r,h in profiles:
    for i in range(n):verts.append((fu+math.cos(i*math.tau/n)*r,fv+math.sin(i*math.tau/n)*r,h))
for j in range(len(profiles)-1):
    for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
geom('Fountain','Steel',verts,faces);rod('Fountain','Black',(fu,fv,.915),(fu,fv,.92),.035,24)
rod('Fountain','Steel',(fu+.18,fv,1.01),(fu+.18,fv,1.13),.025);rod('Fountain','Steel',(fu+.18,fv,1.13),(fu+.10,fv,1.15),.025)

lights=[]
for u in [3.0,7.6,12.2,16.8]:
    for v in [6.4,11.4,16.4,21.4,26.4]:
        box('Lighting','Frame',(u,v,3.91),(.17,1.20,.08));box('Lighting','Lamp',(u,v,3.863),(.125,1.13,.016));lights.append({'campus_m':[u,v,3.79],'lumens':6000,'width_cm':16,'height_cm':118})
# Small light inside the shop; no invented stock, shelving or kitchen fittings.
lights.append({'campus_m':[14.9,(v0+kv)/2,3.79],'lumens':2200,'width_cm':16,'height_cm':80})

mesh_items=[]
for group,d in groups.items():
    used=list(dict.fromkeys(d['m']));me=bpy.data.meshes.new('Dining_'+group);me.from_pydata([site(p) for p in d['v']],[],d['f']);me.update()
    for n in used:me.materials.append(mats[n])
    for p,matname in zip(me.polygons,d['m']):p.material_index=used.index(matname)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        normal=p.normal
        axis=max(range(3),key=lambda i:abs(normal[i]))
        for li in p.loop_indices:
            original=d['v'][me.loops[li].vertex_index]
            uv.data[li].uv=(original[1],original[2]) if axis==0 else ((original[0],original[2]) if axis==1 else (original[0],original[1]))
    ob=bpy.data.objects.new('SM_DiningBuilt_'+group,me);bpy.context.collection.objects.link(ob)
    if group in ['Washbasin','Fountain','Kiosk','DoorFrames','WindowFrames']:
        bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Manufactured edge radius','BEVEL');mod.width=.004;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh_items.append({'name':ob.name,'group':group,'collision':group not in ['Tiles','Sign','Lighting'],'materials':['M_DiningBuild_'+m for m in used]})

def export(objects,file):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(out/file),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
export(list(bpy.data.objects),'ATS_Dining_Built.fbx')
# One profile for instanced shutter slats: 100 x 2.8 x 7.5 cm, centred at origin.
# Runtime translates slats upward individually into the hood; it does not squash their spacing.
profile=[(-.014,-.0375),(-.014,-.028),(-.006,-.024),(-.004,.022),(-.014,.028),(-.014,.0375),(.014,.0375),(.014,.028),(.006,.024),(.004,-.022),(.014,-.028),(.014,-.0375)]
vs=[(x,y,z) for x in [-.5,.5] for y,z in profile];n=len(profile)
fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('ShutterSlat');me.from_pydata(vs,[],fs);me.materials.append(mats['Frame']);me.update()
ob=bpy.data.objects.new('SM_Dining_ShutterSlat',me);bpy.context.collection.objects.link(ob)
export([ob],'SM_Dining_ShutterSlat.fbx')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_Built.blend'))
result={'scope':'Physical G-floor restaurant constructed from the user-confirmed plan, occupying the entire west-wing ground floor, a larger user-facing tuck shop, washbasin, drinking fountain and three automatic roller shutters.',
 'room_campus_bounds':[u0,u1,v0,v1],'ceiling_underside_m':ceil,'height_basis':'Fitted to existing 4.2 m G/1F model storey; not a site measurement.',
 'door_width_m':doorw,'door_height_m':doorh,'doors':doors,'lights':lights,'meshes':mesh_items,'patches':patch_info,
 'materials':{k:{'colour_linear':a,'roughness':b,'metallic':d} for k,(a,b,d) in specs.items()},
 'full_G_floor':{'previous_bounds':[.23,19.68,3.67,19.15909631],'new_model_area_m2':(u1-u0)*(v1-v0),'basis':'User confirms the restaurant occupies the entire G floor of HistoricWestWing. Interior fitted to existing outer shell u=.23..19.68,v=3.67..30.4, excluding the existing open veranda. Not a measured survey.','old_internal_boundary_v_removed':19.15909631,'kiosk_bounds':[ku,u1,v0,kv],'kiosk_front_normal_campus':[0,1,0],'user_camera_campus':[16.245872397,24.443050813,3.835660076],'shutter_type':'User-confirmed vertically rolling restaurant shutters; exact finish, width and height remain model estimates.','no_new_seat_count_or_column_grid_invented':True},
 'user_confirmed':['The two unlabelled rectangles are the two courtyards','Build real geometry following the plan, not location markers','Vita area is a tuck shop with a serving window','Restaurant occupies this whole building G floor','Vita shop is larger and faces the user camera','Restaurant doors are roller shutters'],
 'photo_based_appearance':['Pale pink / cream small mosaic tile, dark borders, white upper wall','White ceiling and linear light fittings','Grey metal window frames','Roller-shutter door type confirmed by user; finish not yet identifiable in school photographs'],
 'implementation_estimates':['Full-floor extent confirmed by user; absolute dimensions still estimated from existing west-wing shell','Shutter widths and heights, larger shop window size, ceiling height','Five windows reused from existing facade; light count/spacing are provisional implementation values','Generic stainless washbasin and drinking-fountain geometry; exact product model unknown'],
 'not_added':['Unconfirmed table and chair arrangement','Unconfirmed rooms beyond the three doors','Kitchen equipment or stock inside the tuck shop','Unverified full column/beam grid']}
(out/'construction_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_PHYSICAL_GEOMETRY',len(mesh_items),'PATCHES',len(patched))
