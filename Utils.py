import rabbitpy
url = 'amqp://guest:guest@localhost:5672/%2F'



def get_conn():
    connection=rabbitpy.Connection(url)
    return connection;

def get_channel():
    channel=get_conn().channel()
    return channel

#Iterates through the exchange names to be created
for exchange_name in ['rpc-replies', 'direct-rpc-requests']:
    exchange=rabbitpy.Exchange(get_channel(),exchange_name,exchange_type="direct")

    exchange.declare()

