"""New photo-informed ATS main-hall wall materials; no automatic execution.

create_dining_hall_mosaic(save=True) returns materials['mosaic'/'border'/'skirting'].
Only NEW assets under StructuralSurfaces_20261108 are created. Existing assets
with the same names are loaded without mutation; no actor, mesh or map is edited.

Room identity is now user-confirmed. The pale interlocking rectangular appearance
is visible in the 2021 dry activity and 2023 cleanup photographs. Native-pixel
inspection cannot decisively establish whether every module has two or three
strips. StripsPerBlock defaults to 3 as an EDITABLE VISUAL ESTIMATE, not a measured
site fact. BlockSizeCM=3.6 and JointWidthCM=0.08 likewise are rendering estimates.
Do not infer special reflective-wall boundaries or pink washing-room zoning.
"""

ASSET_ROOT = '/Game/ATS/Dining/WallFloorDetail_20261108/Materials'

MOSAIC_HLSL = r'''
float3 n = normalize((float3)SurfaceNormal);
float2 horizontal = float2(-n.y,n.x);
horizontal = (dot(horizontal,horizontal)>0.0001) ? normalize(horizontal) : float2(1,0);
float2 p = float2(dot((float2)WorldPos.xy,horizontal),WorldPos.z-FloorZCM);
float blockSize = max(BlockSizeCM,0.5);
float strips = clamp(floor(StripsPerBlock+0.5),2.0,4.0);
float2 block = floor(p/blockSize);
float2 q = frac(p/blockSize)*blockSize;
float parity = fmod(abs(block.x+block.y),2.0);
if (parity>0.5) q=q.yx;
float width = blockSize/strips;
float stripIndex = floor(q.y/width);
float2 local = float2(q.x,frac(q.y/width)*width);
float d = min(min(local.x,blockSize-local.x),min(local.y,width-local.y));
float footprint = max(length(ddx(p)),length(ddy(p)));
float aa = max(footprint,0.012);
float halfJoint = max(JointWidthCM,0.01)*0.5;
float grout = 1.0-smoothstep(halfJoint-aa*0.5,halfJoint+aa*0.5,d);
float3 hash = frac(float3(block.x,block.y,stripIndex)*float3(.1031,.1030,.0973));
hash += dot(hash,hash.yxz+33.33);
hash = frac((hash.xxy+hash.yzz)*hash.zyx);
float3 tile = (hash.x<.20) ? (float3)PalePinkTile :
              ((hash.x<.35) ? (float3)PaleCreamTile : (float3)PaleGreyTile);
tile *= lerp(.965,1.025,hash.y);
float3 averageTile = (float3)PalePinkTile*.20 + (float3)PaleCreamTile*.15 + (float3)PaleGreyTile*.65;
float meanJoint = saturate(JointWidthCM*(1.0/blockSize+1.0/width));
float3 resolved = lerp(tile,(float3)GroutColour,grout);
float3 average = lerp(averageTile,(float3)GroutColour,meanJoint);
// Filter fine joints and individual-tile variation as they become sub-pixel.
float visibility = saturate((1.35-footprint/width)/0.95);
// Keep the larger block's average colour after narrow strips become
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
float3 colour=lerp(average,lerp(blockMean,resolved,visibility),blockVisibility);
float rough = lerp(TileRoughness,0.80,grout*visibility);
return float4(saturate(colour),clamp(rough,0.45,0.85));
'''

BORDER_HLSL = r'''
float3 n = normalize((float3)SurfaceNormal);
float2 horizontal = float2(-n.y,n.x);
horizontal = (dot(horizontal,horizontal)>0.0001) ? normalize(horizontal) : float2(1,0);
float2 p = float2(dot((float2)WorldPos.xy,horizontal),WorldPos.z-FloorZCM);
float pitch = max(BorderTileCM,0.5);
float2 cell=floor(p/pitch);
float2 local=frac(p/pitch)*pitch;
float edge=min(min(local.x,pitch-local.x),min(local.y,pitch-local.y));
float footprint=max(length(ddx(p)),length(ddy(p)));
float aa=max(footprint,0.012);
float grout=1.0-smoothstep(JointWidthCM*.5-aa*.5,JointWidthCM*.5+aa*.5,edge);
float3 h=frac(float3(cell.x,cell.y,cell.x+cell.y)*float3(.1031,.1030,.0973));
h+=dot(h,h.yxz+33.33);h=frac((h.xxy+h.yzz)*h.zyx);
float3 tile=(float3)CharcoalColour*lerp(.92,1.07,h.x);
float3 detail=lerp(tile,(float3)BorderGrout,grout);
float3 mean=lerp((float3)CharcoalColour,(float3)BorderGrout,saturate(2*JointWidthCM/pitch));
float visibility=saturate((1.4-footprint/pitch)/1.0);
return float4(lerp(mean,detail,visibility),lerp(.40,.74,grout*visibility));
'''

