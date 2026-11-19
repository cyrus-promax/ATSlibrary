#include "ATSTour.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "EngineUtils.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Styling/CoreStyle.h"

AATSTourPoint::AATSTourPoint(){RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("TourStop"));}
AATSAutoDoor::AATSAutoDoor(){PrimaryActorTick.bCanEverTick=true; RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Frame")); Hinge=CreateDefaultSubobject<USceneComponent>(TEXT("Hinge")); Hinge->SetupAttachment(RootComponent); Leaf=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DoorLeaf")); Leaf->SetupAttachment(Hinge); Leaf->SetMobility(EComponentMobility::Movable); Leaf->SetCollisionProfileName(TEXT("BlockAll"));}
void AATSAutoDoor::Tick(float Delta){Super::Tick(Delta); const float Now=GetWorld()->GetTimeSeconds(); bool Near=false; bool InSweep=false; for(TActorIterator<APawn> I(GetWorld()); I; ++I){const APawn* P=*I;if(!P)continue; const FVector L=GetActorTransform().InverseTransformPosition(P->GetActorLocation()); const float D=FVector2D(L.X-55,L.Y).Size(); if(FMath::Abs(L.Z-90)<150){Near|=D<ApproachDistance;InSweep|=D<160;}} if(Near)LastNearby=Now; bOpen=Near||InSweep||Now-LastNearby<CloseDelay; CurrentAngle=FMath::FInterpConstantTo(CurrentAngle,bOpen?OpenAngle:0.f,Delta,130.f); Hinge->SetRelativeRotation(FRotator(0,CurrentAngle,0)); Leaf->SetCollisionEnabled(FMath::Abs(CurrentAngle)<8?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);}

void AATSTourHUD::BeginPlay(){Super::BeginPlay();if(!GEngine||!GEngine->GameViewport)return;auto Character=[this](){return Cast<AATSTourCharacter>(GetOwningPawn());};auto Title=[Character](){auto*C=Character();return FText::FromString(C?C->StopTitle:TEXT("ATS"));};auto Details=[Character](){auto*C=Character();return FText::FromString(C?C->StopDescription:TEXT(""));};auto PanelVisibility=[Character](){auto*C=Character();return C&&C->bShowHelp?EVisibility::Visible:EVisibility::Collapsed;};
 TourUI=SNew(SOverlay)
 +SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(22)[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.018,.028,.03,.65)).Padding(FMargin(14,10))[SNew(SVerticalBox)
 +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Text(FText::FromString(TEXT("ATS  香港仔工業學校"))).Font(FCoreStyle::GetDefaultFontStyle("Regular",16))]
 +SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[SNew(STextBlock).Text_Lambda(Title).Font(FCoreStyle::GetDefaultFontStyle("Regular",13)).ColorAndOpacity(FLinearColor(.8,.84,.81))]]]
 +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(SBorder).Visibility_Lambda(PanelVisibility).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.02,.035,.04,.95)).Padding(28)[SNew(SBox).WidthOverride(470)[SNew(SVerticalBox)
 +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold",22)).Text(FText::FromString(TEXT("步行探索校園")))]
 +SVerticalBox::Slot().AutoHeight().Padding(0,18,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",16)).Text(FText::FromString(TEXT("W A S D　前後左右移動\n滑鼠　環顧四周\nCtrl　按住跑步（無體力限制）\nSpace　跳躍　　V　第一／第三人稱\nAlt　自由環視，放開回正\n滾輪　第三人稱遠近\n靠近門口　自動開門\n中鍵　釋放／收回游標\nTab　關閉說明")))]
  +SVerticalBox::Slot().AutoHeight().Padding(0,20,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",13)).Text(FText::FromString(TEXT("入口右轉可經側門進入禮堂，舞台在左邊。課室保留；未有依據的內部結構及上樓路線已撤下，未還原區域暫不開放。"))).AutoWrapText(true)]
 +SVerticalBox::Slot().AutoHeight().Padding(0,20,0,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",12)).Text(FText::FromString(TEXT("依實景影片及公開照片重建。未取得完整樓層圖，部分位置與尺寸為估算。\n周邊三維實景：© 地政總署／香港特別行政區政府"))).AutoWrapText(true).ColorAndOpacity(FLinearColor(.65,.7,.7))]]]]
 +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(0,0,0,18)[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.018,.028,.03,.62)).Padding(FMargin(14,8))[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",13)).Text(FText::FromString(TEXT("WASD 移動   ·   滑鼠環顧   ·   靠近開門   ·   V 視角   ·   Tab 操作說明")))]];
 GEngine->GameViewport->AddViewportWidgetContent(TourUI.ToSharedRef(),10);
}
void AATSTourHUD::EndPlay(const EEndPlayReason::Type Reason){if(TourUI.IsValid()&&GEngine&&GEngine->GameViewport)GEngine->GameViewport->RemoveViewportWidgetContent(TourUI.ToSharedRef());TourUI.Reset();Super::EndPlay(Reason);}
AATSTourGameMode::AATSTourGameMode(){DefaultPawnClass=AATSTourCharacter::StaticClass();HUDClass=AATSTourHUD::StaticClass();}
