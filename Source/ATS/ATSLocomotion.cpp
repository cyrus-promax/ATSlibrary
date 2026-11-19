#include "ATSLocomotion.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimNode_SequencePlayer.h"
#include "Animation/AnimationPoseData.h"
#include "Animation/AnimSequence.h"
#include "Animation/BlendSpace.h"
#include "AnimNodes/AnimNode_BlendSpacePlayer.h"
#include "AnimationRuntime.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
struct FATSLocomotionNode : FAnimNode_Base
{
 FAnimNode_BlendSpacePlayer_Standalone Ground;
 FAnimNode_SequencePlayer_Standalone Takeoff, Air, Landing;
 int32 State=0, PreviousState=0;
 float StateTime=0, BlendElapsed=0, BlendDuration=.2f;
 float Weights[4]={1,0,0,0}, StartWeights[4]={1,0,0,0};
 float Speed=0, VerticalSpeed=0;
 bool bFalling=false;

 FAnimNode_Base& Child(int32 Index)
 {
  if(Index==0)return Ground;
  if(Index==1)return Takeoff;
  if(Index==2)return Air;
  return Landing;
 }
 virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override
 {
  State=PreviousState=0; StateTime=BlendElapsed=0;
  for(int32 I=0;I<4;++I){Weights[I]=StartWeights[I]=I==0?1.f:0.f;Child(I).Initialize_AnyThread(Context);}
 }
 virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override
 {for(int32 I=0;I<4;++I)Child(I).CacheBones_AnyThread(Context);}
 virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override
 {
  const float Dt=Context.GetDeltaTime();
  StateTime+=Dt;
  int32 Next=State;
  if(bFalling)
  {
   if(State==0||State==3)Next=VerticalSpeed>0?1:2;
   else if(State==1 && (StateTime>=.18f||VerticalSpeed<=0))Next=2;
  }
  else if(State==1||State==2)Next=3;
  else if(State==3 && StateTime>=.1f)Next=0;
  if(Next!=State)
  {
   PreviousState=State;State=Next;StateTime=0;BlendElapsed=0;
   BlendDuration=State==2?.15f:State==0?.3f:.2f;
   for(int32 I=0;I<4;++I)StartWeights[I]=Weights[I];
   if(State!=0)Child(State).Initialize_AnyThread(FAnimationInitializeContext(Context.AnimInstanceProxy));
  }
  BlendElapsed+=Dt;
  const float Alpha=FMath::Clamp(BlendElapsed/BlendDuration,0.f,1.f);
  Ground.SetPosition(FVector(Speed,0,0));
  for(int32 I=0;I<4;++I)
  {
   Weights[I]=FMath::Lerp(StartWeights[I],I==State?1.f:0.f,Alpha);
   if(Weights[I]>ZERO_ANIMWEIGHT_THRESH)Child(I).Update_AnyThread(Context.FractionalWeight(Weights[I]));
  }
 }
 virtual void Evaluate_AnyThread(FPoseContext& Output) override
 {
  float Total=0;
  for(int32 I=0;I<4;++I)
  {
   if(Weights[I]<=ZERO_ANIMWEIGHT_THRESH)continue;
   if(Total==0)Child(I).Evaluate_AnyThread(Output);
   else
   {
    FPoseContext Added(Output), Mixed(Output);
    Child(I).Evaluate_AnyThread(Added);
    FAnimationPoseData A(Output),B(Added),Result(Mixed);
    FAnimationRuntime::BlendTwoPosesTogether(A,B,Total/(Total+Weights[I]),Result);
    Output=MoveTemp(Mixed);
   }
   Total+=Weights[I];
  }
  if(Total==0)Output.ResetToRefPose();
 }
};

struct FATSLocomotionProxy : FAnimInstanceProxy
{
 FATSLocomotionNode Root;
 FATSLocomotionProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
 virtual void Initialize(UAnimInstance* Instance) override
 {
  auto* Anim=CastChecked<UATSLocomotion>(Instance);
  Root.Ground.SetBlendSpace(Anim->GroundBlend);
  Root.Ground.SetLoop(true);
  Root.Takeoff.SetSequence(Anim->JumpStart);Root.Takeoff.SetLoopAnimation(false);
  Root.Air.SetSequence(Anim->JumpLoop);Root.Air.SetLoopAnimation(true);
  Root.Landing.SetSequence(Anim->JumpLoop);Root.Landing.SetLoopAnimation(false);Root.Landing.SetStartPosition(.6f);
  FAnimInstanceProxy::Initialize(Instance);
 }
 virtual FAnimNode_Base* GetCustomRootNode() override {return &Root;}
 virtual void PreUpdate(UAnimInstance* Instance,float DeltaSeconds) override
 {
  FAnimInstanceProxy::PreUpdate(Instance,DeltaSeconds);
  auto* Character=Cast<ACharacter>(Instance->TryGetPawnOwner());
  Root.Speed=Character?Character->GetVelocity().Size2D():0;
  Root.VerticalSpeed=Character?Character->GetVelocity().Z:0;
  Root.bFalling=Character&&Character->GetCharacterMovement()->IsFalling();
 }
 virtual void PostUpdate(UAnimInstance* Instance) const override
 {
  FAnimInstanceProxy::PostUpdate(Instance);
  auto* Anim=CastChecked<UATSLocomotion>(Instance);
  static const FName States[]={TEXT("Ground"),TEXT("Takeoff"),TEXT("Air"),TEXT("Landing")};
  Anim->Speed=Root.Speed;Anim->bAirborne=Root.bFalling;Anim->MotionState=States[Root.State];
 }
};
}

UATSLocomotion::UATSLocomotion()
{
 static ConstructorHelpers::FObjectFinder<UBlendSpace> Blend(TEXT("/Game/Actor/player/animation/BlendSpace1D"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Start(TEXT("/Game/Actor/player/animation/animation/Jump_Man"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Loop(TEXT("/Game/Actor/player/animation/animation/Jump_Loop_Man"));
 GroundBlend=Blend.Object;JumpStart=Start.Object;JumpLoop=Loop.Object;
}
FAnimInstanceProxy* UATSLocomotion::CreateAnimInstanceProxy(){return new FATSLocomotionProxy(this);}
void UATSLocomotion::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}