SKIRTING_HLSL = r'''
float3 n=normalize((float3)SurfaceNormal);
float2 tangent=float2(-n.y,n.x);
tangent=(dot(tangent,tangent)>0.0001)?normalize(tangent):float2(1,0);
// Vertical surfaces project in horizontal wall tangent and world Z, never XY.
float2 p=float2(dot((float2)WorldPos.xy,tangent),WorldPos.z-FloorZCM);
float pitch=max(GrainPitchCM,.1);
float2 cell=floor(p/pitch);
float footprint=max(length(ddx(p)),length(ddy(p)))/pitch;
float aa=max(footprint,.015);
float best=0;
float3 chip=(float3)LightAggregate;
[unroll] for(int y=-1;y<=1;++y){
 [unroll] for(int x=-1;x<=1;++x){
  float2 id=cell+float2(x,y);
  float3 h=frac(float3(id.x,id.y,id.x+id.y)*float3(.1031,.1030,.0973));
  h+=dot(h,h.yxz+33.33);h=frac((h.xxy+h.yzz)*h.zyx);
  float2 q=p/pitch-(id+.15+.70*h.xy);
  float angle=h.z*6.2831853;
  float sn=sin(angle),cs=cos(angle);
  q=float2(cs*q.x-sn*q.y,sn*q.x+cs*q.y);
  float d=max(abs(q.x)*.90+abs(q.y)*.55,abs(q.x)*.62+abs(q.y)*.95);
  float radius=lerp(.14,.36,frac(h.z*23.17));
  float mask=(1-smoothstep(radius-aa*.5,radius+aa*.5,d))*step(h.y,.85);
  if(mask>best){
   best=mask;
   chip=lerp((float3)GreyAggregate,(float3)LightAggregate,step(.38,h.x));
   chip*=lerp(.88,1.08,h.z);
  }
 }
}
float3 matrix=(float3)DarkMatrix;
float3 average=lerp(matrix,(float3)GreyAggregate*.38+(float3)LightAggregate*.62,.18);
float visible=saturate((1.4-footprint)/1.05);
float3 detail=lerp(matrix,chip,best);
return float4(saturate(lerp(average,detail,visible)),.54);
'''


def _linear_rgb(rgb):
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
                 for v in (float(c)/255. for c in rgb))


