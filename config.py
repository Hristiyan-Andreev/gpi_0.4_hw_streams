

# Configuration parameters - IPs, Inputs, Stream IDs
	#Define GPI_1 as PIN 40 (GPIO 21)
#GPI_1 = 40 							# GPIO 21
#GPIs = [21, 13, 26]

	#elemental_ip = '37.157.142.3'
elemental_ip = '192.168.2.3'

	#Mapper of GPI inputs to Elemental live streams
gpi2stream = {
		21: '5',
		13: '6',
}

	#Time to wait after edge detection
wait_time = 5