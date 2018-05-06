# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

$WshShell = New-Object -ComObject ("WScript.Shell")
$NAME_CONST = "name"
$EXEC_CONST = "exec"
$ICON_CONST = "icon"
$TYPE_CONST = "type"
$TYPE_APP_CONST = "app"
$TYPE_FOLDER_CONST = "folder"
$ALL_APPS_FOLDER_CONST = "all apps"
$ALLOWED_ICON_TYPES = @(".ico", ".jpg", ".jpeg", ".png", ".bmp")
$WINDOWS_STORE_APPS_FOLDER = "Store apps"
$ICON_STORE_FOLDER = $args[0]
$startDirs = @("C:\ProgramData\Microsoft\Windows\Start Menu\Programs")
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO

Function addShortCutToDirs($shortCut, $baseDir){
	if($shortCut.TargetPath -eq ""){
		return
	}
	$folders = $shortCut.FullName.SubString($baseDir.Length + 1).Split("\")
	#Write-Host "FOLDERS: " + $folders
	$name = $folders[-1].SubString(0, $folders[-1].Length - 4)
	#Write-Host "NAME: " + $name
	$icon = getIcon -icon $shortCut.IconLocation -executable $shortCut.TargetPath
	$exec = $shortCut.TargetPath + " " + $shortCut.Arguments
	$folder = getFolder -folders $folders
	$appEntry = @{}
	$appEntry[$ICON_CONST] = $icon
	$appEntry[$TYPE_CONST] = $TYPE_APP_CONST
	$appEntry[$NAME_CONST] = $name
	$appEntry[$EXEC_CONST] = $exec
	#Write-Host "NAME: " + $name
	#Write-Host "FOLDER_STRUCT: "
	
	$folder[$name] = $appEntry
	$appData[$ALL_APPS_FOLDER_CONST][$name] = $appEntry
}                                                                
Function getFolder($folders){
	
	$result = $appData
	forEach($key in $folders){
		if($key.EndsWith(".lnk")){
			break
		}
		if(-Not ($appData.ContainsKey($key))){
			$result[$key] = @{}
			$result[$key][$TYPE_CONST] = $TYPE_FOLDER_CONST
		}
		$result = $result[$key]
	}
	return $result
}
Function getIcon($icon, $executable){
	$iconInfo = $icon.Split(",")
	#Write-Host $icon
	#Write-Host $executable
	if($iconInfo[0] -eq ""){
		return getIconFromExe -exe $executable
	}
	$ext = $iconInfo[0].SubString($iconInfo[0].Length - 4).toLower()
	if($ALLOWED_ICON_TYPES.Contains($ext)){
		return $iconInfo[0]
	}
	if($ext -eq ".exe"){
		return getIconFromExe -exe $iconInfo[0]
	}
	return getIconFromExe -exe $executable
}
Function getIconFromExe($exe){
	$realExe = [System.Environment]::ExpandEnvironmentVariables($exe)
	#Write-Host "look here"
	#Write-Host "REAL_EXE: " $realExe
	#Write-Host "EXE: " $exe
	try{
		$myIcon = [Drawing.Icon]::ExtractAssociatedIcon($realExe)
		$path = $ICON_STORE_FOLDER + $realExe.GetHashCode() + ".bmp"
		if(![IO.File]::Exists($path)){
			#$stream = New-Object IO.FileStream $path ,'Create','Write','Read'
			$myIcon.ToBitmap().Save($path)
			#$stream.Close()
		}	
		return $path
	}
	catch{
		return ""
	}
}
Function getStartMenuEntries(){
	forEach($dir in $startDirs){
		$links = Get-ChildItem $dir *.lnk -recurse
		ForEach( $link in $links){
			$linkPath = $link.DirectoryName + "\" + $link.Name
			$shortCut = $WshShell.CreateShortcut($linkPath)
			addShortCutToDirs -shortCut $shortCut -baseDir $dir
		}
	}
}

Function getStoreApps(){
	$tempStore = @{}
	$startItems = Get-StartApps
	forEach($startItem in $startItems){
		$name = $startItem.Name
		$appId = $startItem.AppID
		$key = $appId.Split("_")[0]
		$tempStore[$key] = @{}
		$tempStore[$key]["inStart"] = $true
		$tempStore[$key]["inAppx"] = $false
		$tempStore[$key]["name"] = $name
		$tempStore[$key]["appId"] = $appId
	}
	$storeApps = Get-AppxPackage
	forEach($storeApp in $storeApps){
		if($storeApp.IsFramework){
			continue
		}
		$temp = @{}
		$packageName = $storeApp.PackageFullName
		$installLocation = $storeApp.InstallLocation
		$key = $storeApp.Name
		#Write-Host "PACKAGE_NAME: " $packageName
		$icon = (Get-AppxPackageManifest -package $packageName).package.applications.application.visualelements.Square150x150Logo
		if(-Not $tempStore.ContainsKey($key)){
			$temp["inStart"] = $false
			$tempStore[$key] = $temp
		}else{
			$temp = $tempStore[$key]
		}
		$temp["inAppx"] = $true
		$temp["packageName"] = $packageName
		$temp["installLocation"] = $installLocation
		$temp["icon"] = $installLocation + "\" + $icon
	}
	
	#ConvertTo-Json $tempStore|Write-Host
	$startAppsFolder = @{}
	$startAppsFolder[$TYPE_CONST] = $TYPE_FOLDER_CONST
	$startAppsFolder[$NAME_CONST] = $WINDOWS_STORE_APPS_FOLDER
	forEach($key in $tempStore.Keys){
		$temp = $tempStore[$key]
		#Write-Host "TEMP: " $temp
		#Write-Host "TEMP: " $temp.getType()
		if(-Not $temp["inAppx"] -Or -Not $temp["inStart"]){
			continue
		}
		#Write-Host "after continue"
		$entry = @{}
		$entry[$TYPE_CONST] = $TYPE_APP_CONST
		$entry[$NAME_CONST] = $temp["name"]
		$entry[$ICON_CONST] = $temp["icon"]
		$entry[$EXEC_CONST] = "explorer shell:AppsFolder\" + $temp["appId"]
		#Write-Host "ENTRY: " + $entry
		$startAppsFolder[$temp["name"]] = $entry
		$appData[$ALL_APPS_FOLDER_CONST][$temp["name"]] = $entry
	}
	$appData[$WINDOWS_STORE_APPS_FOLDER]=$startAppsFolder
}

$appData = @{}
$appData[$ALL_APPS_FOLDER_CONST] = @{}
$appData[$ALL_APPS_FOLDER_CONST][$TYPE_CONST] = $TYPE_FOLDER_CONST

getStartMenuEntries
if([System.Environment]::OSVersion.Version.Major -ge 10){
	getStoreApps
}
$json = ConvertTo-Json -InputObject $appData
echo $json
