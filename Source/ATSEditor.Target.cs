using UnrealBuildTool;
public class ATSEditorTarget : TargetRules { public ATSEditorTarget(TargetInfo Target) : base(Target) { Type=TargetType.Editor; DefaultBuildSettings=BuildSettingsVersion.V7; IncludeOrderVersion=EngineIncludeOrderVersion.Unreal5_7; ExtraModuleNames.Add("ATS"); } }
