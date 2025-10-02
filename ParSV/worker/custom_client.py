from hepai import HepAI, RemoteModel

model: RemoteModel = HepAI(
    # base_url="http://localhost:42600/apiv2",
    # base_url="http://localhost:42601/apiv2",
    base_url="https://aiapi.ihep.ac.cn/apiv2",  # if you want to connect to a remote worker behind a controller, set the controller address here.
    ).connect_to(
        "hepai/particle-spelling-variants", 
        # version="2.0",
        # owner=None,
        # worker_id=None,
        )

# Call the `custom_method` of the remote model.
# output = model.custom_method(a=1, b=2)
# print(f"output: {output}")

# # # call the `get_stream` of the remote model.
# stream = model.get_stream(stream=True)  # Note: You should set `stream=True` additionally.
# print(f"Output of get_stream:")
# for x in stream:
#     print(f"{x}, type: {type(x)}", flush=True)
    
particle_info = model.particle_name_to_properties("pi+")
print(f"particle_info: {particle_info}")
    
