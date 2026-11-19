import pathlib,json,shutil
work=pathlib.Path(__file__).parent;root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/StructuralSurfaces_20261108';ref=out/'References';ref.mkdir(parents=True,exist_ok=True)
rd=work/'research/dining_structure_20261108'
for name in ['wall_registration.json','floor_registration.json','ceiling_registration.json','floor_shader_sampling.json','ats_school_intro_2026.pdf','ats_2026_native_page_24_00.jpg']:
 p=rd/name
 if p.exists():shutil.copy2(p,ref/name)
for p in [work/'research/dining_shutters/hk01_flood_06.jpg',work/'research/dining_layout/goodschool_2021_p15_image26.png']:
 shutil.copy2(p,ref/p.name)
for name in ['build_dining_hall_surface_panels.py','create_dining_registered_surface_materials.py','create_dining_hall_mosaic.py','create_dining_hall_material_assets.py','import_dining_structural_surfaces.py','validate_dining_structural_surfaces.py']:
 shutil.copy2(work/name,out/name)
notes='''餐廳主廳表面及定位核對（2026-11-08）

使用者已確認：HK01照片中有十字架、淡色馬賽克柱、黑色地面拼帶的主廳，就是目前還原的整層餐廳。
使用者再指出十字架窗牆在目前UE視角正前方；已保存當時相機與畫面。這對應 u=.23 的長牆，照片左側窗牆為 v=3.67、右側為 v=30.4。這只確定牆面方向，沒有把視角中心自動當成十字架的精確位置。

已修改：
1. 原先通廳泛用5cm方磚，改成實景可見的淡白灰、略粉、細長交錯馬賽克外觀。
2. 頂邊改深炭色細瓷磚，裙腳改黑底灰白碎石；保留原有洞口及邊線幾何。
3. 米色水磨石增加深淺碎石對比，修正遠距離變成過亮純米色的問題；門檻採相同地坪材質。
4. 新表面保持不擋路；上牆與天花保留已核對的低光澤白漆。

仍未完全還原：
馬賽克每組條數、尺寸、縫寬、材質色值與粗糙度是視覺近似，沒有實測。原照片不足以嚴格分辨每組兩條或三條，材質暫用可調的三條組法。
未添加無定位依據的整場黑拼帶、全場樑柱網、反光壁面分區。三根現有後排細柱原屬外廊估算重建，不能充當主廳內柱的測量依據。
已確認十字架窗牆方向，但兩窗與十字架的確切橫向位置、窗距，以及內柱距牆尺寸仍待確認。現有空白牆尚不能稱為已完成窗牆還原。

本輪查閱新2026學校簡介全部36頁；新增用膳近照沒有解決完整地板與樑柱配準。參考資料及限制見References。
'''
(out/'本次表面還原說明.txt').write_text(notes,encoding='utf-8-sig')
print('STRUCTURAL_EVIDENCE_PACKAGED')
