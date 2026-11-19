"""Create NEW ATS photo-informed finish assets; never touch scene/existing assets.

UE Python entry point (this file has no auto-run block):
    namespace = {}
    exec(open(PATH, encoding="utf-8").read(), namespace)
    result = namespace["create_dining_photo_materials"](save=True)
    floor = result["materials"]["floor"]
    paint = result["materials"]["paint"]

Default creates only floor and paint. Set include_wall_studies=True to also create
two UNASSIGNED alternatives; evidence does not establish which entire walls use
which finish. This module never finds actors, applies materials, changes a level,
loads a map, modifies imported textures, or overwrites an existing material.

Appearance follows 2021 dry hall + 2023 cleanup photographs. Numeric dimensions,
colours and roughness below are visual rendering choices, NOT site measurements.
No floor-band grid, slab-joint grid, beam layout or photographed perspective crop
is introduced. The existing red/brown terrazzo_tiles_diff_4k.jpg was inspected and
rejected as the main colour source: desaturating it loses the dark/light contrast.
"""

ASSET_ROOT = "/Game/ATS/Dining/PhotoFinishes_20261108/Materials"

# Native shader: two sparse layers of randomly oriented angular aggregate.
# World-space centimetres keep stone scale independent of large floor UVs.
# Analytic edge filtering + per-layer distance fading reduce distant sparkling.
TERRAZZO_HLSL = r"""
float2 plane = (float2)WorldPos.xy / max(ChipScale, 0.05);
float pixelCM = max(length(ddx(plane)), length(ddy(plane)));
float3 colour = MatrixColour;
float rough = DryRoughness;

[unroll] for (int layer = 0; layer < 2; ++layer)
{
    // Coarse diameter about 2-8 mm; fine diameter about 1-3 mm.
    float pitch = (layer == 0) ? 1.05 : 0.36;
    float2 p = plane / pitch;
    float2 cell = floor(p);
    float aa = max(pixelCM / pitch, 0.018);
    float layerFade = saturate((1.5 - pixelCM / pitch) / 1.1);
    float bestMask = 0.0;
    float3 bestColour = MatrixColour;
    float bestRough = DryRoughness;
    [unroll] for (int y = -1; y <= 1; ++y)
    {
        [unroll] for (int x = -1; x <= 1; ++x)
        {
            float2 id = cell + float2(x,y);
            // Arithmetic hash avoids sin's large-world precision instability.
            float3 h = frac(float3(id.x, id.y, id.x + id.y) *
                            float3(0.1031,0.1030,0.0973) + layer * 7.17);
            h += dot(h, h.yxz + 33.33);
            h = frac((h.xxy + h.yzz) * h.zyx);
            float3 h2 = frac(h.yzx * float3(29.53,43.17,61.91) + 0.127);
            float2 centre = id + 0.15 + 0.7 * h.xy;
            float2 q = p - centre;
            float angle = 6.2831853 * h.z;
            float sn = sin(angle), cs = cos(angle);
            q = float2(cs*q.x-sn*q.y, sn*q.x+cs*q.y);
            q.x *= lerp(0.82, 1.24, h2.x);
            q.y *= lerp(0.86, 1.20, h2.y);
            // Clipped diamond, varied in proportion: chips rather than dots.
            float d = max(max(abs(q.x)*0.90 + abs(q.y)*0.54,
                              abs(q.x)*0.68 + abs(q.y)*0.93),
                          abs(q.x + q.y*0.15)*0.96);
            float radius = (layer == 0) ? lerp(0.11,0.37,h2.z)
                                        : lerp(0.16,0.39,h2.z);
            float active = step(h2.y, (layer == 0) ? 0.86 : 0.72);
            float mask = (1.0-smoothstep(radius-aa*0.55,
                                       radius+aa*0.55,d)) * active;
            if (mask > bestMask)
            {
                float pick = frac(h.x*17.17+h.y*41.71+h.z*13.43);
                float3 chip = (pick < 0.31) ? DarkChipColour :
                              ((pick < 0.64) ? MidChipColour : LightChipColour);
                chip *= lerp(0.87,1.12,h2.x);
                bestColour = lerp(MatrixColour,chip,ChipContrast);
                bestMask = mask;
                bestRough = clamp(DryRoughness + (h.z-0.5)*0.07,0.42,0.68);
            }
        }
    }
    // Under-resolved grain converges toward a mild average, not aliased speckles.
    float3 meanChip = DarkChipColour*0.31 + MidChipColour*0.33 + LightChipColour*0.36;
    float3 layerMean = lerp(MatrixColour,meanChip,0.16*ChipContrast);
    colour = lerp(colour, layerMean, (1.0-layerFade)*0.30);
    colour = lerp(colour,bestColour,bestMask*layerFade);
    rough = lerp(rough,bestRough,bestMask*layerFade);
}
return float4(saturate(colour),clamp(rough,0.42,0.68));
"""

