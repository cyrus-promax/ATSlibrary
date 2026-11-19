#include "ATSTour.h"
#include "ATSLocomotion.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "InputCoreTypes.h"

AATSTourCharacter::AATSTourCharacter()
{
 PrimaryActorTick.bCanEverTick=true;
 GetCapsuleComponent()->InitCapsuleSize(35,90);
 BaseEyeHeight=64;CrouchedEyeHeight=32;
 JumpMaxCount=1;JumpMaxHoldTime=0;
 bUseControllerRotationYaw=false;
 auto* Move=GetCharacterMovement();
 // Values read from the current BluePlanet BP_player, including braking and air control.
 Move->MaxWalkSpeed=180;Move->MaxWalkSpeedCrouched=120;
 Move->MaxAcceleration=900;Move->BrakingDecelerationWalking=1200;
 Move->BrakingDecelerationFalling=1500;Move->GroundFriction=6;
 Move->BrakingFriction=0;Move->BrakingFrictionFactor=1;Move->bUseSeparateBrakingFriction=true;
 Move->JumpZVelocity=520;Move->GravityScale=1.75f;Move->AirControl=.35f;
 Move->AirControlBoostMultiplier=2;Move->AirControlBoostVelocityThreshold=25;
 Move->MaxStepHeight=45;Move->MinAnalogWalkSpeed=20;Move->PerchRadiusThreshold=15;
 Move->bOrientRotationToMovement=true;Move->RotationRate=FRotator(0,360,0);
 Arm=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
 Arm->SetupAttachment(RootComponent);Arm->SetAbsolute(false,true,false);
 Arm->bUsePawnControlRotation=false;
 Arm->bInheritPitch=Arm->bInheritYaw=Arm->bInheritRoll=false;
 Arm->TargetArmLength=320;Arm->SocketOffset=FVector(0,60,65);
 Arm->ProbeSize=12;Arm->CameraLagSpeed=16;Arm->bEnableCameraRotationLag=false;
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("TourCamera"));
 Camera->SetupAttachment(Arm);Camera->FieldOfView=90;
 GetMesh()->SetRelativeLocationAndRotation(FVector(0,0,-89),FRotator(0,-90,0));
 GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 for(const TCHAR* Name:{TEXT("Pullover"),TEXT("Pants"),TEXT("Shoes")})
 {
  auto* Part=CreateDefaultSubobject<USkeletalMeshComponent>(FName(Name));
  Part->SetupAttachment(GetMesh());Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);Outfit.Add(Part);
 }
}

void AATSTourCharacter::BeginPlay()
{
 Super::BeginPlay();
 GetMesh()->SetSkeletalMesh(LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Man/Mesh/Full/SK_Man_Full_01.SK_Man_Full_01")));
 GetMesh()->SetAnimInstanceClass(UATSLocomotion::StaticClass());
 for(const auto& Part:Outfit)
 {
  const FString Asset=FString::Printf(TEXT("/Game/Man/Mesh/Parts/SK_Man_%s.SK_Man_%s"),*Part->GetName(),*Part->GetName());
  Part->SetSkeletalMesh(LoadObject<USkeletalMesh>(nullptr,*Asset));Part->SetLeaderPoseComponent(GetMesh());
 }
 // Keep the school entrance heading while applying BluePlanet's camera pitch and offsets.
 Arm->SetWorldRotation(FRotator(-12,GetActorRotation().Yaw,0));
 ApplyPerspective();
 if(auto* P=Cast<APlayerController>(Controller))
 {P->bShowMouseCursor=false;P->SetInputMode(FInputModeGameOnly());P->SetControlRotation(Arm->GetComponentRotation());}
 LastSafeLocation=GetActorLocation();StopTitle=TEXT("校門");
}

void AATSTourCharacter::ApplyPerspective()
{
 Arm->TargetArmLength=bFirstPerson?0:ThirdPersonDistance;
 Arm->SocketOffset=bFirstPerson?FVector::ZeroVector:FVector(0,60,65);
 Arm->TargetOffset=bFirstPerson?FVector(0,0,BaseEyeHeight):FVector::ZeroVector;
 Arm->bDoCollisionTest=!bFirstPerson;Arm->bEnableCameraLag=!bFirstPerson;
 GetMesh()->SetOwnerNoSee(bFirstPerson);
 for(const auto& Part:Outfit)Part->SetOwnerNoSee(bFirstPerson);
}

void AATSTourCharacter::FinishFreeLook()
{
 if(bFreeLookActive||bFreeLookReturning)Arm->SetWorldRotation(FreeLookOrigin);
 bFreeLookActive=bFreeLookReturning=false;
 GetCharacterMovement()->bOrientRotationToMovement=!bFirstPerson;
}

void AATSTourCharacter::ToggleCursor()
{
 if(auto* P=Cast<APlayerController>(Controller))
 {
  FinishFreeLook();
  bFreeLookNeedsRelease=P->IsInputKeyDown(EKeys::LeftAlt)||P->IsInputKeyDown(EKeys::RightAlt);
  P->bShowMouseCursor=!P->bShowMouseCursor;
  if(P->bShowMouseCursor)
  {FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);P->SetInputMode(Mode);StopJumping();}
  else P->SetInputMode(FInputModeGameOnly());
 }
}

