all:
	sudo ./debug_client.py

test:
	sudo ./debug_client_test_server.py

config:
	cd config && ./debug_config.py debug_client.config

clean:
	@echo rm
	@find . | grep pyc$
	@find . | grep pyc$ | xargs rm -f


.PHONY: config clean
