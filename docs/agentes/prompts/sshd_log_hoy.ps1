$ev = Get-WinEvent -FilterHashtable @{LogName='OpenSSH/Operational'; StartTime=(Get-Date).Date} -ErrorAction SilentlyContinue | Where-Object { $_.Message -match 'Accepted' }
$rows = foreach ($e in $ev) {
  $m = ($e.Message -replace '\s+',' ')
  $ip = if ($m -match 'from (\d+\.\d+\.\d+\.\d+)') { $Matches[1] } else { '?' }
  $u  = if ($m -match 'for (\S+) from') { $Matches[1] } else { '?' }
  [pscustomobject]@{ T=$e.TimeCreated; Bin=$e.TimeCreated.ToString('HH:') + ('{0:00}' -f ([math]::Floor($e.TimeCreated.Minute/10)*10)); IP=$ip; U=$u }
}
"TOTAL_ACCEPTED: " + ($rows | Measure-Object).Count
$rows | Group-Object IP,U,Bin | Sort-Object { ($_.Group | Select-Object -First 1).T } | ForEach-Object { $g=$_.Group; "{0} {1} {2} n={3} first={4} last={5}" -f $g[0].Bin,$g[0].IP,$g[0].U,$g.Count,($g | Sort-Object T | Select-Object -First 1).T.ToString('HH:mm:ss'),($g | Sort-Object T | Select-Object -Last 1).T.ToString('HH:mm:ss') }
