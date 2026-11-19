#include "ATSLibraryHunt.h"
#include "ATSTour.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Texture2D.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Styling/CoreStyle.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"

AATSLibraryEgg::AATSLibraryEgg(){
 PrimaryActorTick.bCanEverTick=true; EggMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Egg")); RootComponent=EggMesh;
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> Gold(TEXT("/Game/ATS/LibraryWorkshop_20261108/Materials/M_LW_SignGold.M_LW_SignGold"));
 if(Sphere.Succeeded())EggMesh->SetStaticMesh(Sphere.Object); if(Gold.Succeeded())EggMesh->SetMaterial(0,Gold.Object);
 EggMesh->SetMobility(EComponentMobility::Movable); EggMesh->SetRelativeScale3D(FVector(.38f,.38f,.53f));EggMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void AATSLibraryEgg::Tick(float DeltaSeconds){
 Super::Tick(DeltaSeconds); AATSLibraryHuntGameMode* M=GetWorld()->GetAuthGameMode<AATSLibraryHuntGameMode>();
 if(!M||!M->bStarted)return; APawn* P=UGameplayStatics::GetPlayerPawn(this,0);
 if(P&&FVector::Dist(P->GetActorLocation(),GetActorLocation())<=CollectDistance){M->CollectEgg();Destroy();}
}
AATSLibraryHuntGameMode::AATSLibraryHuntGameMode(){
 PrimaryActorTick.bCanEverTick=true;DefaultPawnClass=AATSTourCharacter::StaticClass();HUDClass=AHUD::StaticClass();
 static ConstructorHelpers::FObjectFinder<UTexture2D> Crest(TEXT("/Game/ATS/LibraryHunt/T_ATS_Crest.T_ATS_Crest"));
 if(Crest.Succeeded())CrestTexture=Crest.Object;
}
void AATSLibraryHuntGameMode::BeginPlay(){
 Super::BeginPlay();TArray<AATSLibraryEgg*> Eggs;for(TActorIterator<AATSLibraryEgg> It(GetWorld());It;++It)Eggs.Add(*It);Total=Eggs.Num();
 // Candidate locations lie on previously traversed paths; one per area, two in the main reading room.
 if(Eggs.Num()==5 && UGameplayStatics::GetCurrentLevelName(this,true).Contains(TEXT("ATS_Library_EggHunt_Complete"))){
  TArray<FVector> Main={FVector(500,-565,95),FVector(800,-565,95),FVector(1150,-565,95)};
  for(int32 I=Main.Num()-1;I>0;--I)Main.Swap(I,FMath::RandHelper(I+1));
  TArray<FVector> Culture={FVector(-288,-725,95),FVector(-220,-650,95)};
  TArray<FVector> Step={FVector(1600,-200,95),FVector(1883,-180,95),FVector(2100,-210,95)};
  TArray<FVector> Lecture={FVector(2420,-210,95),FVector(2543,-160,95)};
  TArray<FVector> Picks={Culture[FMath::RandHelper(Culture.Num())],Main[0],Main[1],Step[FMath::RandHelper(Step.Num())],Lecture[FMath::RandHelper(Lecture.Num())]};
  for(int32 I=0;I<Eggs.Num();++I)Eggs[I]->SetActorLocation(Picks[I],false,nullptr,ETeleportType::TeleportPhysics);
 }
 if(!GEngine||!GEngine->GameViewport)return;
 CrestBrush.SetResourceObject(CrestTexture);CrestBrush.ImageSize=FVector2D(150,170);CrestBrush.DrawAs=ESlateBrushDrawType::Image;
 HuntUI=SNew(SOverlay)
 +SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(24)
 [SNew(SBorder).Visibility_Lambda([this](){return bStarted?EVisibility::Visible:EVisibility::Collapsed;}).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.025f,.035f,.075f,.9f)).Padding(FMargin(20,14))
 [SNew(SVerticalBox)
 +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",23)).Text(FText::FromString(TEXT("圖書館尋寶")))]
 +SVerticalBox::Slot().AutoHeight().Padding(0,8,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",18)).Text_Lambda([this](){return FText::FromString(FString::Printf(TEXT("已找到彩蛋：%d / %d"),Found,Total));})]
 +SVerticalBox::Slot().AutoHeight().Padding(0,8,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",14)).Text_Lambda([this](){return FText::FromString(Total>0&&Found>=Total?TEXT("太棒了！你找到全部彩蛋！按 R 再玩一次。") : TEXT("探索圖書館，走近金色彩蛋即可收集。"));})]]]
 +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(0,0,0,22)
 [SNew(SBorder).Visibility_Lambda([this](){return bStarted?EVisibility::Visible:EVisibility::Collapsed;}).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.025f,.035f,.075f,.85f)).Padding(FMargin(16,9))
 [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",14)).Text(FText::FromString(TEXT("WASD 移動  ·  滑鼠環顧  ·  靠近彩蛋收集  ·  V 切換視角")))]]
 +SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Fill)
 [SNew(SBorder).Visibility_Lambda([this](){return bStarted?EVisibility::Collapsed:EVisibility::Visible;}).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.015f,.025f,.07f,.92f)).Padding(30)
 [SNew(SVerticalBox)
 +SVerticalBox::Slot().FillHeight(1)
 +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)[SNew(SBox).WidthOverride(150).HeightOverride(170)[SNew(SImage).Image(&CrestBrush)]]
 +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,16,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",32)).Text(FText::FromString(TEXT("香港仔工業學校")))]
 +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,8,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",26)).Text(FText::FromString(TEXT("圖書館尋寶")))]
 +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,18,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).Text(FText::FromString(TEXT("探索圖書館，找出五個隨機藏起的金色彩蛋！")))]
 +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,22,0,0)[SNew(SBox).WidthOverride(210).HeightOverride(50)[SNew(SButton).HAlign(HAlign_Center).VAlign(VAlign_Center).OnClicked_Lambda([this](){StartHunt();return FReply::Handled();})[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",20)).Text(FText::FromString(TEXT("開始遊戲")))]]]
 +SVerticalBox::Slot().FillHeight(1)]];
 GEngine->GameViewport->AddViewportWidgetContent(HuntUI.ToSharedRef(),10);
}
void AATSLibraryHuntGameMode::StartHunt(){
 if(bStarted)return;bStarted=true;
 if(APlayerController* PC=UGameplayStatics::GetPlayerController(this,0)){if(bInputLocked){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);bInputLocked=false;}PC->bShowMouseCursor=false;PC->SetInputMode(FInputModeGameOnly());}
}
void AATSLibraryHuntGameMode::CollectEgg(){if(bStarted&&Found<Total)++Found;}
void AATSLibraryHuntGameMode::Tick(float DeltaSeconds){
 Super::Tick(DeltaSeconds);APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);if(!PC)return;
 if(!bStarted&&!bInputLocked&&PC->GetPawn()){PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameAndUI());bInputLocked=true;}
 if(bStarted&&Total>0&&Found>=Total&&PC->WasInputKeyJustPressed(EKeys::R))UGameplayStatics::OpenLevel(this,FName(*UGameplayStatics::GetCurrentLevelName(this,true)));
}
void AATSLibraryHuntGameMode::EndPlay(const EEndPlayReason::Type Reason){if(HuntUI.IsValid()&&GEngine&&GEngine->GameViewport)GEngine->GameViewport->RemoveViewportWidgetContent(HuntUI.ToSharedRef());HuntUI.Reset();Super::EndPlay(Reason);}

