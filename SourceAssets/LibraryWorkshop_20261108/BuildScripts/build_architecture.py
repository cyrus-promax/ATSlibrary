"""Photo-based library architecture studies. Coordinates are display metres, NOT surveyed geometry."""
import bpy, math, json, pathlib, collections
from mathutils import Vector

OUT = pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108')
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'; bpy.context.scene.unit_settings.scale_length=1
palette={
 'LW_Plaster':((.84,.84,.80),.81,0),'LW_PaleOak':((.65,.49,.30),.5,0),
 'LW_FloorOak':((.51,.38,.23),.58,0),'LW_DarkOak':((.21,.105,.045),.48,0),
 'LW_BlackMetal':((.026,.035,.04),.28,.65),'LW_WhiteMetal':((.81,.82,.79),.34,.5),
 'LW_Glass':((.69,.82,.84),.06,0),'LW_Rubber':((.014,.016,.018),.8,0),
 'LW_Light':((.96,.94,.81),.3,0),'LW_Orange':((.56,.19,.045),.46,0),
 'LW_Wicker':((.45,.27,.11),.71,0),'LW_ExitGreen':((.02,.35,.23),.4,0),
 'LW_ScreenWhite':((.86,.86,.84),.73,0),
}
materials={}
for name,(col,r,m) in palette.items():
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*col,1);mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1)
 bs.inputs['Roughness'].default_value=r;bs.inputs['Metallic'].default_value=m
 if name=='LW_Light':bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=3
 if name=='LW_Glass':bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
 materials[name]=mat

groups={}; key=None
refs={'Main':['095817','101837','101839','101230'],'Step':['095910','102511','102535','102702'],
      'Lecture':['100004','100023','103010'],'Culture':['095825','100320','103316']}
def group(mod,part,mat,collision=False):
 global key
 key=(mod,part,mat,collision);groups.setdefault(key,[[],[]])
def mesh(vs,fs):
 v,f=groups[key];n=len(v);v.extend(vs);f.extend([tuple(n+i for i in face) for face in fs])
def box(c,d,rz=0):
 ca,sa=math.cos(rz),math.sin(rz)
 raw=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
 vs=[]
 for a,b,z in raw:
  x,y=a*d[0]/2,b*d[1]/2;vs.append((c[0]+x*ca-y*sa,c[1]+x*sa+y*ca,c[2]+z*d[2]/2))
 mesh(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def tube(points,r=.012,sides=12,cap=True):
 points=[Vector(p) for p in points];vs=[]
 for i,p in enumerate(points):
  direction=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
  helper=Vector((0,0,1)) if abs(direction.z)<.93 else Vector((1,0,0))
  u=direction.cross(helper).normalized();v=direction.cross(u).normalized()
  for j in range(sides):vs.append(tuple(p+r*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v)))
 fs=[]
 for i in range(len(points)-1):
  for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 if cap:fs.extend([tuple(range(sides-1,-1,-1)),tuple((len(points)-1)*sides+j for j in range(sides))])
 mesh(vs,fs)
def rod(a,b,r=.012,sides=12):tube([a,b],r,sides)
def ring(c,r,t=.018,sides=10,n=96):
 tube([(c[0]+r*math.cos(i*math.tau/n),c[1]+r*math.sin(i*math.tau/n),c[2]) for i in range(n+1)],t,sides,False)
def curve_pipe(points,r=.025):
 tube(points,r,12)
 # Couplers are separate geometry around visible straight end portions.
 for a,b in [(points[0],points[1]),(points[-1],points[-2])]:
  a,b=Vector(a),Vector(b);q=(b-a).normalized();rod(a+q*.06,a+q*.1,r*1.2,12)
