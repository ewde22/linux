#!/usr/bin/env bash

#function for checking diskspace
check_space() { 
	percent=$(df -h | grep '/$' | awk '{print $5}' | cut -d'%' -f1)

	if [ "$percent" -lt 80 ]; then
		echo "<span style='color: green; font-weight: bold;'>OK ($percent%)</span>"
	else 
		echo "<span style='color: pink; font-weight: bold;'>WARNING ($percent%)</span>"
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
		body { font-family: 'Courier New', Courier, monospace; background-color: #ffd1dc; color: #800020; padding: 40px; text-align: center; }
        	.container { background: #fff0f5; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(128,0,32,0.1); display: inline-block; text-align: left; max-width: 600px; }
        	 h1 { text-align: center; font-size: 22px; }
        	.info { margin: 15px 0; font-size: 15px; border-bottom: 1px dashed #800020; padding-bottom: 5px; }
        	.footer { text-align: center; font-size: 12px; margin-top: 25px; color: #a04060; }
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