def create_dining_hall_mosaic(save=True):
    import unreal
    ml=unreal.MaterialEditingLibrary
    lib=unreal.EditorAssetLibrary
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    names={'mosaic':'M_Dining_Hall_BasketMosaic_Multiscale','border':'M_Dining_Hall_CharcoalCap_FineJoint',
           'skirting':'M_Dining_Hall_DarkTerrazzoSkirting_Contrasted'}
    result={'materials':{},'material_paths':{},'created':[],'reused_untouched':[],
            'compile_requested':[],'scene_modified':False,
            'evidence':'User confirms the HK01 main hall. Pale alternating rectangular mosaic and charcoal tile cap are visible in 2021/2023 photos.',
            'unmeasured_settings':{'strips_per_block':3,'block_cm':3.6,'joint_cm':.08,'border_tile_cm':2.4,'skirting_grain_pitch_cm':.7},
            'limits':'Two-versus-three strip grouping is not decisive in original pixels. Dimensions, phase, colour swatches and roughness are visual estimates. No normal/displacement or invented special wall zones.',
            'validation':'Caller must verify new shader compilation logs and actual near/far rendering. RecompileMaterial returning None is not success proof.'}
    for key,name in names.items():
        path=ASSET_ROOT+'/'+name
        if lib.does_asset_exist(path):
            material=lib.load_asset(path)
            if not isinstance(material,unreal.Material):raise RuntimeError('Existing non-material target '+path)
            result['materials'][key]=material;result['material_paths'][key]=material.get_path_name()
            result['reused_untouched'].append(path)

    def node(m,cls,x=0,y=0):
        n=ml.create_material_expression(m,cls,x,y)
        if n is None:raise RuntimeError('Cannot create '+cls.__name__)
        return n
    def connect(a,b,pin='',output=''):
        inputs=[str(v) for v in ml.get_material_expression_input_names(b)]
        if pin and pin not in inputs:raise RuntimeError('Unknown input %r; available %r'%(pin,inputs))
        if not ml.connect_material_expressions(a,output,b,pin):raise RuntimeError('Cannot connect %s input %r; available %r'%(b.get_class().get_name(),pin,inputs))
    def prop(a,p):
        if not ml.connect_material_property(a,'',p):raise RuntimeError('Cannot connect property '+str(p))
    def scalar(m,name,value,y):
        n=node(m,unreal.MaterialExpressionScalarParameter,-600,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',float(value));return n
    def colour(m,name,rgb,y):
        n=node(m,unreal.MaterialExpressionVectorParameter,-600,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',unreal.LinearColor(*_linear_rgb(rgb),1));return n
    def constant(m,value,p,y):
        n=node(m,unreal.MaterialExpressionConstant,250,y);n.set_editor_property('r',float(value));prop(n,p)

    for key,name in names.items():
        if key in result['materials']:continue
        m=tools.create_asset(name,ASSET_ROOT,unreal.Material,unreal.MaterialFactoryNew())
        if m is None:raise RuntimeError('Cannot create material '+name)
        bindings={'WorldPos':node(m,unreal.MaterialExpressionWorldPosition,-900,-200),
                  'SurfaceNormal':node(m,unreal.MaterialExpressionVertexNormalWS,-900,-50),
                  'FloorZCM':scalar(m,'FloorZCM_ProjectionPhase',-2455,-100),
                  'JointWidthCM':scalar(m,'JointWidthCM_VisualEstimate',.08,0)}
        if key=='mosaic':
            bindings.update({
                'BlockSizeCM':scalar(m,'BlockSizeCM_VisualEstimate',3.6,100),
                'StripsPerBlock':scalar(m,'StripsPerBlock_VisualEstimate',3,200),
                'TileRoughness':scalar(m,'TileRoughness',.58,300),
                'PaleGreyTile':colour(m,'PaleGreyTile',(232,232,229),400),
                'PalePinkTile':colour(m,'PalePinkTile',(223,209,211),500),
                'PaleCreamTile':colour(m,'PaleCreamTile',(230,229,218),600),
                'GroutColour':colour(m,'PaleJointColour',(162,162,158),700)})
            code=MOSAIC_HLSL
        elif key=='border':
            bindings.update({'BorderTileCM':scalar(m,'BorderTileCM_VisualEstimate',2.4,100),
                             'CharcoalColour':colour(m,'CharcoalTile',(35,36,37),200),
                             'BorderGrout':colour(m,'BorderJoint',(82,82,80),300)})
            code=BORDER_HLSL
        else:
            bindings.update({'GrainPitchCM':scalar(m,'GrainPitchCM_VisualEstimate',.9,100),
                             'DarkMatrix':colour(m,'CharcoalTerrazzoMatrix',(29,30,30),200),
                             'GreyAggregate':colour(m,'GreyAggregate',(128,130,126),300),
                             'LightAggregate':colour(m,'LightAggregate',(224,224,216),400)})
            code=SKIRTING_HLSL
        custom=node(m,unreal.MaterialExpressionCustom,-100,0)
        custom.set_editor_property('description','ATS photo-based material; dimensions and strip count unmeasured')
        custom.set_editor_property('code',code)
        custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT4)
        custom_inputs=[]
        for name in bindings:
            item=unreal.CustomInput();item.set_editor_property('input_name',name);custom_inputs.append(item)
        custom.set_editor_property('inputs',custom_inputs)
        for name,expression in bindings.items():connect(expression,custom,name)
        for flags,target,y in [((True,True,True,False),unreal.MaterialProperty.MP_BASE_COLOR,0),
                               ((False,False,False,True),unreal.MaterialProperty.MP_ROUGHNESS,150)]:
            mask=node(m,unreal.MaterialExpressionComponentMask,100,y)
            for channel,value in zip(('r','g','b','a'),flags):mask.set_editor_property(channel,value)
            connect(custom,mask);prop(mask,target)
        constant(m,0,unreal.MaterialProperty.MP_METALLIC,300)
        constant(m,.35,unreal.MaterialProperty.MP_SPECULAR,400)
        ml.recompile_material(m);result['compile_requested'].append(m.get_path_name())
        if save and not lib.save_loaded_asset(m,only_if_is_dirty=True):raise RuntimeError('Cannot save '+m.get_path_name())
        result['materials'][key]=m;result['material_paths'][key]=m.get_path_name();result['created'].append(m.get_path_name())
    return result
