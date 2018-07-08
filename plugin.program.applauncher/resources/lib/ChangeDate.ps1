if($psversiontable.PSVersion.Major -lt 3){
	$start1 = "c:\ProgramData\Microsoft\Windows\Start Menu\";
}else{
	$start1 = [Environment]::GetFolderPath('CommonStartMenu')+"\";
}
$start2 = [Environment]::GetFolderPath('StartMenu')+"\";
$startDirs = @($start1, $start2);

$time = -1;
foreach($startDir in $startDirs){
	$newTime = (Get-Item $startDir).LastWriteTime.ToFileTime();
	if( $newTime -gt $time ) {
		$time = $newTime;
	} 
}
echo $time