def led_hanging(mod,x,y,style='X'):
 group(mod,'PendantSuspension','LW_BlackMetal')
 rod((x,y,3.77),(x,y,3.03),.0035,8)
 box((x,y,3.76),(.08,.08,.035))
 if style=='X':
  for z,mat,sz in [(3.04,'LW_Orange',(.98,.085,.055)),(3.005,'LW_Light',(.91,.064,.015))]:
   group(mod,'CrossPendantBody' if mat=='LW_Orange' else 'CrossPendantDiffuser',mat)
   for a in [math.pi/4,-math.pi/4]:box((x,y,z),sz,a)
 elif style=='Ring':
  group(mod,'RingPendantBody','LW_PaleOak');ring((x,y,3.07),.38,.055,14)
  group(mod,'RingPendantDiffuser','LW_Light');ring((x,y,3.025),.38,.025,12)
  group(mod,'PendantSuspension','LW_BlackMetal')
  for a in [0,2.094,4.188]:rod((x+math.cos(a)*.33,y+math.sin(a)*.33,3.1),(x,y,3.7),.0025,6)
def ceiling(mod,x0,y0,l,w,beams):
 group(mod,'CeilingSlab','LW_Plaster',True);box((x0+l/2,y0+w/2,3.9),(l,w,.2))
 group(mod,'ExposedBeams','LW_Plaster',True)
 for x in beams:box((x,y0+w/2,3.64),(.24,w,.32))
 # Longitudinal services remain separate, editable study components.
 group(mod,'ExposedWhiteServices','LW_WhiteMetal')
 for yy in [y0+.6,y0+1.02,y0+w-.65]:
  curve_pipe([(x0+.12,yy,3.6),(x0+.4,yy,3.6),(x0+.65,yy,3.42),(x0+l-.4,yy,3.42)],.022)
  for x in beams:box((x,yy,3.49),(.018,.085,.17))
 group(mod,'ConduitSupports','LW_WhiteMetal')
 for x in beams:
  for yy in [y0+.6,y0+w-.65]:
   rod((x,yy-.07,3.42),(x,yy+.07,3.42),.008)
   rod((x,yy,3.46),(x,yy,3.79),.006,8)
def floor(mod,x0,y0,l,w):
 group(mod,'Floor','LW_FloorOak',True);box((x0+l/2,y0+w/2,-.055),(l,w,.11))
def ac(mod,x,y,z=3.43):
 group(mod,'CeilingCassetteCasing','LW_WhiteMetal')
 box((x,y,z),(1.12,.96,.28));box((x,y,z-.16),(1.20,1.04,.045))
 # Three-dimensional intake perimeter and louvres, not a flat painted rectangle.
 group(mod,'CassetteIntakeRecess','LW_Rubber');box((x,y,z-.188),(.87,.71,.025))
 group(mod,'CassetteGrilleSlats','LW_WhiteMetal')
 for i in range(25):box((x-.405+i*.03375,y,z-.208),(.012,.67,.018))
 for side in [-1,1]:
  group(mod,'CassetteIntakeRecess','LW_Rubber');box((x,y+side*.457,z-.185),(.98,.07,.025))
  group(mod,'CassetteGrilleSlats','LW_WhiteMetal')
  for j in [-1,1]:box((x,y+side*.457+j*.018,z-.21),(.95,.009,.019))
 group(mod,'CassetteFixings','LW_WhiteMetal')
 for dx in [-.51,.51]:
  for dy in [-.43,.43]:rod((x+dx,y+dy,z-.2),(x+dx,y+dy,z-.214),.007,10)
 group(mod,'CassetteStatus','LW_ExitGreen');box((x+.48,y+.39,z-.208),(.018,.025,.005))
 # Short visible refrigerant/drain connection to services, grouped for optional removal.
 group(mod,'CassetteServicePipe','LW_WhiteMetal')
 curve_pipe([(x+.54,y,z+.04),(x+.71,y,z+.04),(x+.82,y,3.68),(x+.82,y+.5,3.68)],.025)