void AATSTourCharacter::UpdateControls(float Delta,APlayerController* P)
{
 if(P->WasInputKeyJustPressed(EKeys::MiddleMouseButton)&&!bShowHelp)ToggleCursor();
 if(P->WasInputKeyJustPressed(EKeys::Tab))
 {bShowHelp=!bShowHelp;if(bShowHelp!=P->bShowMouseCursor)ToggleCursor();}
 const bool Blocked=bShowHelp||P->bShowMouseCursor||P->IsMoveInputIgnored();
 const bool Alt=P->IsInputKeyDown(EKeys::LeftAlt)||P->IsInputKeyDown(EKeys::RightAlt);
 if(Blocked)
 {FinishFreeLook();bFreeLookNeedsRelease=Alt;bSprinting=false;GetCharacterMovement()->MaxWalkSpeed=180;StopJumping();return;}
 if(P->WasInputKeyJustPressed(EKeys::V))
 {if(!bFirstPerson)ThirdPersonDistance=Arm->TargetArmLength;bFirstPerson=!bFirstPerson;ApplyPerspective();}
 if(!bFirstPerson)
 {
  const int32 Wheel=(P->WasInputKeyJustPressed(EKeys::MouseScrollDown)?1:0)-(P->WasInputKeyJustPressed(EKeys::MouseScrollUp)?1:0);
  if(Wheel){ThirdPersonDistance=FMath::Clamp(ThirdPersonDistance+20*Wheel,220.f,420.f);Arm->TargetArmLength=ThirdPersonDistance;}
 }
 if(!Alt)bFreeLookNeedsRelease=false;
 if(Alt&&!bFreeLookNeedsRelease&&!bFreeLookActive)
 {if(!bFreeLookReturning)FreeLookOrigin=Arm->GetComponentRotation();bFreeLookActive=true;bFreeLookReturning=false;}
 else if(!Alt&&bFreeLookActive){bFreeLookActive=false;bFreeLookReturning=true;}
 if(bFreeLookReturning)
 {
  const FRotator Rotation=Arm->GetComponentRotation();
  const FRotator Difference=(FreeLookOrigin-Rotation).GetNormalized();
  Arm->SetWorldRotation(Rotation+Difference*(1.f-FMath::Exp(-8.f*Delta)));
  if(FMath::Abs(Difference.Yaw)<=.25f&&FMath::Abs(Difference.Pitch)<=.25f)FinishFreeLook();
 }
 else
 {
  float X=0,Y=0;P->GetInputMouseDelta(X,Y);
  // BluePlanet cancels the engine's .07 mouse scaling before applying .2 degrees/pixel.
  FRotator Rotation=Arm->GetComponentRotation();
  Rotation.Yaw=FRotator::NormalizeAxis(Rotation.Yaw+X*(.2f/.07f));
  Rotation.Pitch=FMath::Clamp(FRotator::NormalizeAxis(Rotation.Pitch)+Y*(.2f/.07f),-80.f,75.f);
  Arm->SetWorldRotation(Rotation);
 }
 P->SetControlRotation(Arm->GetComponentRotation());
 const bool Free=bFreeLookActive||bFreeLookReturning;
 const FRotator Yaw(0,Free?FreeLookOrigin.Yaw:Arm->GetComponentRotation().Yaw,0);
 const float Forward=(P->IsInputKeyDown(EKeys::W)||P->IsInputKeyDown(EKeys::Up)?1.f:0.f)-(P->IsInputKeyDown(EKeys::S)||P->IsInputKeyDown(EKeys::Down)?1.f:0.f);
 const float Right=(P->IsInputKeyDown(EKeys::D)||P->IsInputKeyDown(EKeys::Right)?1.f:0.f)-(P->IsInputKeyDown(EKeys::A)||P->IsInputKeyDown(EKeys::Left)?1.f:0.f);
 AddMovementInput(Yaw.Vector(),Forward);AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y),Right);
 bSprinting=P->IsInputKeyDown(EKeys::LeftControl);
 GetCharacterMovement()->MaxWalkSpeed=bSprinting?450:180;
 GetCharacterMovement()->bOrientRotationToMovement=!Free&&!bFirstPerson;
 if(bFirstPerson&&!Free)SetActorRotation(Yaw);
 if(P->WasInputKeyJustPressed(EKeys::SpaceBar))Jump();
 if(P->WasInputKeyJustReleased(EKeys::SpaceBar))StopJumping();
}

void AATSTourCharacter::Tick(float Delta)
{
 Super::Tick(Delta);
 auto* P=Cast<APlayerController>(Controller);
 if(!P||!IsLocallyControlled())return;
 UpdateControls(Delta,P);
 if(GetCharacterMovement()->IsMovingOnGround())LastSafeLocation=GetActorLocation();
 if(GetActorLocation().Z<LastSafeLocation.Z-1800)
 {TeleportTo(LastSafeLocation,GetActorRotation(),false,true);GetCharacterMovement()->StopMovementImmediately();}
 float Nearest=FLT_MAX;
 for(TActorIterator<AATSTourPoint>I(GetWorld());I;++I)
 {
  const FVector D=I->GetActorLocation()-GetActorLocation();
  if(FMath::Abs(D.Z)>230)continue;
  const float Distance=D.SizeSquared2D();
  if(Distance<Nearest){Nearest=Distance;CurrentStop=I->StopNumber;StopTitle=I->Title;StopDescription=I->Description;}
 }
}
