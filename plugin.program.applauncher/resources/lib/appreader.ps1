$code = @"
using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Text;
namespace System {
	public class ResourceExtractor {
	
		public static string ExtractString(string file, int number) {
			IntPtr lib = LoadLibrary(file);
			StringBuilder result = new StringBuilder(2048);
			LoadString(lib, number, result, result.Capacity);
			FreeLibrary(lib);
			return result.ToString();
		}
		public static Icon ExtractIcon(string file, int number) {
			IntPtr large;
			IntPtr small;
			ExtractIconEx(file, number, out large, out small, 1);
			try {
				return Icon.FromHandle(large);
			} catch {
				return null;
			}
		}
		[DllImport("Shell32.dll", EntryPoint = "ExtractIconExW", CharSet = CharSet.Unicode, ExactSpelling = true, CallingConvention = CallingConvention.StdCall)]
		private static extern int ExtractIconEx(string sFile, int iIndex, out IntPtr piLargeVersion, out IntPtr piSmallVersion, int amountIcons);
		
		[DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
		private static extern IntPtr LoadLibrary([MarshalAs(UnmanagedType.LPStr)]string lpFileName);
		[DllImport("user32.dll", CharSet = CharSet.Auto)]
		private static extern int LoadString(IntPtr hInstance, int ID, StringBuilder lpBuffer, int nBufferMax);
		[DllImport("kernel32.dll", SetLastError = true)]
		[return: MarshalAs(UnmanagedType.Bool)]
		private static extern bool FreeLibrary(IntPtr hModule);
	}
	
}
"@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing
$WshShell = New-Object -ComObject ("WScript.Shell");
$NAME_CONST = "name";
$EXEC_CONST = "exec";
$ARGS_CONST = "args";
$ICON_CONST = "icon";
$TYPE_CONST = "type";
$TYPE_APP_CONST = "app";
$TYPE_FOLDER_CONST = "folder";
$ALL_APPS_FOLDER_CONST = "all apps";
$ALLOWED_ICON_TYPES = @(".ico", ".jpg", ".jpeg", ".png", ".bmp");
$ALLOWED_EXEC_TYPES = @(".exe", ".com", ".bat");

$WINDOWS_STORE_APPS_FOLDER = "Store apps";
$ICON_STORE_FOLDER = $args[0];
$start1 = [Environment]::GetFolderPath('CommonStartMenu')+"\";
$start2 = [Environment]::GetFolderPath('StartMenu')+"\";
$startDirs = @($start1, $start2);
Add-Type -AssemblyName System.Drawing;
Add-Type -AssemblyName System.IO;
Function addShortCutToDirs($shortCut, $baseDir){
	if($shortCut.TargetPath -eq ""){
		return;
	}
	if(-not [IO.File]::Exists($shortCut.TargetPath)){
		return;
	}
	$currentExecType = $shortCut.TargetPath.substring($shortCut.TargetPath.length-4);
	$kill = $true;
	foreach($execType in $ALLOWED_EXEC_TYPES){
		if($execType -eq $currentExecType){
			$kill = $false;
			break;
		}
	}
	if($kill){
		return;
	}
	$fullName = $shortCut.FullName;
	$folders = $shortCut.FullName.SubString($baseDir.Length).Split("\");
	$name = $folders[-1].SubString(0, $folders[-1].Length - 4);
	$targetPath = [System.Environment]::ExpandEnvironmentVariables($shortCut.TargetPath)
	$icon = getIcon -icon $shortCut.IconLocation -executable $targetPath;
	$folder = getFolder -folders $folders -baseDir $baseDir;
	$appEntry = @{};
	$appEntry[$ICON_CONST] = $icon;
	$appEntry[$TYPE_CONST] = $TYPE_APP_CONST;
	$appEntry[$NAME_CONST] = $name;
	$appEntry[$EXEC_CONST] = $targetPath;
	$appEntry[$ARGS_CONST] = @($shortCut.Arguments.split(" "))
	$folder[$name] = $appEntry;
	$appData[$ALL_APPS_FOLDER_CONST][$name] = $appEntry;
}                                                                ;
Function getFolder($folders, $baseDir){
	$result = $appData;
	$dir = $baseDir;
	forEach($key in $folders){
		if($key.EndsWith(".lnk")){
			break;
		}
		$dir = $dir + $key + "\";
		$localized = getLocalizedDirName -dir $dir -default $key;
		if(-Not ($result.ContainsKey($localized))){
			$result[$localized] = @{};
			$result[$localized][$TYPE_CONST] = $TYPE_FOLDER_CONST;
		}
		$result = $result[$localized];
	}
	return $result;
}
Function getLocalizedDirName($dir, $default){
	$dini = $dir + "desktop.ini";
	if([IO.File]::Exists($dini)){
		$content = get-content $dini;
		foreach($line in $content){
			if($line.startswith("LocalizedResourceName=@")){
				$slength = $line.Length - "LocalizedResourceName=@".Length - ($line.Length - $line.indexof(",-"))
				$resourceName = $line.substring("LocalizedResourceName=@".Length, $slength);
				$resourceName = [System.Environment]::ExpandEnvironmentVariables($resourceName);
				$position = [int] $line.substring($line.indexof(",-")+2);
				return [System.ResourceExtractor]::ExtractString($resourceName, $position);
			}
		}
	}
	return $default;
}
Function getIcon($icon, $executable){
	$iconInfo = $icon.Split(",");
	$number = $iconInfo[1];
	$icon = [System.Environment]::ExpandEnvironmentVariables($icon)
	if([IO.File]::Exists($icon)){
		return $icon;
	}
	
	if($iconInfo[0] -eq ""){
		$icon = $executable;
	}else{
		$icon = $iconInfo[0];
	}
	$icon = [System.Environment]::ExpandEnvironmentVariables($icon)
	return getIconFromExe -exe $icon -position $number;
}
Function getIconFromExe($exe, $position){
	try{
		$path = $ICON_STORE_FOLDER + $exe.GetHashCode() + ".bmp";
		if(![IO.File]::Exists($path)){
			$myIcon = [System.ResourceExtractor]::ExtractIcon($exe, $position);
			$myIcon.ToBitmap().Save($path);
		}
		return $path;
	}
	catch{
		return "";
	}
}
Function getStartMenuEntries(){
	forEach($dir in $startDirs){
		$links = Get-ChildItem $dir *.lnk -recurse|Sort-Object -descending;
		ForEach( $link in $links){
			$linkPath = $link.DirectoryName + "\" + $link.Name;
			$shortCut = $WshShell.CreateShortcut($linkPath);
			addShortCutToDirs -shortCut $shortCut -baseDir $dir;
		}
	}
}
Function getStoreLogo($path){
	if([IO.File]::Exists($path)){
		return $path;
	}
	$path = $path.replace('/','\');
	$dir = $path.substring(0, $path.lastindexof("\")+1);
	$dirExists = Test-Path $dir;
	if(-not $dirExists){
		return $path;
	}
	$filepattern = $path.substring($path.lastindexof("\")+1);
	$filepattern = $filepattern.substring(0, $filepattern.lastindexof(".")) + "*" + $filepattern.substring($filepattern.lastindexof("."));
	$foundLogos = (Get-ChildItem $dir $filepattern);
	if($foundLogos -eq $null){
		return $path;
	}
	return $dir + $foundLogos[0].Name;
}
Function getStoreApps(){
	$tempStore = @{};
	$startItems = Get-StartApps;
	forEach($startItem in $startItems){
		$name = $startItem.Name;
		$appId = $startItem.AppID;
		$key = $appId.Split("_")[0];
		$tempStore[$key] = @{};
		$tempStore[$key]["inStart"] = $true;
		$tempStore[$key]["inAppx"] = $false;
		$tempStore[$key]["name"] = $name;
		$tempStore[$key]["appId"] = $appId;
	}
	$storeApps = Get-AppxPackage;
	forEach($storeApp in $storeApps){
		if($storeApp.IsFramework){
			continue;
		}
		$temp = @{};
		$packageName = $storeApp.PackageFullName;
		$installLocation = $storeApp.InstallLocation;
		$key = $storeApp.Name;
		$icon = (Get-AppxPackageManifest -package $packageName).package.applications.application.visualelements.Square44x44Logo;
		if($icon -is [array]){
			$icon = $icon[0];
		}
		if(-Not $tempStore.ContainsKey($key)){
			$temp["inStart"] = $false;
			$tempStore[$key] = $temp;
		}else{
			$temp = $tempStore[$key];
		}
		$temp["inAppx"] = $true;
		$temp["packageName"] = $packageName;
		$temp["installLocation"] = $installLocation;
		$temp["icon"] = getStoreLogo($installLocation + "\" + $icon);
	}

	$startAppsFolder = @{};
	$startAppsFolder[$TYPE_CONST] = $TYPE_FOLDER_CONST;
	$startAppsFolder[$NAME_CONST] = $WINDOWS_STORE_APPS_FOLDER;
	forEach($key in $tempStore.Keys){
		$temp = $tempStore[$key];

		if(-Not $temp["inAppx"] -Or -Not $temp["inStart"]){
			continue;
		}
		$entry = @{};
		$entry[$TYPE_CONST] = $TYPE_APP_CONST;
		$entry[$NAME_CONST] = $temp["name"];
		$entry[$ICON_CONST] = $temp["icon"];
		$entry[$EXEC_CONST] = "explorer"
		$entry[$ARGS_CONST] = @("shell:AppsFolder\" + $temp["appId"]);
		$startAppsFolder[$temp["name"]] = $entry;
		$appData[$ALL_APPS_FOLDER_CONST][$temp["name"]] = $entry;
	}
	$appData[$WINDOWS_STORE_APPS_FOLDER]=$startAppsFolder;
}
$appData = @{};
$appData[$ALL_APPS_FOLDER_CONST] = @{};
$appData[$ALL_APPS_FOLDER_CONST][$TYPE_CONST] = $TYPE_FOLDER_CONST;
getStartMenuEntries;
if([System.Environment]::OSVersion.Version.Major -ge 10){
	getStoreApps;
}
$json = ConvertTo-Json -InputObject $appData -Compress -Depth 100;
echo $json;
