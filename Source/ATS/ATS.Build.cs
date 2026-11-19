using UnrealBuildTool;
public class ATS : ModuleRules { public ATS(ReadOnlyTargetRules Target) : base(Target) { PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs; PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore","Slate","SlateCore","AnimGraphRuntime"}); } }
