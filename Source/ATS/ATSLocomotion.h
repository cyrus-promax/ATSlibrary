#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "ATSLocomotion.generated.h"

class UBlendSpace;
class UAnimSequence;

// Uses the original BluePlanet clips and speed blend; no gameplay or stamina dependency.
UCLASS(Transient)
class ATS_API UATSLocomotion : public UAnimInstance
{
 GENERATED_BODY()
public:
 UATSLocomotion();
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Locomotion") float Speed=0;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Locomotion") bool bAirborne=false;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Locomotion") FName MotionState=TEXT("Ground");
 UPROPERTY() TObjectPtr<UBlendSpace> GroundBlend;
 UPROPERTY() TObjectPtr<UAnimSequence> JumpStart;
 UPROPERTY() TObjectPtr<UAnimSequence> JumpLoop;
 virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
 virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
