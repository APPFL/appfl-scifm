import argparse
from omegaconf import OmegaConf
from appfl.agent import ClientAgent
from appfl.communicator.grpc import GRPCClientCommunicator

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "--config", 
    type=str, 
    default="./client_1.yaml",
    help="Path to the configuration file."
)
args = argparser.parse_args()

client_agent_config = OmegaConf.load(args.config)

client_agent = ClientAgent(client_agent_config=client_agent_config)
client_communicator = GRPCClientCommunicator(
    client_id = client_agent.get_id(),
    **client_agent_config.comm_configs.grpc_configs,
)

client_config = client_communicator.get_configuration()
client_agent.load_config(client_config)

init_global_model = client_communicator.get_global_model(init_model=True)
client_agent.load_parameters(init_global_model)

# Send the number of local data to the server
sample_size = client_agent.get_sample_size()
client_communicator.invoke_custom_action(action='set_sample_size', sample_size=sample_size)

while True:
    client_agent.train()
    local_model = client_agent.get_parameters()
    new_global_model, metadata = client_communicator.update_global_model(local_model)
    if metadata['status'] == 'DONE':
        break
    client_agent.load_parameters(new_global_model)
client_communicator.invoke_custom_action(action='close_connection')