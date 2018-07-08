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
		public static Icon ExtractIcon(string file, int position) {
			IntPtr small;
			IntPtr big;
			SHDefExtractIcon(file, position, 0, out big, out small, 256);
			Icon result = Icon.FromHandle(big);
			DestroyIcon(small);
			return result;
		}
		[DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
		public static extern IntPtr LoadLibrary([MarshalAs(UnmanagedType.LPStr)]string lpFileName);
		[DllImport("user32.dll", CharSet = CharSet.Auto)]
		public static extern int LoadString(IntPtr hInstance, int ID, StringBuilder lpBuffer, int nBufferMax);
		[DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)] 
		public static extern bool DestroyIcon(IntPtr icon);
		[DllImport("kernel32.dll", SetLastError = true)]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool FreeLibrary(IntPtr hModule);
		[DllImport("Shell32.dll", EntryPoint = "SHDefExtractIconW", CharSet = CharSet.Unicode, ExactSpelling = true, CallingConvention = CallingConvention.StdCall)]
		public static extern int SHDefExtractIcon(string lpFileName, int iIndex, int uFlags, out IntPtr piLargeVersion, out IntPtr piSmallVersion, int size);
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
if($psversiontable.PSVersion.Major -lt 3){
	$start1 = "c:\ProgramData\Microsoft\Windows\Start Menu\";
}else{
	$start1 = [Environment]::GetFolderPath('CommonStartMenu')+"\";
}
$start2 = [Environment]::GetFolderPath('StartMenu')+"\";
$startDirs = @($start1, $start2);
Add-Type -AssemblyName System.Drawing;
Function addShortCutToDirs($shortCut, $baseDir){
	if($shortCut.TargetPath -eq ""){
		return;
	}
	if(-not (Test-Path $shortCut.TargetPath)){
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
	$name = getLocalizedName -path $fullName
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
}           
function getLocalizedName($path){
	$name = $path.substring($path.lastindexof("\")+1,$path.length - ($path.lastindexof("\")+5));
	$desktopIni = $path.substring(0, $path.lastindexof("\")+1) + "desktop.ini";
	if(-not (Test-Path $desktopIni)){
		return $name
	}
	try{
		$content = get-content $desktopIni;
		foreach($line in $content){
			if($line.startswith($name)){
				$split = $line.split("=");
				$info = $split[1].split(",");
				if($info[0].startsWith('@')){
					$resourceName = [System.Environment]::ExpandEnvironmentVariables($info[0].substring(1));
					$position = [int]$info[1];
					if($position -lt 0){
						$position = $position * -1;
					}
					$extracted = [System.ResourceExtractor]::ExtractString($resourceName, $position);
					if($extracted -eq ""){
						return $name;
					}
					return $extracted;
				}else{
					return $info[0];
				}
				
			}
		}
	}catch{
		return $name;
	}
	return $name;
}                                                     ;
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
	if(Test-Path $dini){
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
	if(Test-Path $icon){
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
		$path = $ICON_STORE_FOLDER + $exe.GetHashCode() + "v1.bmp";
		if(-not (Test-Path $path)){
			$myIcon = [System.ResourceExtractor]::ExtractIcon($exe, $position);
			$myIcon.ToBitmap().Save($path);
			[System.ResourceExtractor]::DestroyIcon($myIcon.Handle);
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
	if(Test-Path $path){
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

# Author: Joakim Borger Svendsen, 2017. http://www.json.org
# Svendsen Tech. Public domain licensed code.
# v0.3, 2017-04-12 (second release of the day, I actually read some JSON syntax this time)
#       Fixed so you don't double-whack the allowed escapes from the diagram, not quoting null, false and true as values.
# v0.4. Scientific numbers are supported (not quoted as values). 2017-04-12.
# v0.5. Adding switch parameter EscapeAllowedEscapesToo (couldn't think of anything clearer),
#       which also double-whacks (escapes with backslash) allowed escape sequences like \r, \n, \f, \b, etc.
#       Still 2017-04-12.
# v0.6: It's after midnight, so 2017-04-13 now. Added -QuoteValueTypes that makes it quote null, true and false as values.
# v0.7: Changed parameter name from EscapeAllowedEscapesToo to EscapeAll (... seems obvious now). Best to do it before it's
#       too late. 2017-04-13.
# v0.7.1: Made the +/- after "e" in numbers optional as this is apparently valid (as plus, then)
# v0.8: Added a -Compress parameter! 2017-04-13.
# v0.8.1: Fixed bug that made "x.y" be quoted (but scientific numbers and integers worked all the while). 2017-04-14.
# v0.8.2: Fixed bug with calculated properties (yay, this improves flexibility significantly). 2017-04-14.
# v0.9: Almost too many changes to mention. Now null, true and false as _value types_ are unquoted, otherwise they
#       are quoted. Comparing to the PowerShell team's ConvertTo-Json. Now escaping works better and more
#       standards-conforming. If you have a newline in the strings, it'll be replaced by "\n" (literally, not a newline),
# while if you have "\n" literally, it'll turn into \\n. Code quality improvements. Refactoring. Still some more to fix,
# but it's getting better. Datetime stuff is bothering me, not sure I like how it's handled in the PS team's cmdlet, but I
# don't have a sufficiently informed opinion.
#
# v0.9.1: Formatting fixes.
# v0.9.2: Returning proper value types when sending in only single values of $true and $false (passed through).
#         $null is buggy, but only if you pass in _nothing_ else, but $null. As a value in an array, hash or
#         anywhere else, it works fine.
# v0.9.2.1: Forgot.
# v0.9.2.2: Adding escaping of "solidus" (forward slash).
# v0.9.3: Coerce numbers from strings only if -CoerceNumberStrings is specified (non-default), properly detect numerical types and
#         by default omit double quotes only on these.
# v0.9.3.1: Respect and do not doublewhack/escape (regex) "\u[0-9a-f]{4}".
# v0.9.3.2: Undoing previous change ... (wrong logic).
# v0.9.3.3: Comparing to the PS team's ConvertTo-Json again and they don't escape "/" alone. Undoing 0.9.2.2 change.
# v0.9.3.4: Support the IA64 platform and int64 on that too.
# v0.9.4.0: Fix nested array bracket alignment issues. 2017-10-21.
# v0.9.5.0: Handle NaN for [Double] so it's a string and doesn't break JSON syntax with "Nan" unquoted
#           in the data.
#           * Add the -DateTimeAsISO8601 switch parameter (causing datetime objects to be in this format:
#           '2018-06-25T01:25:00').
# v0.9.5.1: Handle "infinity" as well for System.Double.
# v0.9.5.2: Fix bug with DateTime ISO formatting inside hash tables and PS objects.
######################################################################################################

# Take care of special characters in JSON (see json.org), such as newlines, backslashes
# carriage returns and tabs.
# '\\(?!["/bfnrt]|u[0-9a-f]{4})'
function FormatString {
    param(
        [String] $String)
    # removed: #-replace '/', '\/' `
    # This is returned 
    $String -replace '\\', '\\' -replace '\n', '\n' `
        -replace '\u0008', '\b' -replace '\u000C', '\f' -replace '\r', '\r' `
        -replace '\t', '\t' -replace '"', '\"'
}

# Meant to be used as the "end value". Adding coercion of strings that match numerical formats
# supported by JSON as an optional, non-default feature (could actually be useful and save a lot of
# calculated properties with casts before passing..).
# If it's a number (or the parameter -CoerceNumberStrings is passed and it 
# can be "coerced" into one), it'll be returned as a string containing the number.
# If it's not a number, it'll be surrounded by double quotes as is the JSON requirement.
function GetNumberOrString {
    param(
        $InputObject)
    if ($InputObject -is [System.Byte] -or $InputObject -is [System.Int32] -or `
        ($env:PROCESSOR_ARCHITECTURE -imatch '^(?:amd64|ia64)$' -and $InputObject -is [System.Int64]) -or `
        $InputObject -is [System.Decimal] -or `
        ($InputObject -is [System.Double] -and -not [System.Double]::IsNaN($InputObject) -and -not [System.Double]::IsInfinity($InputObject)) -or `
        $InputObject -is [System.Single] -or $InputObject -is [long] -or `
        ($Script:CoerceNumberStrings -and $InputObject -match $Script:NumberRegex)) {
        Write-Verbose -Message "Got a number as end value."
        "$InputObject"
    }
    else {
        Write-Verbose -Message "Got a string (or 'NaN') as end value."
        """$(FormatString -String $InputObject)"""
    }
}

function ConvertToJsonInternal {
    param(
        $InputObject, # no type for a reason
        [Int32] $WhiteSpacePad = 0)
    [String] $Json = ""
    $Keys = @()
    Write-Verbose -Message "WhiteSpacePad: $WhiteSpacePad."
    if ($null -eq $InputObject) {
        Write-Verbose -Message "Got 'null' in `$InputObject in inner function"
        $null
    }
    elseif ($InputObject -is [Bool] -and $InputObject -eq $true) {
        Write-Verbose -Message "Got 'true' in `$InputObject in inner function"
        $true
    }
    elseif ($InputObject -is [Bool] -and $InputObject -eq $false) {
        Write-Verbose -Message "Got 'false' in `$InputObject in inner function"
        $false
    }
    elseif ($InputObject -is [DateTime] -and $Script:DateTimeAsISO8601) {
        Write-Verbose -Message "Got a DateTime and will format it as ISO 8601."
        """$($InputObject.ToString('yyyy\-MM\-ddTHH\:mm\:ss'))"""
    }
    elseif ($InputObject -is [HashTable]) {
        $Keys = @($InputObject.Keys)
        Write-Verbose -Message "Input object is a hash table (keys: $($Keys -join ', '))."
    }
    elseif ($InputObject.GetType().FullName -eq "System.Management.Automation.PSCustomObject") {
        $Keys = @(Get-Member -InputObject $InputObject -MemberType NoteProperty |
            Select-Object -ExpandProperty Name)
        Write-Verbose -Message "Input object is a custom PowerShell object (properties: $($Keys -join ', '))."
    }
    elseif ($InputObject.GetType().Name -match '\[\]|Array') {
        Write-Verbose -Message "Input object appears to be of a collection/array type."
        Write-Verbose -Message "Building JSON for array input object."
        $Json += "[`n" + (($InputObject | ForEach-Object {
            if ($null -eq $_) {
                Write-Verbose -Message "Got null inside array."
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + "null"
            }
            elseif ($_ -is [Bool] -and $_ -eq $true) {
                Write-Verbose -Message "Got 'true' inside array."
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + "true"
            }
            elseif ($_ -is [Bool] -and $_ -eq $false) {
                Write-Verbose -Message "Got 'false' inside array."
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + "false"
            }
            elseif ($_ -is [DateTime] -and $Script:DateTimeAsISO8601) {
                Write-Verbose -Message "Got a DateTime and will format it as ISO 8601."
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$($_.ToString('yyyy\-MM\-ddTHH\:mm\:ss'))"""
            }
            elseif ($_ -is [HashTable] -or $_.GetType().FullName -eq "System.Management.Automation.PSCustomObject" -or $_.GetType().Name -match '\[\]|Array') {
                Write-Verbose -Message "Found array, hash table or custom PowerShell object inside array."
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + (ConvertToJsonInternal -InputObject $_ -WhiteSpacePad ($WhiteSpacePad + 4)) -replace '\s*,\s*$'
            }
            else {
                Write-Verbose -Message "Got a number or string inside array."
                $TempJsonString = GetNumberOrString -InputObject $_
                " " * ((4 * ($WhiteSpacePad / 4)) + 4) + $TempJsonString
            }
        }) -join ",`n") + "`n$(" " * (4 * ($WhiteSpacePad / 4)))],`n"
    }
    else {
        Write-Verbose -Message "Input object is a single element (treated as string/number)."
        GetNumberOrString -InputObject $InputObject
    }
    if ($Keys.Count) {
        Write-Verbose -Message "Building JSON for hash table or custom PowerShell object."
        $Json += "{`n"
        foreach ($Key in $Keys) {
            # -is [PSCustomObject]) { # this was buggy with calculated properties, the value was thought to be PSCustomObject
            if ($null -eq $InputObject.$Key) {
                Write-Verbose -Message "Got null as `$InputObject.`$Key in inner hash or PS object."
                $Json += " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$Key"": null,`n"
            }
            elseif ($InputObject.$Key -is [Bool] -and $InputObject.$Key -eq $true) {
                Write-Verbose -Message "Got 'true' in `$InputObject.`$Key in inner hash or PS object."
                $Json += " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$Key"": true,`n"            }
            elseif ($InputObject.$Key -is [Bool] -and $InputObject.$Key -eq $false) {
                Write-Verbose -Message "Got 'false' in `$InputObject.`$Key in inner hash or PS object."
                $Json += " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$Key"": false,`n"
            }
            elseif ($InputObject.$Key -is [DateTime] -and $Script:DateTimeAsISO8601) {
                Write-Verbose -Message "Got a DateTime and will format it as ISO 8601."
                $Json += " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$Key"": ""$($InputObject.$Key.ToString('yyyy\-MM\-ddTHH\:mm\:ss'))"",`n"
                
            }
            elseif ($InputObject.$Key -is [HashTable] -or $InputObject.$Key.GetType().FullName -eq "System.Management.Automation.PSCustomObject") {
                Write-Verbose -Message "Input object's value for key '$Key' is a hash table or custom PowerShell object."
                $Json += " " * ($WhiteSpacePad + 4) + """$Key"":`n$(" " * ($WhiteSpacePad + 4))"
                $Json += ConvertToJsonInternal -InputObject $InputObject.$Key -WhiteSpacePad ($WhiteSpacePad + 4)
            }
            elseif ($InputObject.$Key.GetType().Name -match '\[\]|Array') {
                Write-Verbose -Message "Input object's value for key '$Key' has a type that appears to be a collection/array."
                Write-Verbose -Message "Building JSON for ${Key}'s array value."
                $Json += " " * ($WhiteSpacePad + 4) + """$Key"":`n$(" " * ((4 * ($WhiteSpacePad / 4)) + 4))[`n" + (($InputObject.$Key | ForEach-Object {
                    #Write-Verbose "Type inside array inside array/hash/PSObject: $($_.GetType().FullName)"
                    if ($null -eq $_) {
                        Write-Verbose -Message "Got null inside array inside inside array."
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + "null"
                    }
                    elseif ($_ -is [Bool] -and $_ -eq $true) {
                        Write-Verbose -Message "Got 'true' inside array inside inside array."
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + "true"
                    }
                    elseif ($_ -is [Bool] -and $_ -eq $false) {
                        Write-Verbose -Message "Got 'false' inside array inside inside array."
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + "false"
                    }
                    elseif ($_ -is [DateTime] -and $Script:DateTimeAsISO8601) {
                        Write-Verbose -Message "Got a DateTime and will format it as ISO 8601."
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + """$($_.ToString('yyyy\-MM\-ddTHH\:mm\:ss'))"""
                    }
                    elseif ($_ -is [HashTable] -or $_.GetType().FullName -eq "System.Management.Automation.PSCustomObject" `
                        -or $_.GetType().Name -match '\[\]|Array') {
                        Write-Verbose -Message "Found array, hash table or custom PowerShell object inside inside array."
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + (ConvertToJsonInternal -InputObject $_ -WhiteSpacePad ($WhiteSpacePad + 8)) -replace '\s*,\s*$'
                    }
                    else {
                        Write-Verbose -Message "Got a string or number inside inside array."
                        $TempJsonString = GetNumberOrString -InputObject $_
                        " " * ((4 * ($WhiteSpacePad / 4)) + 8) + $TempJsonString
                    }
                }) -join ",`n") + "`n$(" " * (4 * ($WhiteSpacePad / 4) + 4 ))],`n"
            }
            else {
                Write-Verbose -Message "Got a string inside inside hashtable or PSObject."
                # '\\(?!["/bfnrt]|u[0-9a-f]{4})'
                $TempJsonString = GetNumberOrString -InputObject $InputObject.$Key
                $Json += " " * ((4 * ($WhiteSpacePad / 4)) + 4) + """$Key"": $TempJsonString,`n"
            }
        }
        $Json = $Json -replace '\s*,$' # remove trailing comma that'll break syntax
        $Json += "`n" + " " * $WhiteSpacePad + "},`n"
    }
    $Json
}

function ConvertTo-STJson {
    [CmdletBinding()]
    #[OutputType([Void], [Bool], [String])]
    param(
        [AllowNull()]
        [Parameter(Mandatory=$true,
                   ValueFromPipeline=$true,
                   ValueFromPipelineByPropertyName=$true)]
        $InputObject,
        [Switch] $Compress,
        [Switch] $CoerceNumberStrings = $false,
        [Switch] $DateTimeAsISO8601 = $false)
    begin{
        $JsonOutput = ""
        $Collection = @()
        # Not optimal, but the easiest now.
        [Bool] $Script:CoerceNumberStrings = $CoerceNumberStrings
        [Bool] $Script:DateTimeAsISO8601 = $DateTimeAsISO8601
        [String] $Script:NumberRegex = '^-?\d+(?:(?:\.\d+)?(?:e[+\-]?\d+)?)?$'
        #$Script:NumberAndValueRegex = '^-?\d+(?:(?:\.\d+)?(?:e[+\-]?\d+)?)?$|^(?:true|false|null)$'
    }
    process {
        # Hacking on pipeline support ...
        if ($_) {
            Write-Verbose -Message "Adding object to `$Collection. Type of object: $($_.GetType().FullName)."
            $Collection += $_
        }
    }
    end {
        if ($Collection.Count) {
            Write-Verbose -Message "Collection count: $($Collection.Count), type of first object: $($Collection[0].GetType().FullName)."
            $JsonOutput = ConvertToJsonInternal -InputObject ($Collection | ForEach-Object { $_ })
        }
        else {
            $JsonOutput = ConvertToJsonInternal -InputObject $InputObject
        }
        if ($null -eq $JsonOutput) {
            Write-Verbose -Message "Returning `$null."
            return $null # becomes an empty string :/
        }
        elseif ($JsonOutput -is [Bool] -and $JsonOutput -eq $true) {
            Write-Verbose -Message "Returning `$true."
            [Bool] $true # doesn't preserve bool type :/ but works for comparisons against $true
        }
        elseif ($JsonOutput-is [Bool] -and $JsonOutput -eq $false) {
            Write-Verbose -Message "Returning `$false."
            [Bool] $false # doesn't preserve bool type :/ but works for comparisons against $false
        }
        elseif ($Compress) {
            Write-Verbose -Message "Compress specified."
            (
                ($JsonOutput -split "\n" | Where-Object { $_ -match '\S' }) -join "`n" `
                    -replace '^\s*|\s*,\s*$' -replace '\ *\]\ *$', ']'
            ) -replace ( # these next lines compress ...
                '(?m)^\s*("(?:\\"|[^"])+"): ((?:"(?:\\"|[^"])+")|(?:null|true|false|(?:' + `
                    $Script:NumberRegex.Trim('^$') + `
                    ')))\s*(?<Comma>,)?\s*$'), "`${1}:`${2}`${Comma}`n" `
              -replace '(?m)^\s*|\s*\z|[\r\n]+'
        }
        else {
            ($JsonOutput -split "\n" | Where-Object { $_ -match '\S' }) -join "`n" `
                -replace '^\s*|\s*,\s*$' -replace '\ *\]\ *$', ']'
        }
    }
}

$appData = @{};
$appData[$ALL_APPS_FOLDER_CONST] = @{};
$appData[$ALL_APPS_FOLDER_CONST][$TYPE_CONST] = $TYPE_FOLDER_CONST;
getStartMenuEntries;
if([System.Environment]::OSVersion.Version.Major -ge 10){
	getStoreApps;
}

$json = ConvertTo-STJson $appData -Compress 
echo $json
