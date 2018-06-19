$kodiExe = "%kodiexe%";
$exec = "%exec%";
$param = @(%args%);
if($param.Length -eq 0){
	$process = Start-Process $exec -PassThru;
}else{
	$process = Start-Process $exec -ArgumentList $param -PassThru;
}
if($process -ne $null){
	$process.WaitForExit();
}
if($param.Length -ge 1 -and $param[0].StartsWith("shell:AppsFolder\")){
	sleep %waittime%;
	$appInfo = $param[0].SubString("shell:AppsFolder\".Length).split("!")[0].split("_");
	$runningProcesses = Get-Process;
	foreach($runningProcess in $runningProcesses){
		if($runningProcess.Path -ne $null -and $runningProcess.Path.Contains($appInfo[0]) -and $runningProcess.Path.Contains($appInfo[1])){
			$runningProcess.WaitForExit();
			break;
		}
	}
}
Start-Process $kodiExe -WindowStyle Maximized -NoNewWindow;


