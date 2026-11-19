from pathlib import Path
import json
root=Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108')
arch=json.loads((root/'architecture_manifest.json').read_text(encoding='utf-8'))
meshes={m['name']:m for m in arch['meshes']}
doors=[]
def add(module,label,leaf_index,hinge,direction,angle):
 stem=f'SM_LW_A_{module}_{label}_Leaf_{leaf_index}'
 wood=stem+'_PaleOak'
 moving=[stem+'_Glass_Glass',stem+'_GlazingBead_WhiteMetal',stem+'_Handle_WhiteMetal',stem+'_Hinges_WhiteMetal']
 closer=stem+'_Closer_WhiteMetal'
 for n in [wood,*moving,closer]:assert n in meshes,n
 doors.append({'id':f'{module}_{label}_Leaf_{leaf_index}','module':module,'wood_mesh':wood,
               'moving_leaf_parts':moving,'hinge_m':hinge,'leaf_direction_vector':direction,
               'rotation_axis':'Blender +Z','suggested_open_angle_blender_degrees':angle,
               'suggested_open_angle_ue_degrees':-angle,
               'leave_static':[closer],
               'closer_note':'One combined closer body+arm mesh; keep static for initial proximity-door prototype. Detailed articulated closer awaits a separate rig.',
               'frame_meshes':[m for m in meshes if m.startswith(f'SM_LW_A_{module}_{label}_') and '_Leaf_' not in m],
               'mesh_coordinate_mode':'All vertices in global Blender metres; mesh object transform identity. Use negative hinge offset on mesh child when attaching to hinge pivot.',
               'location_accuracy':'Display-study dimensions, not surveyed.'})
add('Step','DoubleExit',1,[27.006,0,0],[1,0,0],90)
add('Step','DoubleExit',2,[28.394,0,0],[-1,0,0],-90)
add('Lecture','StageExit1',1,[8,16.186,0],[0,1,0],90)
add('Lecture','StageExit2',1,[8,20.786,0],[0,1,0],90)
(root/'door_assembly_manifest.json').write_text(json.dumps({'version':1,'doors':doors,'portal_note':'The Step endwall open connection is a doorframe-only study with no invented leaf. The two main-module cutaway ends are not doors.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'door_leaves':len(doors),'file':str(root/'door_assembly_manifest.json')},ensure_ascii=False))
