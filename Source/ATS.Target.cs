using UnrealBuildTool;
public class ATSTarget : TargetRules { public ATSTarget(TargetInfo Target) : base(Target) { Type=TargetType.Game; DefaultBuildSettings=BuildSettingsVersion.V7; IncludeOrderVersion=EngineIncludeOrderVersion.Unreal5_7; ExtraModuleNames.Add("ATS"); } }
