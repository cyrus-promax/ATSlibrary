#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "Styling/SlateBrush.h"
#include "ATSLibraryHunt.generated.h"
class UStaticMeshComponent; class UTexture2D; class SWidget;
UCLASS()
class ATS_API AATSLibraryEgg : public AActor {
 GENERATED_BODY()
public:
 AATSLibraryEgg(); virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Library Hunt") TObjectPtr<UStaticMeshComponent> EggMesh;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Library Hunt") float CollectDistance=115.f;
};
UCLASS()
class ATS_API AATSLibraryHuntGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 AATSLibraryHuntGameMode(); virtual void BeginPlay() override; virtual void EndPlay(const EEndPlayReason::Type Reason) override; virtual void Tick(float DeltaSeconds) override;
 void CollectEgg(); void StartHunt();
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Library Hunt") int32 Found=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Library Hunt") int32 Total=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Library Hunt") bool bStarted=false;
private:
 UPROPERTY() TObjectPtr<UTexture2D> CrestTexture;
 FSlateBrush CrestBrush; TSharedPtr<SWidget> HuntUI; bool bInputLocked=false;
};