def window_y(mod,label,x0,y,w,z0=1.12,h=1.8,cols=4,inside=1):
 # For windows on constant y. z top hopper panes, central hinged panes, lower fixed panels.
 group(mod,label+'_Frame','LW_BlackMetal',True)
 for xx in [x0,x0+w]:box((xx,y,z0+h/2),(.065,.11,h+.065))
 levels=[z0,z0+.34,z0+h-.38,z0+h]
 for z in levels:box((x0+w/2,y,z),(w,.11,.055))
 for i in range(1,cols):box((x0+i*w/cols,y,z0+h/2),(.052,.1,h))
 for i in range(cols):
  xa=x0+i*w/cols;xb=x0+(i+1)*w/cols
  for j in range(3):
   za,zb=levels[j],levels[j+1]
   # Slim inner glazing gaskets make the frame readable at close range.
   group(mod,label+'_Gasket','LW_Rubber')
   for xx in [xa+.038,xb-.038]:box((xx,y+inside*.02,(za+zb)/2),(.012,.025,zb-za-.055))
   for zz in [za+.036,zb-.036]:box(((xa+xb)/2,y+inside*.02,zz),(xb-xa-.065,.025,.012))
   group(mod,label+'_Glass','LW_Glass');box(((xa+xb)/2,y,(za+zb)/2),(xb-xa-.085,.009,zb-za-.078))
  # Visible small opening latches with bracket base and spindle.
  group(mod,label+'_Hardware','LW_BlackMetal')
  hx=xb-.075;hy=y+inside*.075;hz=z0+.53
  box((hx,hy,hz),(.03,.022,.08));rod((hx,hy,hz),(hx,hy+inside*.025,hz),.009)
  rod((hx,hy+inside*.025,hz),(hx-.065,hy+inside*.025,hz),.008)
  group(mod,label+'_HopperLatches','LW_BlackMetal')
  rod(((xa+xb)/2,y+inside*.07,z0+h-.32),((xa+xb)/2,y+inside*.09,z0+h-.26),.007)
 group(mod,label+'_Sill','LW_Plaster',True);box((x0+w/2,y+inside*.01,z0-.065),(w+.08,.30,.07))
 # Rolled white blind and guide chain, observed above the black frames.
 group(mod,label+'_BlindRoller','LW_Plaster')
 rod((x0+.03,y+inside*.12,z0+h+.12),(x0+w-.03,y+inside*.12,z0+h+.12),.034,16)
 group(mod,label+'_BlindChain','LW_WhiteMetal')
 hx=x0+w-.05;hy=y+inside*.11
 tube([(hx-.012,hy,z0+h+.1),(hx-.012,hy,z0+h-.55),(hx+.012,hy,z0+h-.56),(hx+.012,hy,z0+h+.1)],.0024,6)

def wall_window_run(mod,x0,y,length,n,inside):
 bay=length/n
 group(mod,'WindowWallPanels','LW_Plaster',True)
 box((x0+length/2,y,.51),(length,.22,1.02));box((x0+length/2,y,3.40),(length,.22,.8))
 for j in range(n+1):box((x0+j*bay,y,1.9),(.27,.3,3.8))
 for j in range(n):window_y(mod,f'WindowBay_{"A" if inside==1 else "B"}_{j+1}',x0+j*bay+.16,y,bay-.32,inside=inside)
 group(mod,'Skirting','LW_Plaster',True);box((x0+length/2,y+inside*.13,.055),(length,.025,.11))

def transform_new_keys(prior,axis_swap,offset):
 # Helper for constructing a local constant-y window/door, then orienting it to x wall.
 for k,(vs,fs) in list(groups.items()):
  old=prior.get(k,0)
  for i in range(old,len(vs)):
   x,y,z=vs[i];vs[i]=(offset[0]+y,offset[1]+x,offset[2]+z) if axis_swap else (offset[0]+x,offset[1]+y,offset[2]+z)
  if axis_swap:
   for i in range(len(fs)):
    if all(j>=old for j in fs[i]):fs[i]=tuple(reversed(fs[i]))

