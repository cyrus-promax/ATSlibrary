import bpy,math,json,pathlib
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/FullGroundFloor_20261108/RearShutterApertures';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(p):u,v,h=p;return(-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
vs=[];fs=[];boxes=[]
def box(u0,u1,v0,v1,h0,h1):
 base=len(vs);vs.extend([site(p) for p in [(u0,v0,h0),(u1,v0,h0),(u1,v1,h0),(u0,v1,h0),(u0,v0,h1),(u1,v0,h1),(u1,v1,h1),(u0,v1,h1)]]);fs.extend([tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);boxes.append([u0,u1,v0,v1,h0,h1])
opening_u=[(2.675,4.875),(10.705,12.905)]
cursor=.2
for a,b in opening_u:
 box(cursor,a,30.45,37.35,0,12.5)
 box(a,b,30.45,37.35,2.8,12.5)
 box(a,b,32.1,37.35,0,2.8)
 cursor=b
box(cursor,53.8,30.45,37.35,0,12.5)
mesh=bpy.data.meshes.new('RearBoundaryThresholdClearance');mesh.from_pydata(vs,[],fs);mesh.update();obj=bpy.data.objects.new('SM_Dining_RearBoundaryClearance',mesh);bpy.context.collection.objects.link(obj);obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.export_scene.fbx(filepath=str(out/'ATS_Dining_RearBoundaryClearance.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
report={'actor':'StaticMeshActor_148','original_bounds_campus':[.2,53.8,30.45,37.35,0,12.5],'clearance_pockets':[{'u':list(p),'v':[30.45,32.1],'h':[0,2.8]} for p in opening_u],'remaining_boxes':boxes,'purpose':'Only allow crossing each confirmed shutter threshold onto existing ground. Unconfirmed spaces beyond 32.1 and between the two thresholds remain inaccessible. No room walls, destinations or corridor beyond the restaurant are invented.'}
(out/'boundary_clearance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('BOUNDARY_THRESHOLD_CLEARANCE',len(boxes))
