#!/usr/bin/env bash

#function for checking diskspace
check_space() { 
	percent=$(df -h | grep '/$' | awk '{print $5}' | cut -d'%' -f1)
	
	if [ "$percent" -lt 80 ]; then
		echo "<span style='color: green; font-weight: bold;'>OK ($percent%)</span>"
	else 
		echo "<span style='color: red; font-weight: bold;'>WARNING ($percent%)</span>"
	fi

}

Date=$(date)
Uptime=$(uptime | cut -d',' -f1)
Free_memory=$(free -h | grep Mem: | awk '{print $4}')
Memory_total=$(free -h | grep Mem: | awk '{print $2}')
Disc_status=$(check_space)

#HTML report
cat << EOF > /var/www/html/viikko3/index.html
<!DOCTYPE html>
<html lang="fi">
<head>
	<meta charset="utf-8">
	<title>Palvelinraportti - Viikko 3</title>
	<style>
		body { font-family: 'Cascadia Code', Courier New, Courier, monospace; 
			background-color: #fff9c4; 
			color: #3d220a; 
			padding: 40px; 
			text-align: center;
			font-size: 18px; }

        	.container { background: #fffde4; 
			padding: 45px; 
			border-radius: 16px; 
			box-shadow: 0 6px 20px rgba(128,0,32,0.1); 
			display: inline-block; 
			text-align: left; 
			max-width: 800px;
			box-sizing: border-box; }

        	 h1 { text-align: center; 
			font-size: 32px;
			color: #1e1105;
			margin-top: 0;
			margin-bottom: 30px; }

        	.info { margin: 25px 0; 
			font-size: 20px; 
			border-bottom: 2px dashed #800020; 
			padding-bottom: 10px; }

        	.footer { text-align: center; 
			font-size: 15px; 
			margin-top: 40px; 
			color: #3d220a; }
    	</style>
</head>

<body>
	<div class="container">
		<h1>Palvelimen tilaraportti</h1>
		<div class="info"><strong>Generointiaika:</strong> $Date</div>
		<div class="info"><strong>Päälläoloaika:</strong> $Uptime</div>
		<div class="info"><strong>Vapaa / yhteensä RAM:</strong> $Free_memory / $Memory_total</div>
		<div class="info"><strong>Levytilan status:</strong> $Disc_status</div>
		<div class="footer">Tämä raportti päivittyy kerran minuutissa automaattisesti.</div>
	</div>
</body>
</html>
EOF



