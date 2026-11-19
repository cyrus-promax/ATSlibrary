import bpy
import pathlib
import math
import json
from mathutils import Vector

root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
out=root/'SourceAssets/Dining/Envelope'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.0
specs={
    'CeilingPaint':([.72,.72,.68],.85,0),
    'WallPaint':([.70,.70,.66],.82,0),
    'GreyGlazedTile':([.30,.31,.30],.27,0),
    'GreyGlazedTileLight':([.315,.325,.315],.28,0),
    'GreyGlazedTileDark':([.29,.30,.29],.29,0),
    'Grout':([.225,.23,.22],.91,0),
    'FixtureWhite':([.71,.72,.70],.40,.05),
    'FanIvory':([.68,.68,.63],.47,.05),
    'LampDiffuser':([.88,.89,.85],.42,0),
}
materials={}
for name,(colour,rough,metal) in specs.items():
    m=bpy.data.materials.new('M_DiningEnvelope_'+name);m.diffuse_color=(*colour,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if name=='LampDiffuser':p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=3
    materials[name]=m
groups={}
def finish(o,group,mat,bevel=0):
    o.data.materials.append(materials[mat]);bpy.context.view_layer.objects.active=o
    if bevel:
        mod=o.modifiers.new('Edge radius','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=True
    mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    groups.setdefault(group,[]).append(o)
    return o
def box(group,mat,pos,size,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,group,mat,bevel)
def cylinder(group,mat,pos,radius,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=pos)
    return finish(bpy.context.object,group,mat,.002)

# A deliberately bounded finish study above the user-confirmed dining area.
# Its open edges are MODEL COVERAGE LIMITS, not claims about the real room edges.
# The eastern finish follows an existing shell surface; no new room boundaries,
# openings, kitchen partitions or access routes are introduced.
u0,u1=7.2,19.655
v0,v1=10.4,22.0
underside=3.96  # follows existing model's 4.2 m G/1F level and 0.24 m slab
box('Ceiling','CeilingPaint',((u0+u1)/2,(v0+v1)/2,underside+.06),(u1-u0,v1-v0,.12),.004)
for v in [v0+.12,16.2,v1-.12]:
    box('Ceiling','CeilingPaint',((u0+u1)/2,v,3.795),(u1-u0,.24,.33),.006)

# Only the finish is added to this existing wall. Rectangular grey reflective
# cladding is visible in both the 2023 anniversary and latest school leaflet.
wall_front=19.645
tile_height=1.80
box('WallFinish','Grout',(wall_front+.008,(v0+v1)/2,tile_height/2),(.014,v1-v0,tile_height),0)
tile_width=.60
for row in range(6):
    start=v0
    col=0
    while start<v1-.001:
        end=min(start+tile_width,v1)
        mat=['GreyGlazedTile','GreyGlazedTile','GreyGlazedTileLight','GreyGlazedTile','GreyGlazedTileDark'][(row*7+col*3)%5]
        box('WallFinish',mat,(wall_front-.003,(start+end)/2,.15+row*.30),(.015,end-start-.002,.298),.0007)
        start=end;col+=1
box('WallPaint','WallPaint',(19.653,(v0+v1)/2,(tile_height+underside)/2),(.016,v1-v0,underside-tile_height),.001)

lights=[]
for v in [13.3,19.1]:
    for u in [9.70,16.85]:
        box('Lights','FixtureWhite',(u,v,3.897),(.145,1.225,.080),.009)
        box('Lights','LampDiffuser',(u,v,3.850),(.108,1.175,.015),.005)
        lights.append({'campus_m':[u,v,3.81],'lumens':4000,'width_cm':12,'height_cm':118,'temperature_k':4500})

# Two repetitions of the clearly visible centreline white three-blade fan.
# Their absolute spacing is a model fit, not an independently measured plan.
for u,v in [(13.27,13.3),(13.27,19.1)]:
    cylinder('Fans','FanIvory',(u,v,3.915),.095,.09)
    cylinder('Fans','FixtureWhite',(u,v,3.665),.012,.44)
    cylinder('Fans','FanIvory',(u,v,3.415),.115,.10)
    cylinder('Fans','FanIvory',(u,v,3.351),.075,.035)
    for i in range(3):
        a=i*math.tau/3+.20
        o=box('Fans','FanIvory',(u+math.cos(a)*.36,v+math.sin(a)*.36,3.420),(.62,.115,.009),.005)
        o.rotation_euler.z=a

c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
items=[]
for group,parts in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object
    o.name='SM_DiningEnvelope_'+group
    bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    for vertex in o.data.vertices:
        u,v,h=vertex.co
        vertex.co=(-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
    # Stable deduplicated material slots.
    old=list(o.data.materials);unique=list(dict.fromkeys(old));indices=[unique.index(old[p.material_index]) for p in o.data.polygons]
    o.data.materials.clear()
    for mat in unique:o.data.materials.append(mat)
    for polygon,index in zip(o.data.polygons,indices):polygon.material_index=index
    items.append({'name':o.name,'group':group,'collision':group in ['Ceiling','WallFinish','WallPaint'],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]})

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(out/'ATS_Dining_Envelope.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_Envelope.blend'))
report={
    'scope':'Partial finish reconstruction in the user-confirmed dining area; no complete room plan is asserted.',
    'appearance_sources':[
        {'url':'http://www.ats.edu.hk/images/doc/20261102.pdf','pdf_page':2,'image':'leaflet_p02_image02.png','features':['grey reflective rectangular wall finish','white ceiling and cross beams','linear light fittings','white ceiling fans']},
        {'url':'http://www.ats.edu.hk/images/doc/Dorm_10_Anniversary_Journal.pdf','pdf_page':30,'image':'anniversary_p30_image02.png','features':['same dining room with blue chairs and white tables','grey lower wall finish','plain white ceiling beams','centreline ceiling fans and flanking strip lights']},
    ],
    'coverage_campus_m':{'u':[u0,u1],'v':[v0,v1]},
    'coverage_edges_are_not_room_boundaries':True,
    'existing_wall_surface_campus_u':19.6799993,
    'ceiling_underside_m':underside,
    'height_basis':'Existing model G/1F floor height 4.2 m minus 0.24 m; NOT a measured dining ceiling height.',
    'minimum_new_headroom_m':3.3335,
    'finish_tile_pitch_m':[.60,.30],
    'new_partitions':0,'new_openings':0,'new_kitchen':False,
    'ceiling_fans':2,'light_fittings':4,
    'not_verified':['Exact dining room extent and orientation','Absolute location of the photographed wall in the campus','Exact ceiling, beam and wall-cladding dimensions','Exact light and fan spacing/count across the full room','Door and window positions','Kitchen and service-area layout'],
    'modelling_limits':'Dimensions are visual estimates fitted to the existing shell. Only a bounded section near the confirmed position is modelled. The rest of the room remains incomplete; do not interpret the coverage edges as real construction joints.',
    'materials':{name:{'colour_linear':col,'roughness':rough,'metallic':metal,'emissive_strength':3 if name=='LampDiffuser' else 0} for name,(col,rough,metal) in specs.items()},
    'meshes':items,'lights':lights,
}
(out/'dining_envelope_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_ENVELOPE_GEOMETRY_READY',[(x['name'],x['faces']) for x in items])
