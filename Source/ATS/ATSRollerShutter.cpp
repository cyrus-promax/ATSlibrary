#include "ATSRollerShutter.h"

#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"

AATSRollerShutter::AATSRollerShutter()
{
 PrimaryActorTick.bCanEverTick=true;
 Frame=CreateDefaultSubobject<USceneComponent>(TEXT("Frame"));
 RootComponent=Frame;

 Slats=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Slats"));
 Slats->SetupAttachment(Frame);
 Slats->SetMobility(EComponentMobility::Movable);
 Slats->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Slats->SetGenerateOverlapEvents(false);
 Slats->SetCanEverAffectNavigation(false);

 CurtainCollision=CreateDefaultSubobject<UBoxComponent>(TEXT("CurtainCollision"));
 CurtainCollision->SetupAttachment(Frame);
 CurtainCollision->SetMobility(EComponentMobility::Movable);
 CurtainCollision->SetCollisionProfileName(TEXT("BlockAll"));
 CurtainCollision->SetGenerateOverlapEvents(false);
 CurtainCollision->SetCanEverAffectNavigation(false);
}

void AATSRollerShutter::OnConstruction(const FTransform& Transform)
{
 Super::OnConstruction(Transform);
 RebuildShutter();
}

void AATSRollerShutter::BeginPlay()
{
 Super::BeginPlay();
 RebuildShutter();
}

void AATSRollerShutter::RebuildShutter()
{
 Width=FMath::Max(20.f, Width);
 Height=FMath::Max(20.f, Height);
 SlatPitch=FMath::Clamp(SlatPitch, 1.f, Height);
 LiftSpeed=FMath::Max(1.f, LiftSpeed);
 ApproachDistance=FMath::Max(0.f, ApproachDistance);
 HoldOpenSeconds=FMath::Max(0.f, HoldOpenSeconds);
 CurrentLift=0.f;
 bOpen=false;
 LastNearbyTime=-1000000.0;
 Slats->ClearInstances();
 UpdateCurtain();
}

void AATSRollerShutter::UpdateCurtain()
{
 constexpr float SourceSlatWidth=100.f;
 constexpr float SourceSlatHeight=7.5f;
 constexpr float CollisionHalfThickness=3.f;
 const float RemainingHeight=FMath::Max(0.f, Height-CurrentLift);
 const int32 VisibleCount=RemainingHeight>.001f ? FMath::CeilToInt(RemainingHeight/SlatPitch) : 0;

 // Only the topmost slat is clipped; all other horizontal pitches stay fixed.
 // Removed slats disappear into the separate header box instead of entering 1F.
 while(Slats->GetInstanceCount()>VisibleCount)
 {
  Slats->RemoveInstance(Slats->GetInstanceCount()-1);
 }
 while(Slats->GetInstanceCount()<VisibleCount)
 {
  Slats->AddInstance(FTransform::Identity);
 }
 TArray<FTransform> Transforms;
 Transforms.Reserve(VisibleCount);
 for(int32 Index=0; Index<VisibleCount; ++Index)
 {
  const float Bottom=CurrentLift+Index*SlatPitch;
  const float VisibleHeight=FMath::Min(SlatPitch, Height-Bottom);
  Transforms.Emplace(FQuat::Identity,
   FVector(Width*.5f, 0.f, Bottom+VisibleHeight*.5f),
   FVector(Width/SourceSlatWidth, 1.f, VisibleHeight/SourceSlatHeight));
 }
 if(VisibleCount>0)
 {
  Slats->BatchUpdateInstancesTransforms(0, Transforms, false, true, true);
 }

 CurtainCollision->SetRelativeLocation(FVector(Width*.5f, 0.f, (Height+CurrentLift)*.5f));
 CurtainCollision->SetBoxExtent(FVector(Width*.5f, CollisionHalfThickness,
  FMath::Max(.01f, RemainingHeight*.5f)), true);
 CurtainCollision->SetCollisionEnabled(RemainingHeight>=.5f
  ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
}

void AATSRollerShutter::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 if(!GetWorld() || !GetWorld()->IsGameWorld())return;

 const double Now=GetWorld()->GetTimeSeconds();
 bool Nearby=false;
 bool InDoorway=false;
 for(TActorIterator<APawn> It(GetWorld()); It; ++It)
 {
  const APawn* Pawn=*It;
  if(!Pawn)continue;
  const FVector Local=GetActorTransform().InverseTransformPosition(Pawn->GetActorLocation());
  float Radius=45.f;
  float HalfHeight=100.f;
  if(const UCapsuleComponent* Capsule=Pawn->FindComponentByClass<UCapsuleComponent>())
  {
   Radius=Capsule->GetScaledCapsuleRadius();
   HalfHeight=Capsule->GetScaledCapsuleHalfHeight();
  }
  // Exclude pawns on the storey above; account for the character capsule rather
  // than treating its centre as a point at ground level.
  if(Local.Z-HalfHeight>=Height || Local.Z+HalfHeight<=0.f)continue;

  const float OutsideWidth=FMath::Max(FMath::Abs(Local.X-Width*.5f)-Width*.5f, 0.f);
  Nearby|=FVector2D(OutsideWidth, Local.Y).Size()<ApproachDistance;
  InDoorway|=Local.X>=-Radius-15.f && Local.X<=Width+Radius+15.f
   && FMath::Abs(Local.Y)<=Radius+30.f;
 }
 if(Nearby || InDoorway)LastNearbyTime=Now;
 bOpen=Nearby || InDoorway || Now-LastNearbyTime<HoldOpenSeconds;
 const float NextLift=FMath::FInterpConstantTo(CurrentLift, bOpen?Height:0.f,
  DeltaSeconds, LiftSpeed);
 if(!FMath::IsNearlyEqual(NextLift, CurrentLift, .0001f))
 {
  CurrentLift=NextLift;
  UpdateCurtain();
 }
}
