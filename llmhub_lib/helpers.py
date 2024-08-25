# llmhub_lib/helpers.py

def update_processes(service_manager):
    service_manager.update_services()

def start_specific_process(service_manager, model_name, quant, engine=None, context_size=4096, port=8081):
    service_manager.start_service(model_name, quant, context_size, port)

def stop_all_processes(service_manager):
    service_manager.stop_all_services()

def stop_specific_process(service_manager, model_name):
    service_manager.stop_service(model_name)

def start_proxy_process(service_manager):
    # Logic to start the proxy process
    config = service_manager.config_manager.get_merged_config()
    if config.get('enable_proxy', False):
        web_port = config.get('port', 5000)
        proxy_process_name = f"proxy-{web_port}"
        running_processes = service_manager.state_manager.list_states()

        if proxy_process_name not in running_processes:
            # Assumes web_server.py is being run as the proxy process
            script_path = "/path/to/web_server.py"  # Adjust the path as necessary
            proxy_cmd = [sys.executable, str(script_path)]
            service_manager.process_manager.start_process(proxy_cmd, proxy_process_name, web_port)
        else:
            print(f"Proxy process {proxy_process_name} is already running.")
    else:
        print("Proxy is disabled in the configuration.")

def stop_proxy_process(service_manager):
    # Logic to stop the proxy process
    config = service_manager.config_manager.get_merged_config()
    if config.get('enable_proxy', False):
        web_port = config.get('port', 5000)
        proxy_process_name = f"proxy-{web_port}"
        running_processes = service_manager.state_manager.list_states()
        if proxy_process_name in running_processes:
            service_manager.process_manager.stop_process(proxy_process_name)
        else:
            print(f"Proxy process {proxy_process_name} is not running.")
    else:
        print("Proxy is disabled in the configuration.")