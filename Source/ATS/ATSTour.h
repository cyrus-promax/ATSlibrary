#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "ATSTour.generated.h"
class UCameraComponent; class USpringArmComponent; class UStaticMeshComponent; class UAnimSequence; class SWidget;

UCLASS()
class ATS_API AATSTourPoint : public AActor {
 GENERATED_BODY()
public:
 AATSTourPoint();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tour") int32 StopNumber=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tour") FString Title;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tour",meta=(MultiLine=true)) FString Description;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tour") bool bSurveyExterior=false;
};

UCLASS()
class ATS_API AATSAutoDoor : public AActor {
 GENERATED_BODY()
public:
 AATSAutoDoor(); virtual void Tick(float Delta) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USceneComponent> Hinge;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Leaf;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door") float OpenAngle=-100.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door") float ApproachDistance=240.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door") float CloseDelay=1.5f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Door") float CurrentAngle=0.f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Door") bool bOpen=false;
private: float LastNearby=-100.f;
};

UCLASS()
class ATS_API AATSTourCharacter : public ACharacter {
 GENERATED_BODY()
public:
 AATSTourCharacter(); virtual void Tick(float Delta) override; virtual void BeginPlay() override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USpringArmComponent> Arm;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 CurrentStop=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bFirstPerson=true;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Movement") bool bSprinting=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Camera") bool bFreeLookActive=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Camera") bool bFreeLookReturning=false;
 bool bShowHelp=false; FString StopTitle; FString StopDescription;
private:
 UPROPERTY() TArray<TObjectPtr<USkeletalMeshComponent>> Outfit;
 void ApplyPerspective(); void ToggleCursor(); void FinishFreeLook();
 void UpdateControls(float Delta,class APlayerController* Player);
 FVector LastSafeLocation;
 FRotator FreeLookOrigin;
 bool bFreeLookNeedsRelease=false;
 float ThirdPersonDistance=320;
};

UCLASS()
class ATS_API AATSTourHUD : public AHUD {
 GENERATED_BODY()
public: virtual void BeginPlay() override; virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private: TSharedPtr<SWidget> TourUI;
};

UCLASS()
class ATS_API AATSTourGameMode : public AGameModeBase {
 GENERATED_BODY()
public: AATSTourGameMode();
};