WALL_STUDY_HLSL = r"""
float3 n = normalize((float3)SurfaceNormal);
float3 tangent = normalize(float3(-n.y,n.x,0.00001));
float2 p = float2(dot((float3)WorldPos,tangent),WorldPos.z);
float aa = max(length(ddx(p)),length(ddy(p)));
float2 tile;
float2 index;
if (BasketPattern > 0.5)
{
    float cell = 4.0;  // Illustrative scale only: two rectangular units per cell.
    float2 block = floor(p/cell);
    float2 local = frac(p/cell)*cell;
    float parity = fmod(abs(block.x+block.y),2.0);
    if (parity > 0.5) local = local.yx;
    tile = float2(cell,cell*0.5);
    index = floor(local/tile) + block*2.0;
    p = local;
}
else
{
    tile = float2(2.0,2.0); // Unmeasured visual scale, not a factual tile size.
    index = floor(p/tile);
}
float2 uv = frac(p/tile)*tile;
float edge = min(min(uv.x,tile.x-uv.x),min(uv.y,tile.y-uv.y));
float grout = 1.0-smoothstep(0.045-aa*0.5,0.045+aa*0.5,edge);
float variation = frac(sin(dot(index,float2(12.9898,78.233)))*43758.5453);
float3 tileColour = TileColour * lerp(0.96,1.035,variation);
float fade = saturate(1.5-aa/max(min(tile.x,tile.y),0.1));
return float4(lerp(tileColour,GroutColour,grout*fade),0.64);
"""


def _linear(rgb):
    """Convert deliberately selected sRGB colour swatches to linear UE values."""
    return tuple(v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
                 for v in (channel/255.0 for channel in rgb))