def text_mesh(mod,part,body,loc,size,mat,rotation=(math.pi/2,0,0),font=None):
 curve=bpy.data.curves.new(part,'FONT');curve.body=body;curve.size=size;curve.align_x='CENTER';curve.extrude=.0007;curve.resolution_u=8
 if font:curve.font=font
 o=bpy.data.objects.new(part,curve);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH')
 group(mod,part,mat)
 mesh([tuple(o.matrix_world@v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]);bpy.data.objects.remove(o,do_unlink=True)

font=None
for path in ['C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjh.ttf','C:/Windows/Fonts/simhei.ttf']:
 if pathlib.Path(path).exists():
  try:font=bpy.data.fonts.load(path);break
  except:pass

def door_y(mod,label,xc,y,width=1.4,h=2.32,double=True,inside=1):
 group(mod,label+'_Frame','LW_PaleOak',True)
 for xx in [xc-width/2-.045,xc+width/2+.045]:box((xx,y,(h-.03)/2),(.085,.28,h-.03))
 box((xc,y,h+.015),(width+.17,.28,.09))
 group(mod,label+'_Stop','LW_PaleOak')
 for xx in [xc-width/2,xc+width/2]:box((xx,y+inside*.047,h/2),(.025,.035,h))
 group(mod,label+'_Seal','LW_Rubber')
 for xx in [xc-width/2+.008,xc+width/2-.008]:box((xx,y+inside*.03,h/2),(.008,.012,h-.03))
 leaves=2 if double else 1
 for i in range(leaves):
  ww=width/leaves-.012;cx=xc-width/2+(i+.5)*width/leaves
  part=label+f'_Leaf_{i+1}'
  gh=1.57;gw=.13;gz=1.21
  group(mod,part,'LW_PaleOak',True)
  for xx in [cx-(ww+gw)/4,cx+(ww+gw)/4]:box((xx,y,h/2),((ww-gw)/2,.045,h-.025))
  bh=gz-gh/2;th=h-(gz+gh/2)
  box((cx,y,bh/2),(gw,.045,bh));box((cx,y,gz+gh/2+th/2),(gw,.045,th))
  group(mod,part+'_Glass','LW_Glass');box((cx,y,gz),(gw-.018,.008,gh-.018))
  group(mod,part+'_GlazingBead','LW_WhiteMetal')
  for xx in [cx-gw/2,cx+gw/2]:box((xx,y+inside*.028,gz),(.012,.018,gh+.015))
  for zz in [gz-gh/2,gz+gh/2]:box((cx,y+inside*.028,zz),(gw+.015,.018,.012))
  group(mod,part+'_Handle','LW_WhiteMetal')
  hx=cx+((ww/2-.075) if i==0 else -(ww/2-.075));hy=y+inside*.045
  rod((hx,hy,1.02),(hx,hy+inside*.035,1.02),.015,16)
  rod((hx,hy+inside*.035,1.02),(hx+(-.11 if i==0 else .11),hy+inside*.035,1.02),.011,16)
  rod((hx,hy-.009*inside,.94),(hx,hy+.003*inside,.94),.017,16)
  group(mod,part+'_Hinges','LW_WhiteMetal')
  sx=cx+(-ww/2 if i==0 else ww/2)
  for zz in [.25,1.12,2.03]:
   box((sx,y+inside*.029,zz),(.032,.014,.1));rod((sx,y+inside*.043,zz-.05),(sx,y+inside*.043,zz+.05),.007,12)
  group(mod,part+'_Closer','LW_WhiteMetal')
  box((cx,y+inside*.05,h-.13),(.22,.055,.055))
  tube([(cx,y+inside*.08,h-.13),(cx+.15,y+inside*.18,h-.14),(cx+.22,y+inside*.05,h+.005)],.008,10)
 group(mod,label+'_ExitBox','LW_WhiteMetal');box((xc,y+inside*.08,h+.39),(.42,.08,.17))
 group(mod,label+'_ExitFace','LW_Light');box((xc,y+inside*.125,h+.39),(.389,.008,.142))
 # Face orientation follows the interior. Text is actual geometry, no low-res bitmap.
 text_mesh(mod,label+'_ExitLettering','EXIT 出口',(xc,y+inside*.132,h+.348),.082,'LW_ExitGreen',
           (math.pi/2,0,0) if inside==-1 else (math.pi/2,0,math.pi),font)

# MAIN READING STUDY: two observed long window walls, deliberately open ends.
floor('Main',0,0,14,8);ceiling('Main',0,0,14,8,[.2,3.5,7,10.5,13.8])
wall_window_run('Main',0,0,14,4,1);wall_window_run('Main',0,8,14,4,-1)
for x in [2.5,7,11.5]:
 ac('Main',x,2.3);ac('Main',x,5.7)
for x in [2,6,10]:
 for y in [2.1,5.9]:led_hanging('Main',x,y)
for lane in [2.9,5.1]:
 pts=[]
 for i in range(161):
  x=.65+12.7*i/160;z=3.2-.23*(1-math.cos((x-.65)/4.23*math.tau))/2
  pts.append((x,lane,z))
 group('Main','FlowingLEDHousing','LW_WhiteMetal');tube(pts,.024,8)
 group('Main','FlowingLEDDiffuser','LW_Light');tube([(x,y,z-.023) for x,y,z in pts],.014,8)
 group('Main','FlowingLEDSuspension','LW_BlackMetal')
 for x in [.65,4.88,9.11,13.35]:rod((x,lane,3.22),(x,lane,3.79),.0024,6)
group('Main','WallCross','LW_DarkOak')
box((8.8,7.83,3.36),(.037,.025,.30));box((8.8,7.83,3.42),(.17,.025,.035))

# STEP READING STUDY: one long window wall plus known adjacent end-door wall.
floor('Step',20,0,9,6);ceiling('Step',20,0,9,6,[20.2,24.5,28.8])
wall_window_run('Step',20,0,6.7,2,1)
group('Step','EndWall','LW_Plaster',True)
# A 1.2m doorway centred y2.1; no invented destination attached.
for ya,yb in [(0,1.5),(2.7,6)]:box((29,(ya+yb)/2,1.9),(.2,yb-ya,3.8))
box((29,2.1,3.06),(.2,1.2,1.48))
group('Step','EndDoorFrame','LW_WhiteMetal',True)
for yy in [1.5,2.7]:box((28.91,yy,1.16),(.12,.055,2.32))
box((28.91,2.1,2.32),(.12,1.25,.055))
group('Step','DoorWallAbove','LW_Plaster',True);box((27.85,0,3.08),(2.3,.22,1.44))
for xx,ww in [(26.85,.3),(28.7,.6)]:box((xx,0,1.18),(ww,.22,2.36))
door_y('Step','DoubleExit',27.7,0,1.4,inside=1)
for x,y in [(22,2),(25.4,1.7),(27.5,4)]:led_hanging('Step',x,y,'Ring')
ac('Step',23,3);ac('Step',27,3)

# LECTURE STUDY: window/stage wall and opposite tier-window wall; open lateral display access.
floor('Lecture',0,16,8,6);ceiling('Lecture',0,16,8,6,[.15,4,7.85])
group('Lecture','StageWallSegments','LW_Plaster',True)
for ya,yb in [(16,16.13),(17.27,17.55),(20.45,20.73),(21.87,22)]:box((8,(ya+yb)/2,1.47),(.2,yb-ya,2.94))
box((8,19,.49),(.2,2.9,.98));box((8,19,3.37),(.2,6,.86))
for yc in [16.7,21.3]:box((8,yc,2.63),(.2,1.14,.62))
prior={k:len(v[0]) for k,v in groups.items()}
window_y('Lecture','StageWindow',17.6,0,2.8,1.05,1.86,4,inside=-1)
transform_new_keys(prior,True,(8,0,0))
for i,yc in enumerate([16.7,21.3]):
 prior={k:len(v[0]) for k,v in groups.items()}
 door_y('Lecture',f'StageExit{i+1}',yc,0,1.04,inside=-1,double=False)
 transform_new_keys(prior,True,(8,0,0))
 # Swapping axes reflects the glyph outlines: mirror once more along the text baseline.
 glyph_key=('Lecture',f'StageExit{i+1}_ExitLettering','LW_ExitGreen',False)
 glyph_v,glyph_f=groups[glyph_key]
 groups[glyph_key]=[[(x,2*yc-y,z) for x,y,z in glyph_v],[tuple(reversed(face)) for face in glyph_f]]
# Rear wall windows are high above the supplied tier seating. Two 2.55m bays.
group('Lecture','TierWindowWall','LW_Plaster',True)
box((0,19,.79),(.22,6,1.58));box((0,19,3.56),(.22,6,.48))
for yc in [16.12,19,21.88]:box((0,yc,1.9),(.32,.28,3.8))
for i,y0 in enumerate([16.3,19.15]):
 prior={k:len(v[0]) for k,v in groups.items()}
 window_y('Lecture',f'TierWindow{i+1}',y0,0,2.55,1.65,1.65,4,inside=1)
 transform_new_keys(prior,True,(0,0,0))
group('Lecture','ProjectionScreen','LW_ScreenWhite');box((7.81,19,2.12),(.028,2.1,1.18))
group('Lecture','ProjectionScreenEdge','LW_BlackMetal')
for y in [17.94,20.06]:box((7.8,y,2.12),(.035,.024,1.23))
for z in [1.51,2.74]:box((7.8,19,z),(.035,2.15,.027))
group('Lecture','ProjectionScreenRoller','LW_WhiteMetal');rod((7.8,17.85,2.79),(7.8,20.15,2.79),.045,20)
group('Lecture','CeilingLightWoodFrame','LW_PaleOak')
for x in [2.15,5.85]:box((x,19,3.12),(.11,4.15,.12))
for y in [16.95,21.05]:box((4,y,3.12),(3.8,.11,.12))
group('Lecture','CeilingLightPanel','LW_Light');box((4,19,3.145),(3.6,3.98,.045))
group('Lecture','CeilingLightSuspension','LW_WhiteMetal')
for x in [2.2,5.8]:
 for y in [17,21]:rod((x,y,3.15),(x,y,3.8),.005,8)
ac('Lecture',6.2,19)
group('Lecture','WallSpeakers','LW_BlackMetal')
for y in [16.8,21.2]:box((7.78,y,3.22),(.17,.26,.39))
group('Lecture','SpeakerGrille','LW_Rubber')
for y in [16.8,21.2]:
 for z in [3.1,3.21,3.31]:rod((7.67,y,z),(7.655,y,z),.067,24)

# CULTURE CORNER: open sides intentionally preserve unknown room boundaries.
floor('Culture',20,16,6,5);ceiling('Culture',20,16,6,5,[20.15,25.85])
group('Culture','CornerWalls','LW_Plaster',True)
box((26,18.5,1.9),(.2,5,3.8));box((23,21,1.9),(6,.2,3.8))
ac('Culture',23,18.5)
for x in [21.8,24.4]:
 y=18.25;z=3.1
 group('Culture','WickerPendantCords','LW_BlackMetal');rod((x,y,z+.19),(x,y,3.8),.004,8)
 group('Culture','WickerPendantWeave','LW_Wicker')
 # Individually modelled radial bamboo strips and circumferential binding rings.
 for i in range(56):
  theta=i*math.tau/56;pts=[]
  for j in range(21):
   t=j/20;r=.035+.31*math.sin(t*math.pi/2);zz=z+.20-.28*t
   pts.append((x+r*math.cos(theta),y+r*math.sin(theta),zz))
  tube(pts,.0037,6)
 for j in range(5):
  t=.2+j*.2;r=.035+.31*math.sin(t*math.pi/2);ring((x,y,z+.20-.28*t),r,.0038,6,96)
 group('Culture','WickerPendantBulb','LW_Light');rod((x,y,z-.03),(x,y,z+.10),.055,24)
 group('Culture','WickerPendantSocket','LW_BlackMetal');rod((x,y,z+.09),(x,y,z+.18),.027,16)

# Mesh finalization: static object transforms are identity; UV0 has metric-repeat coordinates.
objects=[];manifest=[]
for (mod,part,mat,collision),(vs,fs) in groups.items():
 if not vs:continue
 name=f'SM_LW_A_{mod}_{part}_{mat[3:]}'
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(materials[mat]);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 if 'Glass' not in mat and len(fs)<18000 and 'Lettering' not in part:
  bevel=ob.modifiers.new('CloseRangeEdgeHighlights','BEVEL');bevel.width=.0025 if mat!='LW_Plaster' else .004;bevel.segments=2
  bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(45)
  try:bpy.ops.object.modifier_apply(modifier=bevel.name)
  except Exception:ob.modifiers.remove(bevel)
 me=ob.data
 uv=me.uv_layers.new(name='UVMap')
 scale=2 if mat in ['LW_FloorOak','LW_Plaster'] else 1
 for poly in me.polygons:
  axis=max(range(3),key=lambda a:abs(poly.normal[a]));axes=[a for a in range(3) if a!=axis]
  for li in poly.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co
   if mat=='LW_PaleOak' and 'Leaf_' in part and axis!=2:
    uv.data[li].uv=(co.z,co[0 if axis==1 else 1])
   else:uv.data[li].uv=(co[axes[0]]/scale,co[axes[1]]/scale)
  # Cylindrical services smooth; architectural boxes retain weighted corner definition.
  poly.use_smooth=any(s in part for s in ['Pipe','Ring','Weave','Cords','Suspension','Services','Roller','FlowingLED'])
 ob.select_set(False);objects.append(ob)
 mn=[min(v.co[a] for v in me.vertices) for a in range(3)];mx=[max(v.co[a] for v in me.vertices) for a in range(3)]
 manifest.append({'name':name,'module':mod,'part':part,'material':mat,'collision':collision,
                  'vertices':len(me.vertices),'polygons':len(me.polygons),'bounds_m':{'min':mn,'max':mx},
                  'source_photos':[f'20240831_{s}.jpg' for s in refs[mod]],'dimensions_status':'provisional_display_dimensions'})
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(OUT/'Architecture.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Architecture.blend'))
data={'version':1,'kind':'independent_photo_based_library_studies','coordinate_system':'Blender metres x/y/z; objects transforms baked to identity',
      'not_as_built':True,'notes':['Four spaced display modules; their relative arrangement is not the school floorplan.','Dimensions and detailed service routes are provisional visual study, not measured.','Open cutaway ends intentionally avoid inventing unknown partitions or corridors.','Each door leaf, glazing, handle, hinge and closer is separately identifiable for later pivot grouping.'],
      'materials':{n:{'color':c,'roughness':r,'metallic':m} for n,(c,r,m) in palette.items()},'meshes':manifest,
      'summary':{'mesh_count':len(manifest),'vertices':sum(m['vertices'] for m in manifest),'polygons':sum(m['polygons'] for m in manifest)},
      'modules':{'Main':{'origin':[0,0,0],'size':[14,8,3.8]},'Step':{'origin':[20,0,0],'size':[9,6,3.8]},'Lecture':{'origin':[0,16,0],'size':[8,6,3.8]},'Culture':{'origin':[20,16,0],'size':[6,5,3.8]}}}
(OUT/'architecture_manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIBRARY_ARCHITECTURE_COMPLETE',json.dumps(data['summary']),flush=True)
