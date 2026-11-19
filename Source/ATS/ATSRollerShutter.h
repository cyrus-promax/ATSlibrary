#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ATSRollerShutter.generated.h"

class UBoxComponent;
class UInstancedStaticMeshComponent;
class USceneComponent;

/** The actor origin is the left edge of the doorway at floor level.
 *  Local X runs across its width, Y through the doorway, and Z points up.
 *  Slat meshes are centred and measure 100 x 2.8 x 7.5 cm before scaling.
 */
UCLASS()
class ATS_API AATSRollerShutter : public AActor
{
 GENERATED_BODY()

public:
 AATSRollerShutter();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;

 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Shutter")
 TObjectPtr<USceneComponent> Frame;

 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Shutter")
 TObjectPtr<UInstancedStaticMeshComponent> Slats;

 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Shutter")
 TObjectPtr<UBoxComponent> CurtainCollision;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="20.0", Units="cm"))
 float Width=220.f;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="20.0", Units="cm"))
 float Height=280.f;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="1.0", Units="cm"))
 float SlatPitch=7.5f;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="1.0", Units="cm/s"))
 float LiftSpeed=180.f;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="0.0", Units="cm"))
 float ApproachDistance=230.f;

 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Shutter", meta=(ClampMin="0.0", Units="s"))
 float HoldOpenSeconds=2.f;

 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category="Shutter")
 float CurrentLift=0.f;

 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category="Shutter")
 bool bOpen=false;

 UFUNCTION(BlueprintCallable, CallInEditor, Category="Shutter")
 void RebuildShutter();

private:
 void UpdateCurtain();
 double LastNearbyTime=-1000000.0;
};