def create_dining_photo_materials(save=True, include_wall_studies=False):
    """Return material objects + created/reused paths; never apply them to meshes.

    Existing asset names are read and returned without mutation, recompilation or
    saving. A conflicting non-Material asset aborts before any new asset is made.
    Compilation is requested only for newly created materials. This does not by
    itself prove an error-free live shader: caller must inspect UE compile results
    and a lit close-up before applying the output to the campus.
    """
    import unreal

    ml = unreal.MaterialEditingLibrary
    lib = unreal.EditorAssetLibrary
    assets = unreal.AssetToolsHelpers.get_asset_tools()
    names = {"floor": "M_Dining_BeigeFineTerrazzo_Dry",
             "paint": "M_Dining_OffWhitePaint_Matte"}
    if include_wall_studies:
        names.update({"basket_study": "M_Dining_PaleBasketMosaic_UNASSIGNED",
                      "pink_study": "M_Dining_PinkSquareMosaic_UNASSIGNED"})
    report = {"materials": {}, "materials_by_name": {}, "material_paths": {},
              "created": [], "reused_untouched": [],
              "compile_results": {}, "scene_modified": False,
              "unassigned_studies": [],
              "validation": "UE shader compilation and lit near/far appearance require caller verification.",
              "note": "Shader numeric settings are visual approximations, not site measurements."}

    # Preflight the complete target set before mutating even the new folder.
    for key, name in names.items():
        path = ASSET_ROOT + "/" + name
        if lib.does_asset_exist(path):
            material = lib.load_asset(path)
            if not isinstance(material, unreal.Material):
                raise RuntimeError("Refusing existing non-Material target: " + path)
            report["materials"][key] = material
            report["materials_by_name"][name] = material
            report["material_paths"][key] = material.get_path_name()
            report["reused_untouched"].append(path)

    def node(material, cls, x=0, y=0):
        result = ml.create_material_expression(material, cls, x, y)
        if result is None:
            raise RuntimeError("Could not create expression: " + cls.__name__)
        return result

    def link(a, b, pin="", output=""):
        # UE's single-input nodes do not necessarily expose the display label
        # "Input" as a connectable pin name. Empty selects the first input by
        # the documented MaterialEditingLibrary contract. Custom inputs retain
        # their explicit names, which we check against this installed engine.
        actual_inputs = [str(value) for value in
                         ml.get_material_expression_input_names(b)]
        if pin and pin not in actual_inputs:
            raise RuntimeError("Unknown input %r on %s; available inputs: %r" %
                               (pin, b.get_class().get_name(), actual_inputs))
        if not ml.connect_material_expressions(a, output, b, pin):
            raise RuntimeError("Could not connect input %r on %s; available inputs: %r" %
                               (pin, b.get_class().get_name(), actual_inputs))

    def property_link(a, prop):
        if not ml.connect_material_property(a, "", prop):
            raise RuntimeError("Could not connect material property: " + str(prop))

    def scalar(material, name, value, y):
        result = node(material, unreal.MaterialExpressionScalarParameter, -650, y)
        result.set_editor_property("parameter_name", name)
        result.set_editor_property("default_value", value)
        return result

    def colour(material, name, rgb, y):
        result = node(material, unreal.MaterialExpressionVectorParameter, -650, y)
        result.set_editor_property("parameter_name", name)
        result.set_editor_property("default_value", unreal.LinearColor(*_linear(rgb), 1.0))
        return result

    def constant(material, value, prop, y):
        result = node(material, unreal.MaterialExpressionConstant, 250, y)
        result.set_editor_property("r", value)
        property_link(result, prop)

    def custom_rgba(material, code, bindings):
        custom = node(material, unreal.MaterialExpressionCustom, -120, 0)
        custom.set_editor_property("description", "ATS photo-informed appearance; dimensions unmeasured")
        custom.set_editor_property("code", code)
        custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
        inputs = []
        for name in bindings:
            item = unreal.CustomInput()
            item.set_editor_property("input_name", name)
            inputs.append(item)
        custom.set_editor_property("inputs", inputs)
        for name, expression in bindings.items():
            link(expression, custom, name)
        rgb = node(material, unreal.MaterialExpressionComponentMask, 100, 0)
        alpha = node(material, unreal.MaterialExpressionComponentMask, 100, 150)
        for expression, flags in [(rgb, (True,True,True,False)),
                                  (alpha, (False,False,False,True))]:
            for channel, value in zip(("r","g","b","a"), flags):
                expression.set_editor_property(channel, value)
            link(custom, expression)
        property_link(rgb, unreal.MaterialProperty.MP_BASE_COLOR)
        property_link(alpha, unreal.MaterialProperty.MP_ROUGHNESS)

    for key, name in names.items():
        if key in report["materials"]:
            continue
        material = assets.create_asset(name, ASSET_ROOT, unreal.Material,
                                       unreal.MaterialFactoryNew())
        if material is None:
            raise RuntimeError("Cannot create fresh material " + name)
        # Material defaults are opaque/default-lit/one-sided. No normal map or
        # displacement: polished aggregate should not resemble raised gravel.
        if key == "floor":
            wp = node(material, unreal.MaterialExpressionWorldPosition, -900, -200)
            bindings = {
                "WorldPos": wp,
                "ChipScale": scalar(material, "AggregateScale_VisualEstimate", 1.0, -100),
                "ChipContrast": scalar(material, "AggregateContrast", 0.94, 0),
                "DryRoughness": scalar(material, "DryRoughness", 0.55, 100),
                "MatrixColour": colour(material, "WarmBeigeMatrix", (202,195,173), 200),
                "DarkChipColour": colour(material, "CharcoalChips", (63,63,58), 300),
                "MidChipColour": colour(material, "WarmGreyChips", (137,135,123), 400),
                "LightChipColour": colour(material, "IvoryChips", (222,218,204), 500),
            }
            custom_rgba(material, TERRAZZO_HLSL, bindings)
        elif key == "paint":
            base = colour(material, "OffWhitePaint", (231,230,225), 0)
            rough = scalar(material, "MattePaintRoughness", 0.84, 120)
            property_link(base, unreal.MaterialProperty.MP_BASE_COLOR)
            property_link(rough, unreal.MaterialProperty.MP_ROUGHNESS)
        else:
            wp = node(material, unreal.MaterialExpressionWorldPosition, -900, -200)
            normal = node(material, unreal.MaterialExpressionVertexNormalWS, -900, -50)
            basket = key == "basket_study"
            bindings = {
                "WorldPos": wp, "SurfaceNormal": normal,
                "BasketPattern": scalar(material, "BasketPattern", 1.0 if basket else 0.0, 0),
                "TileColour": colour(material, "TileColour", (222,219,210) if basket else (213,190,184), 150),
                "GroutColour": colour(material, "GroutColour", (187,182,174), 300),
            }
            custom_rgba(material, WALL_STUDY_HLSL, bindings)
            report["unassigned_studies"].append(material.get_path_name())
        constant(material, 0.0, unreal.MaterialProperty.MP_METALLIC, 300)
        constant(material, 0.35, unreal.MaterialProperty.MP_SPECULAR, 400)
        compile_result = ml.recompile_material(material)
        report["compile_results"][key] = str(compile_result)
        # Some UE versions return errors; older versions return None.
        if compile_result is not None and hasattr(compile_result, "__len__") and len(compile_result):
            raise RuntimeError("New material compile messages: " + str(compile_result))
        if save and not lib.save_loaded_asset(material, only_if_is_dirty=True):
            raise RuntimeError("Could not save NEW material " + name)
        report["materials"][key] = material
        report["materials_by_name"][name] = material
        report["material_paths"][key] = material.get_path_name()
        report["created"].append(material.get_path_name())
    return report
