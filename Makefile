all:
	# sakura -x "sudo tcpdump -i eth0"&
	wireshark -R "eth.type == 0xb00b" -f "ether proto 0xb00b" -X lua_script:../tools/wireshark/dissector.lua -i eth0 &	
	sudo ./debug_client.py
	less log

test:
	sudo ./debug_client_test_server.py

config:
	cd config && ./debug_config.py debug_client.config

clean:
	@echo rm
	@find . | grep pyc$
	@find . | grep pyc$ | xargs rm -f


.PHONY: config clean
