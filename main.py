import sys
import liveapi
import time
import RPi.GPIO as GPIO

from flask import Flask

sys.path.append('/home/pi/config')
import config as cf

# Time measurement class
class TimeMeasure():
	start_time = 0
	end_time = 0
	def __init__(self):
		self.start_time = time.time()
		self.end_time = time.time()
		
	def start_measure(self):
		self.start_time = time.time()

	def end_measure(self):
		self.end_time = time.time() - self.start_time
		print("Reaction time: " + str(self.end_time))

time_measure = TimeMeasure()

# GPI to Stream class with more information
class GpiStream:
	stream_id = '0'
	in_cue = False
	
	def __init__(self, id):
		self.stream_id = id
	def __str__(self):
		return "GPI: {} str_id: {} in_cue: {}".format(self.gpi_input, self.stream_id, self.in_cue)

# Configure the web app (needed only for autorestar)
app = Flask(__name__)
app.config.from_object(cf.FlaskConfig)

# Make a new dict with GPIs as Keys and GpiStreams as values
gpi_stream_dict = {}
for gpi, id in cf.gpi2stream.items():
	gpi_stream_dict[gpi] = GpiStream(id)


# Setup GPIO inputs/outputs
	#Use Board pin numbering - etc. (12) in pinout command
GPIO.setmode(GPIO.BCM)
	#Setup GPIOs as inputs with PULL-UP
for GPI in list(cf.gpi2stream):
	GPIO.setup( GPI, GPIO.IN, pull_up_down=GPIO.PUD_UP )


# Define callbacks

# Start cue on Falling edge and Stop Cue on Rising edge
def start_stop_avail(gpi):
	edge = GPIO.input(gpi)
	print("1. {} Event detcted".format(edge))
	print("2. Stream is in cue: {}".format(gpi_stream_dict[gpi].in_cue))
	
	# Rising edge detected and Stream is in Cue => Stop cue
	if edge and gpi_stream_dict[gpi].in_cue:	
		print("3. Stopping cue")
		time_measure.start_measure()
		resp = liveapi.cue_command(cf.elemental_ip, cf.gpi2stream[gpi], 'stop_cue') # Stop cue
		time_measure.end_measure()
		#print(resp)
		gpi_stream_dict[gpi].in_cue = False 		# Stream is no longer in cue
		time.sleep(cf.wait_time)					# Sleeps the thread for all GPIO inputs - not good
		
	# Falling edge detected and Stream is NOT in Cue => Start cue
	elif not edge and not gpi_stream_dict[gpi].in_cue:	
		print("3. Starting cue")
		time_measure.start_measure()
		resp = liveapi.cue_command(cf.elemental_ip, cf.gpi2stream[gpi], 'start_cue') # Start cue			
		time_measure.end_measure()
		#print(resp)
		gpi_stream_dict[gpi].in_cue = True			# Stream is now in cue
		time.sleep(cf.wait_time)					# Sleeps the thread for all GPIO inputs - not good
		

# Tie callbacks to events
for GPI in list(cf.gpi2stream):
	#GPIO.add_event_detect( GPI, GPIO.BOTH, callback = start_stop_avail, bouncetime = cf.wait_time*1000)
	GPIO.add_event_detect( GPI, GPIO.BOTH, callback = start_stop_avail, bouncetime = 200)

@app.route('/')
def index():
	return "Working"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')		
